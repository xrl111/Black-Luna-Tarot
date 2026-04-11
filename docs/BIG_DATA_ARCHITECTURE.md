#  Big Data Architecture — Black Luna Tarot

> **Tài liệu kiến trúc Big Data Pipeline cho luận văn Thạc sĩ.**
> Phiên bản: 2.0 | Cập nhật: 2026-04-09

---

## 1. Tổng Quan Kiến Trúc

### 1.1 Mô Hình Lambda Architecture

Hệ thống Black Luna Tarot triển khai **Lambda Architecture** với hai tầng dữ liệu song song:

| Tầng | Vai trò | Công nghệ | Đặc điểm |
|------|---------|-----------|----------|
| **OLTP** (Speed Layer) | Phục vụ user real-time | MongoDB, FastAPI | Low latency, flexible schema |
| **OLAP** (Batch Layer) | Phân tích dữ liệu | HDFS, Hive, Spark | Columnar storage, batch queries |
| **Message Bus** | Decouple OLTP  OLAP | Apache Kafka | Event-driven, fault-tolerant |

### 1.2 Kiến Trúc Tổng Thể

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  React SPA  │────│  FastAPI     │────│  MongoDB        │
│  (Frontend) │     │  (Backend)   │     │  (OLTP Store)   │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
                    emit_event()
                           │
                    ┌──────▼───────┐
                    │ Apache Kafka │──── Debezium CDC ── PostgreSQL
                    │ (KRaft mode) │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Spark Stream │  Watermark · Validate · Aggregate
                    │ (Structured) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼                         ▼
     ┌─────────────────┐     ┌─────────────────┐
     │ HDFS Parquet     │     │ Daily Aggregates │
     │ fact_card_draws  │     │ agg_daily_stats  │
     └────────┬────────┘     └────────┬────────┘
              │                       │
              ▼                       ▼
     ┌─────────────────────────────────────────┐
     │    Apache Hive (SQL Interface)           │
     │    Star Schema: Fact + Dims              │
     └─────────────────────────────────────────┘
```

---

## 2. Luồng Dữ Liệu Chi Tiết (Data Flow)

### 2.1 Luồng Chính: Reading → Analytics

1. **User bấm "Lưu Reading"** trên frontend React
2. **FastAPI Backend** → `ReadingService.create_reading()`:
   - `insert_one()` vào MongoDB (OLTP) 
   - `kafka_producer.emit_reading_event()` → topic `tarot-events` 
   - Nếu Kafka fail → event lưu vào **Dead Letter Queue** (MongoDB collection)
3. **Spark Structured Streaming** đọc từ Kafka mỗi 30 giây:
   - **Parse JSON** → schema matching với `kafka_producer.py`
   - **Watermark** → xử lý event trễ tối đa 10 phút
   - **Flatten** → kéo nested fields lên top-level
   - **Explode** → 1 reading 3 lá bài → 3 rows
   - **Validate** → null check + deduplication
   - **Enrich** → thêm `reading_date`, `reading_hour`, `is_reversed`, `is_major_arcana`
   - **JOIN** → LEFT JOIN với User profiles từ CDC topic
4. **Ghi vào HDFS** dưới dạng Parquet, phân vùng theo `reading_date`, nén Snappy
5. **Aggregation Stream** → tính daily stats mỗi 5 phút
6. **Hive External Table** trỏ tới HDFS → query bằng SQL

### 2.2 Luồng CDC: PostgreSQL → Kafka

1. **PostgreSQL** lưu users table + Hive metastore
2. **Debezium** giám sát WAL (Write-Ahead Log) của PostgreSQL
3. Khi có INSERT/UPDATE/DELETE trên `users` table → tự động gửi event vào Kafka topic `dbserver1.public.users`
4. **Spark** đọc user profiles từ CDC topic (batch read) → dùng cho JOIN

### 2.3 Luồng Failover: Dead Letter Queue

```
emit_event() FAIL
      │
      ▼
MongoDB: kafka_dead_letters
      │
      ├── API: GET /api/v1/bigdata/dead-letters  (xem events)
      ├── API: POST /api/v1/bigdata/replay        (replay events)
      └── Script: scripts/replay_dead_letters.py   (replay offline)
