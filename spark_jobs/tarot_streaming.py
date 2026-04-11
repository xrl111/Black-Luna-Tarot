# ============================================================================
#  Black Luna Tarot — Spark Structured Streaming Pipeline
# ============================================================================
# Đọc event từ 2 nguồn Kafka:
#   1. topic 'tarot-events'       → Reading events (từ App Producer)
#   2. topic 'dbserver1.public.users' → User CDC events (từ Debezium)
# Biến đổi: Parse → Watermark → Explode Cards → JOIN Users → Enrich → Validate → HDFS Parquet
# Thêm: Aggregation Stream cho daily stats
#
# Chạy bằng:
#   docker exec spark-master spark-submit \
#     --master spark://spark-master:7077 \
#     --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
#     /app/spark_jobs/tarot_streaming.py
# ============================================================================

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, from_json, explode, to_date, hour, lit,
    when, size, count, current_timestamp, expr,
    countDistinct, avg, window, max as spark_max,
    min as spark_min, sum as spark_sum, round as spark_round
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType, BooleanType, TimestampType, ArrayType, LongType
)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TarotStreaming")


# ============================================================================
# BƯỚC 0: Khởi tạo SparkSession
# ============================================================================
def create_spark_session():
    """Create SparkSession with Hive + HDFS support"""
    spark = SparkSession.builder \
        .appName("TarotStreamingPipeline") \
        .master("spark://spark-master:7077") \
        .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .config("spark.sql.streaming.checkpointLocation", "hdfs://namenode:9000/checkpoints/tarot_streaming") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .enableHiveSupport() \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    logger.info(" SparkSession created successfully (Log Level: ERROR)")
    return spark


# ============================================================================
# BƯỚC 1: Định nghĩa Schema JSON (khớp với kafka_producer.py)
# ============================================================================

# Schema cho mỗi lá bài trong mảng cards
card_schema = StructType([
    StructField("card_id", StringType()),
    StructField("card_name", StringType()),
    StructField("card_name_vi", StringType()),
    StructField("suit", StringType()),
    StructField("arcana", StringType()),
    StructField("number", StringType()),
    StructField("position", IntegerType()),
    StructField("orientation", StringType()),
    StructField("position_meaning", StringType()),
    StructField("element", StringType()),
    StructField("zodiac", StringType()),
    StructField("planet", StringType()),
])

# Schema cho reading object
reading_schema = StructType([
    StructField("reading_id", StringType()),
    StructField("session_id", StringType()),
    StructField("user_id", StringType()),
    StructField("question", StringType()),
    StructField("reading_type", StringType()),
    StructField("reading_spread", StringType()),
    StructField("ai_model_used", StringType()),
    StructField("tokens_used", IntegerType()),
    StructField("processing_time_sec", DoubleType()),
    StructField("ai_response_length", IntegerType()),
    StructField("ai_response_truncated", StringType()),
    StructField("created_at", StringType()),
])

# Schema cho question_analysis
question_analysis_schema = StructType([
    StructField("category", StringType()),
    StructField("complexity", StringType()),
    StructField("emotion", StringType()),
    StructField("urgency", StringType()),
    StructField("word_count", IntegerType()),
])

# Schema cho metadata
metadata_schema = StructType([
    StructField("app_version", StringType()),
    StructField("source", StringType()),
    StructField("environment", StringType()),
])

# Schema TỔNG cho toàn bộ event JSON từ Kafka
tarot_event_schema = StructType([
    StructField("event_id", StringType()),
    StructField("event_type", StringType()),
    StructField("event_timestamp", StringType()),
    StructField("version", StringType()),
    StructField("reading", reading_schema),
    StructField("question_analysis", question_analysis_schema),
    StructField("cards", ArrayType(card_schema)),
    StructField("metadata", metadata_schema),
])

# Schema cho CDC User event từ Debezium (sau ExtractNewRecordState transform)
user_cdc_schema = StructType([
    StructField("id", IntegerType()),
    StructField("email", StringType()),
    StructField("name", StringType()),
    StructField("experience_level", StringType()),
    StructField("belief_system", StringType()),
    StructField("cultural_background", StringType()),
    StructField("reading_frequency", StringType()),
    StructField("preferred_style", StringType()),
    StructField("language_preference", StringType()),
    StructField("total_readings", IntegerType()),
    StructField("average_rating", DoubleType()),
    StructField("engagement_score", DoubleType()),
    StructField("is_active", BooleanType()),
    StructField("created_at", LongType()),
    StructField("updated_at", LongType()),
    StructField("__op", StringType()),
    StructField("__table", StringType()),
    StructField("__source_ts_ms", LongType()),
])


