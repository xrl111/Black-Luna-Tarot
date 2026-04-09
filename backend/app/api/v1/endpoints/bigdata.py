# 🎯 Black Luna Tarot — Big Data API Endpoints
"""
API endpoints for Big Data pipeline monitoring, stats, and DLQ management.
Endpoints:
  GET  /bigdata/status       → Kafka producer metrics + pipeline status
  GET  /bigdata/stats        → Basic analytics stats from MongoDB
  GET  /bigdata/dead-letters → List failed events from DLQ
  POST /bigdata/replay       → Replay events from DLQ
"""

from typing import Optional
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings

logger = structlog.get_logger()

router = APIRouter()


@router.get("/status", summary="Big Data Pipeline Status")
async def bigdata_status():
    """
    Returns Kafka producer metrics and overall pipeline health.
    Includes: events_sent, events_failed, avg_latency, success_rate.
    """
    result = {
        "kafka_enabled": settings.KAFKA_ENABLED,
        "kafka_bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "kafka_topic": settings.KAFKA_TOPIC_READINGS,
        "producer": None,
    }

    if settings.KAFKA_ENABLED:
        try:
            from app.services.kafka_producer import get_kafka_producer
            producer = get_kafka_producer()
            result["producer"] = producer.get_metrics()
        except Exception as e:
            result["producer"] = {"error": str(e)}

    # DLQ stats
    try:
        from app.core.database import database
        if database is not None:
            dlq_total = await database["kafka_dead_letters"].count_documents({})
            dlq_pending = await database["kafka_dead_letters"].count_documents({"retried": False})
            result["dead_letter_queue"] = {
                "total": dlq_total,
                "pending": dlq_pending,
                "replayed": dlq_total - dlq_pending,
            }
    except Exception as e:
        result["dead_letter_queue"] = {"error": str(e)}

    return result


@router.get("/stats", summary="Big Data Analytics Stats")
async def bigdata_stats():
    """
    Return analytics statistics queried from MongoDB.
    In production, this would query Hive/HDFS via Spark SQL.
    For now, aggregates from the readings collection.
    """
    try:
        from app.core.database import database
        if database is None:
            raise HTTPException(status_code=503, detail="Database not available")

        readings_col = database["readings"]

        # Total readings
        total_readings = await readings_col.count_documents({})

        # Aggregation pipeline for stats
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_readings": {"$sum": 1},
                    "avg_processing_time": {"$avg": "$processing_time"},
                    "avg_rating": {"$avg": "$user_rating"},
                    "total_tokens": {"$sum": "$tokens_used"},
                }
            }
        ]
        agg_result = await readings_col.aggregate(pipeline).to_list(1)

        # Reading type distribution
        type_pipeline = [
            {"$group": {"_id": "$reading_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        type_dist = await readings_col.aggregate(type_pipeline).to_list(10)

        # AI model usage
        model_pipeline = [
            {"$group": {"_id": "$ai_model_used", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        model_dist = await readings_col.aggregate(model_pipeline).to_list(10)

        # Readings per day (last 7 days)
        daily_pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": -1}},
            {"$limit": 7},
        ]
        daily_stats = await readings_col.aggregate(daily_pipeline).to_list(7)

        stats = agg_result[0] if agg_result else {}

        return {
            "total_readings": total_readings,
            "avg_processing_time_sec": round(stats.get("avg_processing_time", 0) or 0, 2),
            "avg_rating": round(stats.get("avg_rating", 0) or 0, 2),
            "total_tokens_used": stats.get("total_tokens", 0) or 0,
            "reading_type_distribution": [
                {"type": item["_id"], "count": item["count"]}
                for item in type_dist if item["_id"]
            ],
            "ai_model_usage": [
                {"model": item["_id"], "count": item["count"]}
                for item in model_dist if item["_id"]
            ],
            "daily_stats": [
                {"date": item["_id"], "count": item["count"]}
                for item in daily_stats if item["_id"]
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get bigdata stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Stats query failed: {str(e)}")


@router.get("/dead-letters", summary="List Dead Letter Queue Events")
async def list_dead_letters(
    limit: int = Query(default=20, ge=1, le=100),
    pending_only: bool = Query(default=True),
):
    """
    List failed Kafka events stored in the Dead Letter Queue.
    """
    try:
        from app.core.database import database
        if database is None:
            raise HTTPException(status_code=503, detail="Database not available")

        dlq_col = database["kafka_dead_letters"]

        query_filter = {"retried": False} if pending_only else {}

        cursor = dlq_col.find(
            query_filter,
            {
                "payload.reading.ai_response_truncated": 0,  # Exclude large fields
            }
        ).sort("created_at", -1).limit(limit)

        events = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            if "created_at" in doc and isinstance(doc["created_at"], datetime):
                doc["created_at"] = doc["created_at"].isoformat()
            events.append(doc)

        total = await dlq_col.count_documents(query_filter)

        return {
            "total": total,
            "limit": limit,
            "pending_only": pending_only,
            "events": events,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list dead letters", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay", summary="Replay Dead Letter Queue Events")
async def replay_dead_letters(
    limit: int = Query(default=10, ge=1, le=50),
):
    """
    Replay pending events from the Dead Letter Queue back to Kafka.
    """
    if not settings.KAFKA_ENABLED:
        raise HTTPException(status_code=400, detail="Kafka is not enabled")

    try:
        from app.core.database import database
        from app.services.kafka_producer import get_kafka_producer

        if database is None:
            raise HTTPException(status_code=503, detail="Database not available")

        producer = get_kafka_producer()
        if not producer._is_running:
            raise HTTPException(status_code=503, detail="Kafka producer is not running")

        dlq_col = database["kafka_dead_letters"]

        cursor = dlq_col.find({"retried": False}).sort("created_at", 1).limit(limit)

        replayed = 0
        failed = 0
        from bson import ObjectId

        async for doc in cursor:
            payload = doc.get("payload", {})
            event_type = payload.get("event_type", "unknown")
            key = payload.get("reading", {}).get("session_id", "unknown")

            success = await producer.emit_event(event_type, payload, key=key)

            if success:
                await dlq_col.update_one(
                    {"_id": doc["_id"]},
                    {
                        "$set": {
                            "retried": True,
                            "retried_at": datetime.now(timezone.utc),
                        },
                        "$inc": {"retry_count": 1},
                    }
                )
                replayed += 1
            else:
                await dlq_col.update_one(
                    {"_id": doc["_id"]},
                    {"$inc": {"retry_count": 1}}
                )
                failed += 1

        return {
            "replayed": replayed,
            "failed": failed,
            "total_attempted": replayed + failed,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to replay dead letters", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