```

---

## 3. Kafka Event Schema

### 3.1 Topic: `tarot-events`

```json
{
  "event_id": "evt_6612abc123",
  "event_type": "reading.created",
  "event_timestamp": "2026-04-09T06:00:00+00:00",
  "version": "1.0",
  
  "reading": {
    "reading_id": "6612abc123",
    "session_id": "sess_xxx",
    "user_id": null,
    "question": "Tôi có nên thay đổi công việc?",
    "reading_type": "career",
    "reading_spread": "three_card",
    "ai_model_used": "qwen2.5:1.5b",
    "tokens_used": 320,
    "processing_time_sec": 3.5,
    "ai_response_length": 1200,
    "ai_response_truncated": "...(max 2000 chars)...",
    "created_at": "2026-04-09T06:00:00+00:00"
  },
  
  "question_analysis": {
    "category": "career",
    "complexity": "medium",
    "emotion": "uncertain",
    "urgency": "medium",
    "word_count": 8
  },
  
  "cards": [
    {
      "card_id": "...",
      "card_name": "The Fool",
      "card_name_vi": "Kẻ Khờ",
      "suit": "major",
      "arcana": "major",
      "number": "0",
      "position": 1,
      "orientation": "upright",
      "position_meaning": "Quá khứ",
      "element": "air",
      "zodiac": null,
      "planet": "Uranus"
    }
  ],
  
  "metadata": {
    "app_version": "1.0.0",
    "source": "backend-api",
    "environment": "development"
  }
}
```

### 3.2 Topic: `dbserver1.public.users` (CDC)

Debezium format với `ExtractNewRecordState` transform — chỉ chứa after-state:

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "Nguyễn Văn A",
  "experience_level": "intermediate",
  "belief_system": "tarot",
  "cultural_background": "vietnamese",
  "__op": "c",
  "__table": "users",
  "__source_ts_ms": 1712649600000
}
```

---

## 4. Data Warehouse — Star Schema

### 4.1 Schema Overview

```
               ┌─────────────────┐
               │   dim_cards     │
               │ (78 Tarot cards)│
               └────────┬────────┘
                         │ card_id
┌─────────────┐ ┌───────┴─────────┐ ┌─────────────────┐
│  dim_time   │─┤ fact_card_draws │─┤ agg_daily_stats  │
│ (Calendar)  │ │  (Main Fact)    │ │ (Pre-aggregated) │
└─────────────┘ └─────────────────┘ └─────────────────┘
```

### 4.2 Tables

| Table | Type | Rows | Mô tả |
|-------|------|------|--------|
| `fact_card_draws` | Fact (External) | Tăng theo usage | 1 row = 1 card in 1 reading |
| `dim_cards` | Dimension | 78 | Thông tin 78 lá bài Rider-Waite |
| `dim_time` | Dimension | ~365/year | Calendar dimension |
| `agg_daily_stats` | Aggregation | ~1/day | Pre-computed daily statistics |

### 4.3 Partitioning & Storage

- **Format:** Apache Parquet (columnar)
- **Compression:** Snappy
- **Partition key:** `reading_date` (YYYY-MM-DD)
- **HDFS paths:**
  - `/data/tarot/fact_card_draws/reading_date=2026-04-09/`
  - `/data/tarot/dim_cards/`
  - `/data/tarot/dim_time/`
  - `/data/tarot/agg_daily_stats/`

---

## 5. Docker Infrastructure

### 5.1 Services

| Service | Image | Port(s) | RAM | Vai trò |
|---------|-------|---------|-----|---------|
| `kafka` | bitnami/kafka:3.7 | 9092, 9094 | ~512MB | Message broker (KRaft) |
| `postgres` | postgres:15-alpine | 5433 | ~200MB | App DB + Hive Metastore |
| `kafka-connect` | debezium/connect:2.5 | 8083 | ~512MB | CDC connector |
| `namenode` | hadoop-namenode:3.2.1 | 9870, 9000 | ~512MB | HDFS metadata |
| `datanode` | hadoop-datanode:3.2.1 | 9864 | ~512MB | HDFS data storage |
| `hive-metastore` | hive:2.3.2 | 9083 | ~256MB | Table schema storage |
| `hive-server` | hive:2.3.2 | 10000, 10002 | ~256MB | SQL query engine |
| `spark-master` | bitnami/spark:3.5.1 | 8081, 7077 | ~512MB | Spark coordinator |
| `spark-worker` | bitnami/spark:3.5.1 | — | ~1GB | Spark executor |
| `kafka-ui` | provectuslabs/kafka-ui | 8085 | ~200MB | Kafka web UI |

**Tổng RAM ước tính: ~4.5-5GB** (dev configuration)