# ============================================================================
# BƯỚC 2: Đọc từ Kafka — Nguồn 1: tarot-events (Reading Stream)
# ============================================================================
def read_reading_stream(spark):
    """Read reading events from Kafka topic 'tarot-events'"""
    raw_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "tarot-events") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    # Parse JSON từ Kafka value (binary → string → struct)
    parsed = raw_stream \
        .select(
            from_json(
                col("value").cast("string"),
                tarot_event_schema
            ).alias("data"),
            col("timestamp").alias("kafka_timestamp")
        ) \
        .select("data.*", "kafka_timestamp") \
        .filter(col("event_type") == "reading.created")

    # ── Gap 4 Fix: Thêm Watermark cho Late-Arriving Data ──
    # Cho phép dữ liệu đến trễ tối đa 10 phút trước khi bị loại
    parsed = parsed.withWatermark("kafka_timestamp", "10 minutes")

    logger.info(" Reading stream connected to 'tarot-events' (watermark: 10 min)")
    return parsed


# ============================================================================
# BƯỚC 3: Đọc từ Kafka — Nguồn 2: CDC Users (Batch/Micro-batch)
# ============================================================================
def read_users_stream(spark):
    """
    Read user CDC events from Kafka topic 'dbserver1.public.users'.
    Uses batch read (not streaming) since user data changes infrequently.
    """
    try:
        users_df = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "dbserver1.public.users") \
            .option("startingOffsets", "earliest") \
            .load() \
            .select(
                from_json(
                    col("value").cast("string"),
                    user_cdc_schema
                ).alias("user")
            ) \
            .select("user.*") \
            .filter(col("__op") != "d")  # Bỏ qua các event DELETE

        # Deduplicate: giữ bản ghi mới nhất cho mỗi user
        users_df = users_df \
            .orderBy(col("__source_ts_ms").desc()) \
            .dropDuplicates(["id"])

        logger.info(f" Users loaded from CDC topic: {users_df.count()} records")
        return users_df

    except Exception as e:
        logger.warning(f" Cannot read users CDC topic (may not exist yet): {e}")
        # Return empty DataFrame with schema
        return spark.createDataFrame([], user_cdc_schema)


# ============================================================================
# BƯỚC 4: Flatten + Explode Cards
# ============================================================================
def flatten_and_explode(parsed_stream):
    """
    Kéo nested fields lên top-level và explode mảng cards.
    MỘT reading 3 lá bài → TẠO RA 3 dòng (fact_card_draw).
    """
    flattened = parsed_stream.select(
        # Event-level
        col("event_id"),
        col("event_timestamp"),
        col("version"),

        # Reading fields (flatten)
        col("reading.reading_id").alias("reading_id"),
        col("reading.session_id").alias("session_id"),
        col("reading.user_id").alias("user_id"),
        col("reading.question").alias("question"),
        col("reading.reading_type").alias("reading_type"),
        col("reading.reading_spread").alias("reading_spread"),
        col("reading.ai_model_used").alias("ai_model_used"),
        col("reading.tokens_used").alias("tokens_used"),
        col("reading.processing_time_sec").alias("processing_time_sec"),
        col("reading.ai_response_length").alias("ai_response_length"),
        col("reading.created_at").alias("created_at"),

        # Question analysis (flatten)
        col("question_analysis.category").alias("category"),
        col("question_analysis.complexity").alias("complexity"),
        col("question_analysis.emotion").alias("emotion"),
        col("question_analysis.urgency").alias("urgency"),
        col("question_analysis.word_count").alias("word_count"),

        # Cards array (keep for explode)
        col("cards"),

        # Card count before explode
        size(col("cards")).alias("card_count"),

        # Kafka metadata
        col("kafka_timestamp"),
    )

    # Explode cards array: 1 row per card
    exploded = flattened \
        .withColumn("card", explode(col("cards"))) \
        .select(
            "*",
            col("card.card_id").alias("card_id"),
            col("card.card_name").alias("card_name"),
            col("card.card_name_vi").alias("card_name_vi"),
            col("card.suit").alias("suit"),
            col("card.arcana").alias("arcana"),
            col("card.number").alias("card_number"),
            col("card.position").alias("position"),
            col("card.orientation").alias("orientation"),
            col("card.position_meaning").alias("position_meaning"),
            col("card.element").alias("element"),
            col("card.zodiac").alias("zodiac"),
            col("card.planet").alias("planet"),
        ) \
        .drop("cards", "card")

    logger.info(" Flatten + Explode cards completed")
    return exploded


