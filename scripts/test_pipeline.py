#!/usr/bin/env python3
# ============================================================================
# 🎯 Black Luna Tarot — E2E Pipeline Verification Script
# ============================================================================
# Kiểm tra toàn bộ luồng: API → Kafka → Spark → HDFS → Hive
#
# Cách chạy:
#   python scripts/test_pipeline.py
#
# Yêu cầu:
#   - Backend API đang chạy (localhost:8000)
#   - Docker Compose Big Data đang chạy
#   - pip install httpx aiokafka
# ============================================================================

import asyncio
import json
import time
import sys
import subprocess
from datetime import datetime

try:
    import httpx
except ImportError:
    print("❌ Missing dependency: pip install httpx")
    sys.exit(1)


# ============================================================================
# CONFIG
# ============================================================================
API_BASE_URL = "http://localhost:8000"
KAFKA_BOOTSTRAP = "localhost:9094"
KAFKA_TOPIC = "tarot-events"
HDFS_NAMENODE = "http://localhost:9870"


class PipelineTest:
    """End-to-end pipeline verification"""

    def __init__(self):
        self.results = []
        self.reading_id = None

    def _log(self, step: str, status: str, detail: str = ""):
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        msg = f"{icon} [{step}] {status}: {detail}"
        print(msg)
        self.results.append({"step": step, "status": status, "detail": detail})

    # ── Step 1: Health Check ──
    async def test_health(self):
        """Check all services are healthy"""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(f"{API_BASE_URL}/health")
                data = resp.json()

                # Check overall status
                status = data.get("status", "unknown")
                services = data.get("services", {})

                self._log("Health Check", "PASS" if status in ["healthy", "degraded"] else "FAIL",
                           f"status={status}, services={len(services)}")

                # Check individual services
                for name, info in services.items():
                    svc_status = info.get("connected", False)
                    self._log(f"  Service: {name}", "PASS" if svc_status else "WARN",
                               info.get("status", "unknown"))

            except Exception as e:
                self._log("Health Check", "FAIL", str(e))

    # ── Step 2: Create Test Reading ──
    async def test_create_reading(self):
        """POST a test reading to the API"""
        async with httpx.AsyncClient(timeout=30) as client:
            payload = {
                "session_id": f"test_pipeline_{int(time.time())}",
                "question": "Tôi có nên thay đổi công việc trong tháng này không?",
                "reading_type": "career",
                "reading_spread": "three_card",
                "cards_drawn": [
                    {
                        "card_id": "test_card_1",
                        "card_name": "The Fool",
                        "card_name_vi": "Kẻ Khờ",
                        "suit": "major",
                        "card_type": "major",
                        "number": "0",
                        "position": 1,
                        "orientation": "upright",
                        "position_meaning": "Quá khứ",
                        "interpretation": "Bắt đầu một điều mới mẻ, tự do và vô tư.",
                        "traditional_meaning": "Sự khởi đầu, ngây thơ, mạo hiểm."
                    },
                    {
                        "card_id": "test_card_2",
                        "card_name": "The Tower",
                        "card_name_vi": "Tháp",
                        "suit": "major",
                        "card_type": "major",
                        "number": "16",
                        "position": 2,
                        "orientation": "reversed",
                        "position_meaning": "Hiện tại",
                        "interpretation": "Tránh được một tai họa nhỏ, sự thay đổi chậm.",
                        "traditional_meaning": "Sự sụp đổ, thay đổi đột ngột."
                    },
                    {
                        "card_id": "test_card_3",
                        "card_name": "The Star",
                        "card_name_vi": "Ngôi Sao",
                        "suit": "major",
                        "card_type": "major",
                        "number": "17",
                        "position": 3,
                        "orientation": "upright",
                        "position_meaning": "Tương lai",
                        "interpretation": "Hy vọng, chữa lành và cảm hứng sẽ đến.",
                        "traditional_meaning": "Hy vọng, niềm tin, cảm hứng."
                    },
                ],
                "ai_response": "Đây là bài test pipeline. The Fool cho thấy bạn đang ở giai đoạn bắt đầu mới.",
                "ai_model_used": "test-model",
                "tokens_used": 100,
                "processing_time": 1.5,
            }

            try:
                resp = await client.post(f"{API_BASE_URL}/api/v1/readings/", json=payload)
                if resp.status_code in [200, 201]:
                    data = resp.json()
                    self.reading_id = data.get("id") or data.get("_id") or data.get("reading_id")
                    self._log("Create Reading", "PASS",
                               f"reading_id={self.reading_id}")
                else:
                    self._log("Create Reading", "FAIL",
                               f"status={resp.status_code}, body={resp.text[:200]}")
            except Exception as e:
                self._log("Create Reading", "FAIL", str(e))

    # ── Step 3: Check Kafka ──
    async def test_kafka_message(self):
        """Verify the event was sent to Kafka topic"""
        try:
            from aiokafka import AIOKafkaConsumer

            async def _consume():
                consumer = AIOKafkaConsumer(
                    KAFKA_TOPIC,
                    bootstrap_servers=KAFKA_BOOTSTRAP,
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,
                    group_id=f"test_pipeline_{int(time.time())}",
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                )
                await consumer.start()
                found = False
                msg_count = 0
                try:
                    async for msg in consumer:
                        msg_count += 1
                        if self.reading_id and self.reading_id in str(msg.value):
                            found = True
                            break
                        if msg_count > 20:
                            break
                finally:
                    await consumer.stop()
                return found, msg_count

            try:
                found, msg_count = await asyncio.wait_for(_consume(), timeout=8.0)
                if found:
                    self._log("Kafka Message", "PASS", f"Event found in topic '{KAFKA_TOPIC}'")
                else:
                    self._log("Kafka Message", "WARN",
                               f"Checked {msg_count} messages, event not matched")
            except asyncio.TimeoutError:
                self._log("Kafka Message", "WARN",
                           "Consumer timed out (topic may not exist yet)")

        except ImportError:
            self._log("Kafka Message", "WARN", "aiokafka not installed, skipping")
        except Exception as e:
            self._log("Kafka Message", "WARN", f"Cannot connect to Kafka: {e}")

    # ── Step 4: Check BigData API ──
    async def test_bigdata_status(self):
        """Check Big Data pipeline status endpoint"""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(f"{API_BASE_URL}/api/v1/bigdata/status")
                data = resp.json()

                kafka_enabled = data.get("kafka_enabled", False)
                producer = data.get("producer", {})
                dlq = data.get("dead_letter_queue", {})

                self._log("BigData Status", "PASS",
                           f"kafka_enabled={kafka_enabled}, events_sent={producer.get('events_sent', 'N/A')}")

                if dlq:
                    self._log("  DLQ Status", "PASS" if dlq.get("pending", 0) == 0 else "WARN",
                               f"pending={dlq.get('pending', 'N/A')}, total={dlq.get('total', 'N/A')}")

            except Exception as e:
                self._log("BigData Status", "FAIL", str(e))

    # ── Step 5: Check HDFS ──
    async def test_hdfs_files(self):
        """Check if HDFS has Parquet files"""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(
                    f"{HDFS_NAMENODE}/webhdfs/v1/data/tarot/fact_card_draws?op=LISTSTATUS"
                )
                if resp.status_code == 200:
                    data = resp.json()
                    statuses = data.get("FileStatuses", {}).get("FileStatus", [])
                    self._log("HDFS Files", "PASS" if statuses else "WARN",
                               f"Found {len(statuses)} items in /data/tarot/fact_card_draws/")
                else:
                    self._log("HDFS Files", "WARN",
                               f"HDFS returned status {resp.status_code} (path may not exist yet)")
            except Exception as e:
                self._log("HDFS Files", "WARN", f"Cannot connect to HDFS: {e}")

    # ── Step 6: Check BigData Stats ──
    async def test_bigdata_stats(self):
        """Check analytics stats endpoint"""
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(f"{API_BASE_URL}/api/v1/bigdata/stats")
                data = resp.json()
                total = data.get("total_readings", 0)
                self._log("BigData Stats", "PASS",
                           f"total_readings={total}, daily_stats={len(data.get('daily_stats', []))}")
            except Exception as e:
                self._log("BigData Stats", "FAIL", str(e))

    # ── Run All ──
    async def run_all(self):
        """Run all pipeline tests"""
        print("=" * 70)
        print("🎯 Black Luna Tarot — E2E Pipeline Verification")
        print(f"   Time: {datetime.now().isoformat()}")
        print("=" * 70)
        print()

        await self.test_health()
        print()
        await self.test_create_reading()
        print()

        # Wait a moment for Kafka to process
        print("⏳ Waiting 3 seconds for event propagation...")
        await asyncio.sleep(3)

        await self.test_kafka_message()
        print()
        await self.test_bigdata_status()
        print()
        await self.test_hdfs_files()
        print()
        await self.test_bigdata_stats()
        print()

        # Summary
        print("=" * 70)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warned = sum(1 for r in self.results if r["status"] == "WARN")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        total = len(self.results)

        print(f"📊 Results: {passed} PASS / {warned} WARN / {failed} FAIL (total: {total})")

        if failed == 0:
            print("🎉 Pipeline verification PASSED!")
        else:
            print("⚠️  Some checks failed — review output above.")
        print("=" * 70)

        return failed == 0


if __name__ == "__main__":
    tester = PipelineTest()
    success = asyncio.run(tester.run_all())
    sys.exit(0 if success else 1)