### 5.2 Khởi động

```bash
# Chạy Big Data infrastructure
docker-compose -f docker-compose.bigdata.yml up -d

# Đăng ký Debezium CDC connector
./scripts/register-debezium.sh

# Setup HDFS directories
./scripts/setup-hdfs.sh

# Chạy Spark Streaming
docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /app/spark_jobs/tarot_streaming.py

# Tạo Hive tables
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 \
  -f /app/spark_jobs/create_hive_tables.sql
```

### 5.3 Web UIs

| UI | URL | Mô tả |
|----|-----|--------|
| Kafka UI | http://localhost:8085 | Topics, messages, consumer groups |
| HDFS NameNode | http://localhost:9870 | File browser, disk usage |
| Spark UI | http://localhost:8081 | Active jobs, stages, executors |
| Hive Web UI | http://localhost:10002 | Query interface |

---

## 6. API Endpoints — Big Data

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/v1/bigdata/status` | Kafka producer metrics, DLQ stats |
| `GET` | `/api/v1/bigdata/stats` | Analytics aggregations |
| `GET` | `/api/v1/bigdata/dead-letters` | List failed Kafka events |
| `POST` | `/api/v1/bigdata/replay` | Replay DLQ events to Kafka |

---

## 7. Monitoring & Observability

### 7.1 Kafka Producer Metrics

Truy cập qua `GET /api/v1/bigdata/status`:

```json
{
  "producer": {
    "is_running": true,
    "events_sent": 42,
    "events_failed": 2,
    "dlq_count": 2,
    "avg_latency_ms": 15.3,
    "success_rate": 95.45,
    "last_event_at": "2026-04-09T06:00:00Z",
    "recent_errors": []
  }
}
```

### 7.2 Health Check

Endpoint `/health` bao gồm trạng thái Kafka cùng MongoDB và Ollama:

```json
{
  "status": "healthy",
  "services": {
    "mongodb": {"connected": true},
    "ollama": {"connected": true},
    "kafka": {
      "connected": true,
      "details": {
        "events_sent": 42,
        "success_rate": 95.45
      }
    }
  }
}
```

---

## 8. Data Quality & Reliability

### 8.1 Kafka Producer
- **Idempotent producer** (`enable_idempotence=True`) → exactly-once semantics
- **Graceful degradation** → Kafka fail không ảnh hưởng reading save
- **Dead Letter Queue** → events thất bại lưu MongoDB để replay

### 8.2 Spark Streaming
- **Watermark** → xử lý late-arriving data (10 phút)
- **Null validation** → filter records thiếu critical fields
- **Deduplication** → `dropDuplicates(["event_id", "card_id"])`
- **Checkpointing** → exactly-once processing

### 8.3 Backfill
- Script `backfill_historical.py` → migrate dữ liệu cũ từ MongoDB → HDFS
- Bypass Kafka, ghi trực tiếp Parquet

---

## 9. Scripts

| Script | Mô tả | Cách chạy |
|--------|--------|-----------|
| `scripts/register-debezium.sh` | Đăng ký CDC connector | `bash scripts/register-debezium.sh` |
| `scripts/setup-hdfs.sh` | Tạo thư mục HDFS | `bash scripts/setup-hdfs.sh` |
| `scripts/test_pipeline.py` | E2E pipeline verification | `python scripts/test_pipeline.py` |
| `scripts/replay_dead_letters.py` | DLQ replay | `python scripts/replay_dead_letters.py` |
| `spark_jobs/backfill_historical.py` | Batch backfill MongoDB → HDFS | `docker exec spark-master spark-submit ...` |

---

## 10. Giá Trị Luận Văn

| Khía cạnh | Giá trị thể hiện |
|-----------|------------------|
| **Lambda Architecture** | OLTP (MongoDB) + OLAP (HDFS/Hive) song song |
| **Event-Driven** | Kafka producer/consumer, async processing |
| **CDC** | Debezium real-time capture từ PostgreSQL |
| **Streaming Processing** | Spark Structured Streaming + Watermark |
| **Star Schema** | Fact + Dimension tables trên Hive |
| **Data Quality** | Validation, deduplication, DLQ |
| **Exactly-Once** | Idempotent producer + checkpoint |
| **Graceful Degradation** | Kafka fail → app vẫn hoạt động |
| **Observability** | Metrics, health checks, Kafka UI |
| **Batch Processing** | Backfill job cho historical data |