# ============================================================================
# BƯỚC 5: Enrich — Thêm Derived Columns (Cột tính toán)
# ============================================================================
def enrich_data(exploded_df):
    """Add computed columns for analytical queries"""
    enriched = exploded_df \
        .withColumn("reading_date", to_date(col("created_at"))) \
        .withColumn("reading_hour", hour(col("kafka_timestamp"))) \
        .withColumn("is_reversed", col("orientation") == "reversed") \
        .withColumn("is_major_arcana", col("arcana") == "major") \
        .withColumn("is_anonymous", col("user_id").isNull()) \
        .withColumn("has_reversed_in_reading",
            when(col("orientation") == "reversed", True).otherwise(False)
        )

    logger.info(" Derived columns added")
    return enriched


# ============================================================================
# BƯỚC 6: Data Quality Validation (Phase 4.1)
# ============================================================================
def validate_data_quality(df: DataFrame) -> DataFrame:
    """
    Validate data before writing to HDFS:
    - Remove records with null critical fields
    - Deduplicate events by event_id + card_id
    - Log warning counts
    """
    total_before = None  # Can't call .count() on streaming DF

    # Filter out records with null critical fields
    valid_df = df.filter(
        col("reading_id").isNotNull() &
        col("event_id").isNotNull() &
        col("card_name").isNotNull() &
        col("reading_date").isNotNull()
    )

    # Deduplicate by event_id + card_id (handles Kafka retries)
    deduped = valid_df.dropDuplicates(["event_id", "card_id"])

    logger.info(" Data quality validation applied (null filter + dedup)")
    return deduped


# ============================================================================
# BƯỚC 7: JOIN với User data từ CDC (Stream-to-Batch JOIN)
# ============================================================================
def join_with_users(enriched_df, users_df):
    """
    LEFT JOIN reading events với user profiles từ CDC.
    Thêm thông tin experience_level, cultural_background, v.v.
    """
    if users_df is None or users_df.rdd.isEmpty():
        # Nếu chưa có user data, thêm các cột NULL
        result = enriched_df \
            .withColumn("user_experience_level", lit(None).cast(StringType())) \
            .withColumn("user_cultural_background", lit(None).cast(StringType())) \
            .withColumn("user_belief_system", lit(None).cast(StringType())) \
            .withColumn("user_reading_frequency", lit(None).cast(StringType()))
        logger.warning(" No user data available, adding NULL columns")
        return result

    # Rename user columns to avoid ambiguity
    users_renamed = users_df.select(
        col("id").cast(StringType()).alias("pg_user_id"),
        col("experience_level").alias("user_experience_level"),
        col("cultural_background").alias("user_cultural_background"),
        col("belief_system").alias("user_belief_system"),
        col("reading_frequency").alias("user_reading_frequency"),
    )

    result = enriched_df.join(
        users_renamed,
        enriched_df.user_id == users_renamed.pg_user_id,
        "left"
    ).drop("pg_user_id")

    logger.info(" JOIN with user profiles completed")
    return result


# ============================================================================
# BƯỚC 8: Ghi vào HDFS (Parquet) — phân vùng theo ngày
# ============================================================================
def write_to_hdfs(final_df):
    """
    Ghi streaming data vào HDFS dưới dạng Parquet, phân vùng theo reading_date.
    Sử dụng checkpoint để đảm bảo exactly-once semantics.
    """
    # Drop kafka_timestamp trước khi ghi (không cần trong data warehouse)
    output_df = final_df.drop("kafka_timestamp")

    query = output_df.writeStream \
        .format("parquet") \
        .option("path", "hdfs://namenode:9000/data/tarot/fact_card_draws") \
        .option("checkpointLocation", "hdfs://namenode:9000/checkpoints/tarot_streaming") \
        .partitionBy("reading_date") \
        .outputMode("append") \
        .trigger(processingTime="5 seconds") \
        .start()

    logger.info(" HDFS Parquet sink started (trigger: every 30 seconds)")
    return query


