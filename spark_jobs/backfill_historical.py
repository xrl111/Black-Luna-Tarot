# ============================================================================
#  Black Luna Tarot — Batch Backfill Job
# ============================================================================
# Mục đích: Load dữ liệu lịch sử từ MongoDB vào HDFS Parquet.
# Dùng khi: (1) Migration dữ liệu cũ, (2) Re-populate sau khi reset HDFS
#
# Chạy bằng:
#   docker exec spark-master spark-submit \
#     --master spark://spark-master:7077 \
#     --packages org.mongodb.spark:mongo-spark-connector_2.12:10.2.1 \
#     /app/spark_jobs/backfill_historical.py \
#     --mongo-uri "mongodb://host.docker.internal:27017/tarot_system" \
#     --output-path "hdfs://namenode:9000/data/tarot/fact_card_draws" \
#     --limit 0
# ============================================================================

import argparse
import sys
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, lit, to_date, hour, when, size, explode,
    udf, current_timestamp, struct, array
)
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DoubleType, BooleanType, ArrayType
)

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BackfillHistorical")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Backfill historical readings from MongoDB to HDFS")
    parser.add_argument("--mongo-uri", required=True, help="MongoDB connection URI")
    parser.add_argument("--output-path", default="hdfs://namenode:9000/data/tarot/fact_card_draws",
                        help="HDFS output path for Parquet files")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of readings (0 = all)")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for processing")
    return parser.parse_args()


def create_spark_session():
    """Create SparkSession for batch processing"""
    spark = SparkSession.builder \
        .appName("TarotBackfillHistorical") \
        .master("spark://spark-master:7077") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "1g") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    logger.info(" SparkSession created for backfill job")
    return spark


def read_from_mongodb(spark, mongo_uri, limit=0):
    """
    Read readings from MongoDB using Spark MongoDB connector.
    Falls back to pymongo direct read if connector is not available.
    """
    try:
        # Try using Spark MongoDB Connector
        reader = spark.read \
            .format("mongodb") \
            .option("connection.uri", mongo_uri) \
            .option("database", "tarot_system") \
            .option("collection", "readings")

        if limit > 0:
            reader = reader.option("pipeline", f'[{{"$limit": {limit}}}]')

        df = reader.load()
        logger.info(f" Loaded {df.count()} readings from MongoDB via Spark connector")
        return df

    except Exception as e:
        logger.warning(f" Spark MongoDB connector failed: {e}")
        logger.info(" Falling back to pymongo direct read...")
        return read_from_mongodb_pymongo(spark, mongo_uri, limit)


def read_from_mongodb_pymongo(spark, mongo_uri, limit=0):
    """
    Fallback: Read from MongoDB using pymongo and convert to Spark DataFrame.
    This works without the mongo-spark-connector JAR.
    """
    try:
        from pymongo import MongoClient

        client = MongoClient(mongo_uri)
        db_name = mongo_uri.split("/")[-1].split("?")[0] if "/" in mongo_uri else "tarot_system"
        db = client[db_name]
        collection = db["readings"]

        query = {}
        cursor = collection.find(query)
        if limit > 0:
            cursor = cursor.limit(limit)

        readings = list(cursor)
        client.close()

        logger.info(f" Loaded {len(readings)} readings from MongoDB via pymongo")

        if not readings:
            logger.warning(" No readings found in MongoDB")
            return None

        # Convert to flat records for Spark
        flat_records = []
        for reading in readings:
            reading_id = str(reading.get("_id", ""))
            session_id = reading.get("session_id", "")
            user_id = reading.get("user_id", None)
            question = reading.get("question", "")
            reading_type = reading.get("reading_type", "")
            reading_spread = reading.get("reading_spread", "")
            ai_model = reading.get("ai_model_used", "")
            tokens = reading.get("tokens_used", 0) or 0
            proc_time = reading.get("processing_time", 0.0) or 0.0
            ai_response = reading.get("ai_response", "")
            created_at = reading.get("created_at", datetime.utcnow())
            cards = reading.get("cards_drawn", [])

            if isinstance(created_at, datetime):
                created_at_str = created_at.isoformat()
                reading_date = created_at.strftime("%Y-%m-%d")
                reading_hour = created_at.hour
            else:
                created_at_str = str(created_at)
                reading_date = str(created_at)[:10]
                reading_hour = 0

            # Analyze question
            question_analysis = _analyze_question(question)

            # Explode cards
            if not cards:
                cards = [{"card_name": "Unknown"}]

            for card in cards:
                card_data = card if isinstance(card, dict) else {}
                flat_records.append({
                    "event_id": f"backfill_{reading_id}",
                    "event_timestamp": created_at_str,
                    "version": "1.0",
                    "reading_id": reading_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "question": question,
                    "reading_type": reading_type,
                    "reading_spread": reading_spread,
                    "ai_model_used": ai_model,
                    "tokens_used": tokens,
                    "processing_time_sec": proc_time,
                    "ai_response_length": len(ai_response) if ai_response else 0,
                    "category": question_analysis["category"],
                    "complexity": question_analysis["complexity"],
                    "emotion": question_analysis["emotion"],
                    "urgency": question_analysis["urgency"],
                    "word_count": question_analysis["word_count"],
                    "card_id": str(card_data.get("card_id", "")),
                    "card_name": card_data.get("card_name", ""),
                    "card_name_vi": card_data.get("card_name_vi", ""),
                    "suit": card_data.get("suit", ""),
                    "arcana": card_data.get("card_type", card_data.get("arcana", "")),
                    "card_number": card_data.get("number", ""),
                    "position": card_data.get("position", 0) or 0,
                    "orientation": card_data.get("orientation", "upright"),
                    "position_meaning": card_data.get("position_meaning", ""),
                    "element": card_data.get("element", None),
                    "zodiac": card_data.get("zodiac", None),
                    "planet": card_data.get("planet", None),
                    "card_count": len(cards),
                    "reading_hour": reading_hour,
                    "is_reversed": card_data.get("orientation", "upright") == "reversed",
                    "is_major_arcana": card_data.get("card_type", card_data.get("arcana", "")) == "major",
                    "is_anonymous": user_id is None,
                    "has_reversed_in_reading": any(
                        c.get("orientation") == "reversed" for c in cards if isinstance(c, dict)
                    ),
                    "user_experience_level": None,
                    "user_cultural_background": None,
                    "user_belief_system": None,
                    "user_reading_frequency": None,
                    "created_at": created_at_str,
                    "reading_date": reading_date,
                })

        # Create Spark DataFrame
        schema = StructType([
            StructField("event_id", StringType()),
            StructField("event_timestamp", StringType()),
            StructField("version", StringType()),
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
            StructField("category", StringType()),
            StructField("complexity", StringType()),
            StructField("emotion", StringType()),
            StructField("urgency", StringType()),
            StructField("word_count", IntegerType()),
            StructField("card_id", StringType()),
            StructField("card_name", StringType()),
            StructField("card_name_vi", StringType()),
            StructField("suit", StringType()),
            StructField("arcana", StringType()),
            StructField("card_number", StringType()),
            StructField("position", IntegerType()),
            StructField("orientation", StringType()),
            StructField("position_meaning", StringType()),
            StructField("element", StringType()),
            StructField("zodiac", StringType()),
            StructField("planet", StringType()),
            StructField("card_count", IntegerType()),
            StructField("reading_hour", IntegerType()),
            StructField("is_reversed", BooleanType()),
            StructField("is_major_arcana", BooleanType()),
            StructField("is_anonymous", BooleanType()),
            StructField("has_reversed_in_reading", BooleanType()),
            StructField("user_experience_level", StringType()),
            StructField("user_cultural_background", StringType()),
            StructField("user_belief_system", StringType()),
            StructField("user_reading_frequency", StringType()),
            StructField("created_at", StringType()),
            StructField("reading_date", StringType()),
        ])

        df = spark.createDataFrame(flat_records, schema)
        logger.info(f" Created Spark DataFrame with {df.count()} rows")
        return df

    except Exception as e:
        logger.error(f" Failed to read from MongoDB: {e}")
        return None


