#!/usr/bin/env python3
# ============================================================================
# 🎯 Black Luna Tarot — Dead Letter Queue Replay Script
# ============================================================================
# Replay failed Kafka events from MongoDB DLQ back to Kafka.
#
# Cách chạy:
#   python scripts/replay_dead_letters.py
#   python scripts/replay_dead_letters.py --limit 5 --dry-run
#
# Yêu cầu:
#   - MongoDB đang chạy
#   - Kafka đang chạy (nếu không dry-run)
#   - pip install pymongo aiokafka
# ============================================================================

import asyncio
import argparse
import json
import sys
from datetime import datetime, timezone

try:
    from pymongo import MongoClient
except ImportError:
    print("❌ Missing dependency: pip install pymongo")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Replay Dead Letter Queue events")
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017",
                        help="MongoDB URI (default: mongodb://localhost:27017)")
    parser.add_argument("--db-name", default="tarot_system",
                        help="Database name (default: tarot_system)")
    parser.add_argument("--kafka-bootstrap", default="localhost:9094",
                        help="Kafka bootstrap servers (default: localhost:9094)")
    parser.add_argument("--kafka-topic", default="tarot-events",
                        help="Kafka topic (default: tarot-events)")
    parser.add_argument("--limit", type=int, default=10,
                        help="Max events to replay (default: 10)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show events without sending to Kafka")
    return parser.parse_args()


async def replay_events(args):
    """Replay DLQ events to Kafka"""
    print("=" * 60)
    print("🎯 Dead Letter Queue Replay")
    print(f"   MongoDB: {args.mongo_uri}/{args.db_name}")
    print(f"   Kafka:   {args.kafka_bootstrap} → {args.kafka_topic}")
    print(f"   Limit:   {args.limit}")
    print(f"   Dry Run: {args.dry_run}")
    print("=" * 60)

    # Connect to MongoDB
    client = MongoClient(args.mongo_uri)
    db = client[args.db_name]
    dlq_col = db["kafka_dead_letters"]

    # Find pending events
    pending = list(dlq_col.find({"retried": False}).sort("created_at", 1).limit(args.limit))

    if not pending:
        print("\n✅ No pending events in Dead Letter Queue!")
        client.close()
        return

    print(f"\n📋 Found {len(pending)} pending events:\n")

    for i, event in enumerate(pending, 1):
        payload = event.get("payload", {})
        event_id = payload.get("event_id", "?")
        event_type = payload.get("event_type", "?")
        created = event.get("created_at", "?")
        error = event.get("error", "?")
        retry_count = event.get("retry_count", 0)

        print(f"  {i}. event_id={event_id}, type={event_type}")
        print(f"     error: {error[:80]}")
        print(f"     created: {created}, retries: {retry_count}")
        print()

    if args.dry_run:
        print("🔍 Dry-run mode — no events sent to Kafka.")
        client.close()
        return

    # Send to Kafka
    try:
        from aiokafka import AIOKafkaProducer

        producer = AIOKafkaProducer(
            bootstrap_servers=args.kafka_bootstrap,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await producer.start()

        replayed = 0
        failed = 0

        for event in pending:
            payload = event.get("payload", {})
            key = payload.get("reading", {}).get("session_id", "unknown")

            try:
                await producer.send_and_wait(
                    topic=args.kafka_topic,
                    key=key,
                    value=payload,
                )

                # Mark as replayed in MongoDB
                dlq_col.update_one(
                    {"_id": event["_id"]},
                    {
                        "$set": {
                            "retried": True,
                            "retried_at": datetime.now(timezone.utc),
                        },
                        "$inc": {"retry_count": 1},
                    }
                )
                replayed += 1
                print(f"  ✅ Replayed: {payload.get('event_id', '?')}")

            except Exception as e:
                failed += 1
                dlq_col.update_one(
                    {"_id": event["_id"]},
                    {"$inc": {"retry_count": 1}}
                )
                print(f"  ❌ Failed: {payload.get('event_id', '?')} — {e}")

        await producer.stop()

        print(f"\n📊 Results: {replayed} replayed, {failed} failed")

    except ImportError:
        print("❌ aiokafka not installed. Run: pip install aiokafka")
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")

    client.close()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(replay_events(args))