# ============================================================================
# BƯỚC 9: Aggregation Stream — Daily Stats (Phase 2.3)
# ============================================================================
def write_daily_aggregations(enriched_df):
    """
    Micro-batch aggregation stream cho dashboard.
    Tính toán daily statistics và ghi vào HDFS partition riêng.
    """
    agg_df = enriched_df \
        .withWatermark("kafka_timestamp", "1 hour") \
        .groupBy(
            window("kafka_timestamp", "1 day"),
            "reading_date"
        ) \
        .agg(
            countDistinct("reading_id").alias("total_readings"),
            countDistinct("session_id").alias("unique_sessions"),
            spark_round(avg("processing_time_sec"), 2).alias("avg_processing_time"),
            spark_round(avg("tokens_used"), 0).alias("avg_tokens_used"),
            spark_round(avg("word_count"), 1).alias("avg_question_length"),
            spark_round(avg("ai_response_length"), 0).alias("avg_response_length"),
            spark_round(avg("card_count"), 1).alias("avg_card_count"),
            count(when(col("is_reversed") == True, 1)).alias("reversed_count"),
            count(when(col("is_major_arcana") == True, 1)).alias("major_arcana_count"),
            count(when(col("is_anonymous") == True, 1)).alias("anonymous_count"),
            count("*").alias("total_card_draws"),
        )

    # Calculate derived ratios
    agg_with_ratios = agg_df \
        .withColumn("reversed_ratio",
            spark_round(col("reversed_count") / col("total_card_draws") * 100, 2)
        ) \
        .withColumn("major_arcana_ratio",
            spark_round(col("major_arcana_count") / col("total_card_draws") * 100, 2)
        ) \
        .drop("window")  # Drop window column before writing

    query = agg_with_ratios.writeStream \
        .format("parquet") \
        .option("path", "hdfs://namenode:9000/data/tarot/agg_daily_stats") \
        .option("checkpointLocation", "hdfs://namenode:9000/checkpoints/daily_agg") \
        .outputMode("update") \
        .trigger(processingTime="30 seconds") \
        .start()

    logger.info(" Daily aggregation stream started (trigger: every 5 minutes)")
    return query


# ============================================================================
# BƯỚC 10 (Debug): Ghi ra console để theo dõi
# ============================================================================
def write_to_console(final_df):
    """Write to console for debugging"""
    # Chọn ra các cột quan trọng nhất và hiện theo chiều dọc (vertical) để dễ đọc trên terminal
    debug_df = final_df.select(
        "reading_id", "user_id", "user_experience_level", "user_belief_system", 
        "reading_type", "question", "card_name", "position", "orientation"
    )
    
    query = debug_df.writeStream \
        .format("console") \
        .option("truncate", False) \
        .option("vertical", True) \
        .option("numRows", 5) \
        .outputMode("append") \
        .trigger(processingTime="5 seconds") \
        .start()

    logger.info(" Console sink started (debug mode)")
    return query


# ============================================================================
# MAIN: Khởi chạy Pipeline
# ============================================================================
def main():
    print("=" * 70)
    print(" Black Luna Tarot — Spark Streaming Pipeline v2.0")
    print("   Features: Watermark, Data Quality, Aggregation Stream")
    print("=" * 70)

    # Bước 0: Tạo SparkSession
    spark = create_spark_session()

    # Bước 1: Đọc Reading events từ Kafka (with watermark)
    reading_stream = read_reading_stream(spark)

    # Bước 2: Đọc User data từ CDC (batch)
    users_df = read_users_stream(spark)

    # Bước 3: Flatten + Explode Cards
    exploded = flatten_and_explode(reading_stream)

    # Bước 4: Enrich với derived columns
    enriched = enrich_data(exploded)

    # Bước 5: Data Quality Validation
    validated = validate_data_quality(enriched)

    # Bước 6: JOIN với user profiles
    # LƯU Ý: Stream-to-static JOIN (streaming DF join batch DF) 
    # Spark hỗ trợ điều này natively
    final_df = join_with_users(validated, users_df)

    # Bước 7: Ghi vào HDFS (Parquet) — Fact table
    hdfs_query = write_to_hdfs(final_df)

    # Bước 8: Aggregation Stream — Daily stats
    try:
        agg_query = write_daily_aggregations(final_df)
    except Exception as e:
        logger.warning(f" Aggregation stream failed to start: {e}")
        agg_query = None

    # Bước 9: Ghi ra console (debug)
    console_query = write_to_console(final_df)

    print("")
    print("=" * 70)
    print(" Pipeline đang chạy! Chờ events từ Kafka...")
    print("   - Reading events:  topic 'tarot-events' (watermark: 10min)")
    print("   - User CDC:        topic 'dbserver1.public.users'")
    print("   - Fact output:     hdfs://namenode:9000/data/tarot/fact_card_draws/")
    print("   - Agg output:      hdfs://namenode:9000/data/tarot/agg_daily_stats/")
    print("   - Fact trigger:    mỗi 5 giây")
    print("   - Agg trigger:     mỗi 30 giây")
    print("   - Data quality:    null filter + dedup")
    print("   - Nhấn Ctrl+C để dừng.")
    print("=" * 70)

    # Chờ cho đến khi pipeline bị dừng
    hdfs_query.awaitTermination()


if __name__ == "__main__":
    main()
