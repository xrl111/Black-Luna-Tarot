#  Tarot System - Kafka Event Producer
"""
Kafka producer for emitting tarot reading events to the Big Data pipeline.
- Singleton pattern via module-level instance
- Graceful degradation: if Kafka is down, readings still save to MongoDB
- Feature flag: KAFKA_ENABLED controls whether events are emitted
- Dead Letter Queue: failed events saved to MongoDB for replay
- Metrics: tracking latency, success rate, error history
- Idempotent producer: exactly-once semantics
"""

import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from collections import deque

import structlog
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.core.config import settings

logger = structlog.get_logger()

# Module-level singleton
_producer: Optional["TarotKafkaProducer"] = None


class TarotKafkaProducer:
    """
    Async Kafka producer for tarot reading events.
    Lifecycle managed by FastAPI lifespan (start/stop).
    """

    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
        self._is_running = False
        # ── Metrics ──
        self._metrics = {
            "events_sent": 0,
            "events_failed": 0,
            "total_latency_ms": 0.0,
            "last_event_at": None,
            "dlq_count": 0,
            "started_at": None,
            "errors": deque(maxlen=10),  # Last 10 errors
        }

    async def start(self):
        """Initialize and start the Kafka producer"""
        if not settings.KAFKA_ENABLED:
            logger.info("Kafka producer disabled (KAFKA_ENABLED=False)")
            return

        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                request_timeout_ms=settings.KAFKA_PRODUCER_TIMEOUT * 1000,
                acks="all",  # Đảm bảo message được ghi vào tất cả replica
                enable_idempotence=True,  # Exactly-once producer semantics
            )
            await self._producer.start()
            self._is_running = True
            self._metrics["started_at"] = datetime.now(timezone.utc).isoformat()
            logger.info(
                " Kafka producer started",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                topic=settings.KAFKA_TOPIC_READINGS,
                idempotence=True,
            )
        except Exception as e:
            logger.error(" Failed to start Kafka producer", error=str(e))
            self._is_running = False

    async def stop(self):
        """Gracefully stop the Kafka producer"""
        if self._producer and self._is_running:
            try:
                await self._producer.stop()
                self._is_running = False
                logger.info("Kafka producer stopped gracefully")
            except Exception as e:
                logger.error("Error stopping Kafka producer", error=str(e))

    # ── Metrics ──────────────────────────────────────────────────────────────

    def get_metrics(self) -> dict:
        """Return producer metrics for monitoring"""
        total = self._metrics["events_sent"] + self._metrics["events_failed"]
        avg_latency = (
            self._metrics["total_latency_ms"] / max(1, self._metrics["events_sent"])
        )
        return {
            "is_running": self._is_running,
            "events_sent": self._metrics["events_sent"],
            "events_failed": self._metrics["events_failed"],
            "dlq_count": self._metrics["dlq_count"],
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate": round(
                self._metrics["events_sent"] / max(1, total) * 100, 2
            ),
            "last_event_at": self._metrics["last_event_at"],
            "started_at": self._metrics["started_at"],
            "recent_errors": list(self._metrics["errors"]),
            "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "topic": settings.KAFKA_TOPIC_READINGS,
        }

    # ── Dead Letter Queue ────────────────────────────────────────────────────

    async def _save_to_dead_letter(self, payload: dict, error: str):
        """Save failed event to MongoDB dead letter collection for replay"""
        try:
            from app.core.database import database
            if database is not None:
                await database["kafka_dead_letters"].insert_one({
                    "payload": payload,
                    "error": error,
                    "topic": settings.KAFKA_TOPIC_READINGS,
                    "created_at": datetime.now(timezone.utc),
                    "retried": False,
                    "retry_count": 0,
                })
                self._metrics["dlq_count"] += 1
                logger.info(" Event saved to Dead Letter Queue", event_id=payload.get("event_id"))
        except Exception as dlq_err:
            logger.error(" Failed to save to DLQ", error=str(dlq_err))

    # ── Generic Event Emission ───────────────────────────────────────────────

    async def emit_event(self, event_type: str, payload: dict, key: str = "unknown") -> bool:
        """
        Generic event emission to Kafka.
        Supports future event types: reading.generated, reading.rated, session.started, etc.
        
        Args:
            event_type: Event type string (e.g., "reading.created")
            payload: Event data dict
            key: Partition key (typically session_id)
            
        Returns:
            True if event was sent successfully, False otherwise
        """
        if not settings.KAFKA_ENABLED or not self._is_running:
            return False

        try:
            start_time = time.time()

            await self._producer.send_and_wait(
                topic=settings.KAFKA_TOPIC_READINGS,
                key=key,
                value=payload,
            )

            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            self._metrics["events_sent"] += 1
            self._metrics["total_latency_ms"] += elapsed_ms
            self._metrics["last_event_at"] = datetime.now(timezone.utc).isoformat()

            logger.info(
                " Kafka event emitted",
                event_id=payload.get("event_id"),
                event_type=event_type,
                topic=settings.KAFKA_TOPIC_READINGS,
                key=key,
                latency_ms=elapsed_ms,
            )
            return True

        except (KafkaError, Exception) as e:
            self._metrics["events_failed"] += 1
            self._metrics["errors"].append({
                "error": str(e),
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            logger.warning(" Kafka send failed (non-blocking)", error=str(e), event_type=event_type)
            # Save to Dead Letter Queue
            await self._save_to_dead_letter(payload, str(e))
            return False

    # ── Reading Event ────────────────────────────────────────────────────────

    async def emit_reading_event(self, reading) -> bool:
        """
        Emit a reading event to Kafka topic 'tarot-events'.
        
        Args:
            reading: Reading object (from MongoDB insert)
            
        Returns:
            True if event was sent successfully, False otherwise
        """
        if not settings.KAFKA_ENABLED or not self._is_running:
            return False

        # Build the event payload
        payload = self._build_event_payload(reading)

        # Send to Kafka with session_id as partition key
        # (ensures same session always goes to same partition → ordering)
        session_id = str(reading.session_id) if hasattr(reading, "session_id") else "unknown"

        return await self.emit_event("reading.created", payload, key=session_id)

    def _build_event_payload(self, reading) -> Dict[str, Any]:
        """
        Build the JSON event payload matching the schema designed in Task 2.1.
        Denormalized and optimized for Spark consumption.
        """
        reading_id = str(reading.id) if hasattr(reading, "id") else "unknown"
        now = datetime.now(timezone.utc).isoformat()

        # --- Question analysis (reuse logic from TrainingDataService) ---
        question_analysis = self._analyze_question(
            reading.question if hasattr(reading, "question") else ""
        )

        # --- Build cards array (denormalized) ---
        cards = []
        if hasattr(reading, "cards_drawn") and reading.cards_drawn:
            for card in reading.cards_drawn:
                cards.append({
                    "card_id": str(card.card_id) if hasattr(card, "card_id") else "",
                    "card_name": card.card_name if hasattr(card, "card_name") else "",
                    "card_name_vi": card.card_name_vi if hasattr(card, "card_name_vi") else "",
                    "suit": card.suit if hasattr(card, "suit") else "",
                    "arcana": card.card_type if hasattr(card, "card_type") else "",
                    "number": card.number if hasattr(card, "number") else "",
                    "position": card.position if hasattr(card, "position") else 0,
                    "orientation": card.orientation if hasattr(card, "orientation") else "upright",
                    "position_meaning": card.position_meaning if hasattr(card, "position_meaning") else "",
                    "element": card.element if hasattr(card, "element") else None,
                    "zodiac": card.zodiac if hasattr(card, "zodiac") else None,
                    "planet": card.planet if hasattr(card, "planet") else None,
                })

        # --- Construct the full event ---
        payload = {
            "event_id": f"evt_{reading_id}",
            "event_type": "reading.created",
            "event_timestamp": now,
            "version": "1.0",

            "reading": {
                "reading_id": reading_id,
                "session_id": reading.session_id if hasattr(reading, "session_id") else "",
                "user_id": reading.user_id if hasattr(reading, "user_id") else None,
                "question": reading.question if hasattr(reading, "question") else "",
                "reading_type": reading.reading_type if hasattr(reading, "reading_type") else "",
                "reading_spread": reading.reading_spread if hasattr(reading, "reading_spread") else "",
                "ai_model_used": reading.ai_model_used if hasattr(reading, "ai_model_used") else "",
                "tokens_used": reading.tokens_used if hasattr(reading, "tokens_used") else 0,
                "processing_time_sec": reading.processing_time if hasattr(reading, "processing_time") else 0.0,
                "ai_response_length": len(reading.ai_response) if hasattr(reading, "ai_response") else 0,
                # Truncate AI response to 2000 chars for Kafka (full text in MongoDB)
                "ai_response_truncated": (reading.ai_response[:2000] if hasattr(reading, "ai_response") and reading.ai_response else ""),
                "created_at": reading.created_at.isoformat() if hasattr(reading, "created_at") and reading.created_at else now,
            },

            "question_analysis": question_analysis,
            "cards": cards,

            "metadata": {
                "app_version": settings.VERSION,
                "source": "backend-api",
                "environment": settings.ENVIRONMENT,
            },
        }

        return payload

    def _analyze_question(self, question: str) -> Dict[str, Any]:
        """
        Analyze question for category, complexity, emotion.
        Reuses logic from TrainingDataService._analyze_question()
        """
        question_lower = question.lower()

        # Determine category
        categories = {
            "career": ["việc", "công việc", "sự nghiệp", "thăng tiến", "chuyển việc", "nghề"],
            "love": ["tình yêu", "tình cảm", "mối quan hệ", "hôn nhân", "người yêu", "crush"],
            "health": ["sức khỏe", "bệnh", "thể chất", "tinh thần", "healing"],
            "finance": ["tiền bạc", "tài chính", "đầu tư", "kinh doanh", "tiết kiệm"],
            "spiritual": ["linh hồn", "tâm linh", "mục đích", "định mệnh", "thiền"],
        }
        category = "general"
        for cat, keywords in categories.items():
            if any(kw in question_lower for kw in keywords):
                category = cat
                break

        # Determine complexity
        word_count = len(question.split())
        if word_count < 5:
            complexity = "simple"
        elif word_count > 15:
            complexity = "complex"
        else:
            complexity = "medium"

        # Determine emotion
        emotions = {
            "uncertain": ["có nên", "có thể", "không biết", "lo lắng", "phân vân"],
            "anxious": ["lo", "sợ", "hoảng", "stress", "áp lực"],
            "hopeful": ["hy vọng", "mong muốn", "ước mơ", "tương lai", "mong"],
            "confused": ["bối rối", "không hiểu", "mâu thuẫn", "lẫn lộn"],
        }
        emotion = "neutral"
        for emo, keywords in emotions.items():
            if any(kw in question_lower for kw in keywords):
                emotion = emo
                break

        # Determine urgency
        urgency_keywords = ["gấp", "ngay", "khẩn", "nhanh", "tuần này", "hôm nay"]
        urgency = "high" if any(kw in question_lower for kw in urgency_keywords) else "medium"

        return {
            "category": category,
            "complexity": complexity,
            "emotion": emotion,
            "urgency": urgency,
            "word_count": word_count,
        }


def get_kafka_producer() -> TarotKafkaProducer:
    """Get the singleton Kafka producer instance"""
    global _producer
    if _producer is None:
        _producer = TarotKafkaProducer()
    return _producer