def _analyze_question(question: str) -> dict:
    """Analyze question category, complexity, emotion, urgency"""
    question_lower = question.lower() if question else ""

    categories = {
        "career": ["việc", "công việc", "sự nghiệp", "thăng tiến", "nghề"],
        "love": ["tình yêu", "tình cảm", "mối quan hệ", "hôn nhân", "người yêu"],
        "health": ["sức khỏe", "bệnh", "thể chất", "tinh thần"],
        "finance": ["tiền bạc", "tài chính", "đầu tư", "kinh doanh"],
        "spiritual": ["linh hồn", "tâm linh", "mục đích", "định mệnh"],
    }
    category = "general"
    for cat, keywords in categories.items():
        if any(kw in question_lower for kw in keywords):
            category = cat
            break

    word_count = len(question.split()) if question else 0
    complexity = "simple" if word_count < 5 else ("complex" if word_count > 15 else "medium")

    emotions = {
        "uncertain": ["có nên", "không biết", "phân vân"],
        "anxious": ["lo", "sợ", "stress", "áp lực"],
        "hopeful": ["hy vọng", "mong", "ước mơ", "tương lai"],
    }
    emotion = "neutral"
    for emo, keywords in emotions.items():
        if any(kw in question_lower for kw in keywords):
            emotion = emo
            break

    urgency_keywords = ["gấp", "ngay", "khẩn", "nhanh", "hôm nay"]
    urgency = "high" if any(kw in question_lower for kw in urgency_keywords) else "medium"

    return {
        "category": category,
        "complexity": complexity,
        "emotion": emotion,
        "urgency": urgency,
        "word_count": word_count,
    }


def write_to_hdfs(df, output_path):
    """Write DataFrame to HDFS as Parquet, partitioned by reading_date"""
    logger.info(f" Writing {df.count()} rows to {output_path}")

    df.write \
        .format("parquet") \
        .mode("append") \
        .partitionBy("reading_date") \
        .option("compression", "snappy") \
        .save(output_path)

    logger.info(f" Successfully wrote data to {output_path}")


def main():
    print("=" * 70)
    print(" Black Luna Tarot — Batch Backfill Job")
    print("   MongoDB → HDFS Parquet (bypass Kafka)")
    print("=" * 70)

    args = parse_args()

    # Create Spark session
    spark = create_spark_session()

    # Read from MongoDB
    df = read_from_mongodb_pymongo(spark, args.mongo_uri, args.limit)

    if df is None or df.rdd.isEmpty():
        logger.warning(" No data to backfill. Exiting.")
        spark.stop()
        sys.exit(0)

    total_rows = df.count()
    logger.info(f" Total rows to backfill: {total_rows}")

    # Write to HDFS
    write_to_hdfs(df, args.output_path)

    # Summary
    print("")
    print("=" * 70)
    print(f" Backfill completed!")
    print(f"   - Total rows written: {total_rows}")
    print(f"   - Output path: {args.output_path}")
    print(f"   - Format: Parquet (Snappy compression)")
    print(f"   - Partitioned by: reading_date")
    print("=" * 70)

    spark.stop()


if __name__ == "__main__":
    main()
