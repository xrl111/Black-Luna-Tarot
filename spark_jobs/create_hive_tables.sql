-- ============================================================================
-- 🎯 Black Luna Tarot — Hive DDL: Tạo bảng Data Warehouse
-- ============================================================================
-- Star Schema: 1 Fact Table + 2 Dimension Tables + 1 Aggregation Table
-- Chạy script này từ beeline HOẶC Spark SQL sau khi đã có dữ liệu Parquet.
-- Cách chạy qua beeline:
--   docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000
--   > !run /app/spark_jobs/create_hive_tables.sql
-- ============================================================================

-- Tạo database riêng cho Data Warehouse
CREATE DATABASE IF NOT EXISTS tarot_dwh
COMMENT 'Black Luna Tarot - Data Warehouse for analytics';

-- ============================================================================
-- FACT TABLE: fact_card_draws
-- ============================================================================
-- Mỗi dòng = MỘT LÁ BÀI được rút trong MỘT LẦN ĐỌC.
-- Ví dụ: 1 reading với 3 lá bài = 3 dòng trong bảng này.
-- Bảng EXTERNAL trỏ tới file Parquet trên HDFS (Spark ghi vào).

CREATE EXTERNAL TABLE IF NOT EXISTS tarot_dwh.fact_card_draws (
    -- Event metadata
    event_id                STRING      COMMENT 'ID duy nhất của event (evt_xxx)',
    event_timestamp         STRING      COMMENT 'Thời điểm event được tạo (ISO 8601)',
    version                 STRING      COMMENT 'Schema version (1.0)',

    -- Reading info
    reading_id              STRING      COMMENT 'ID reading trong MongoDB',
    session_id              STRING      COMMENT 'Session ID (tạo bởi frontend)',
    user_id                 STRING      COMMENT 'User ID (null nếu ẩn danh)',
    question                STRING      COMMENT 'Câu hỏi của người dùng',
    reading_type            STRING      COMMENT 'Loại đọc bài (career, love, health, ...)',
    reading_spread          STRING      COMMENT 'Kiểu trải bài (three_card, celtic_cross, ...)',
    ai_model_used           STRING      COMMENT 'Model AI đã dùng (qwen2.5:1.5b, ...)',
    tokens_used             INT         COMMENT 'Số token AI tiêu thụ',
    processing_time_sec     DOUBLE      COMMENT 'Thời gian xử lý AI (giây)',
    ai_response_length      INT         COMMENT 'Độ dài câu trả lời AI (ký tự)',

    -- Question analysis
    category                STRING      COMMENT 'Phân loại câu hỏi (career, love, general, ...)',
    complexity              STRING      COMMENT 'Độ phức tạp (simple, medium, complex)',
    emotion                 STRING      COMMENT 'Cảm xúc phát hiện (neutral, anxious, hopeful, ...)',
    urgency                 STRING      COMMENT 'Độ khẩn cấp (medium, high)',
    word_count              INT         COMMENT 'Số từ trong câu hỏi',

    -- Card info (exploded — mỗi dòng = 1 lá bài)
    card_id                 STRING      COMMENT 'ID lá bài trong MongoDB',
    card_name               STRING      COMMENT 'Tên tiếng Anh (The Fool, King of Pentacles, ...)',
    card_name_vi            STRING      COMMENT 'Tên tiếng Việt (Kẻ Khờ, Vua Đồng Tiền, ...)',
    suit                    STRING      COMMENT 'Bộ (wands, cups, swords, pentacles, major)',
    arcana                  STRING      COMMENT 'Nhóm (major, minor)',
    card_number             STRING      COMMENT 'Số thứ tự lá bài',
    position                INT         COMMENT 'Vị trí trong trải bài (1, 2, 3, ...)',
    orientation             STRING      COMMENT 'Hướng (upright, reversed)',
    position_meaning        STRING      COMMENT 'Ý nghĩa vị trí (Quá khứ, Hiện tại, ...)',
    element                 STRING      COMMENT 'Nguyên tố (fire, water, air, earth)',
    zodiac                  STRING      COMMENT 'Cung hoàng đạo',
    planet                  STRING      COMMENT 'Hành tinh',

    -- Derived columns (tính bởi Spark)
    card_count              INT         COMMENT 'Tổng số lá bài trong reading',
    reading_hour            INT         COMMENT 'Giờ đọc bài (0-23)',
    is_reversed             BOOLEAN     COMMENT 'Lá bài này có bị ngược không?',
    is_major_arcana         BOOLEAN     COMMENT 'Lá Major Arcana?',
    is_anonymous            BOOLEAN     COMMENT 'Người dùng ẩn danh?',
    has_reversed_in_reading BOOLEAN     COMMENT 'Reading này có lá ngược nào không?',

    -- User profile (JOIN từ CDC PostgreSQL)
    user_experience_level   STRING      COMMENT 'Kinh nghiệm (beginner, intermediate, advanced)',
    user_cultural_background STRING     COMMENT 'Nền văn hóa (vietnamese, ...)',
    user_belief_system      STRING      COMMENT 'Hệ thống tín ngưỡng',
    user_reading_frequency  STRING      COMMENT 'Tần suất đọc bài',

    -- Technical
    created_at              STRING      COMMENT 'Thời điểm reading được tạo'
)
PARTITIONED BY (reading_date STRING COMMENT 'Ngày đọc bài (YYYY-MM-DD), dùng để phân vùng HDFS')
STORED AS PARQUET
LOCATION 'hdfs://namenode:9000/data/tarot/fact_card_draws/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- Tự động phát hiện partitions mới (chạy sau khi Spark đã ghi dữ liệu)
-- MSCK REPAIR TABLE tarot_dwh.fact_card_draws;


-- ============================================================================
-- DIMENSION TABLE: dim_cards — Lookup table cho thông tin lá bài
-- ============================================================================
-- 78 lá bài Rider-Waite. Dữ liệu được load 1 lần từ MongoDB.
-- Dùng để JOIN với fact_card_draws cho enriched analytics.

CREATE EXTERNAL TABLE IF NOT EXISTS tarot_dwh.dim_cards (
    card_id         STRING      COMMENT 'ID lá bài (MongoDB ObjectId)',
    card_name       STRING      COMMENT 'Tên tiếng Anh',
    card_name_vi    STRING      COMMENT 'Tên tiếng Việt',
    suit            STRING      COMMENT 'Bộ (wands, cups, swords, pentacles, major)',
    arcana          STRING      COMMENT 'Nhóm (major, minor)',
    number          STRING      COMMENT 'Số thứ tự',
    element         STRING      COMMENT 'Nguyên tố (fire, water, air, earth)',
    zodiac          STRING      COMMENT 'Cung hoàng đạo',
    planet          STRING      COMMENT 'Hành tinh',
    meaning_upright STRING      COMMENT 'Ý nghĩa khi lá xuôi',
    meaning_reversed STRING     COMMENT 'Ý nghĩa khi lá ngược',
    keywords        STRING      COMMENT 'Từ khóa chính (comma-separated)'
)
STORED AS PARQUET
LOCATION 'hdfs://namenode:9000/data/tarot/dim_cards/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');


-- ============================================================================
-- DIMENSION TABLE: dim_time — Time dimension cho phân tích theo thời gian
-- ============================================================================
-- Pre-generated time dimension table cho các truy vấn thời gian.
-- Hỗ trợ phân tích: theo ngày trong tuần, giờ, cuối tuần, v.v.

CREATE EXTERNAL TABLE IF NOT EXISTS tarot_dwh.dim_time (
    date_key        STRING      COMMENT 'Khóa ngày (YYYY-MM-DD)',
    year            INT         COMMENT 'Năm',
    month           INT         COMMENT 'Tháng (1-12)',
    day             INT         COMMENT 'Ngày (1-31)',
    day_of_week     INT         COMMENT 'Ngày trong tuần (1=Mon, 7=Sun)',
    day_name        STRING      COMMENT 'Tên ngày (Monday, Tuesday, ...)',
    hour            INT         COMMENT 'Giờ (0-23)',
    is_weekend      BOOLEAN     COMMENT 'Có phải cuối tuần?',
    quarter         INT         COMMENT 'Quý (1-4)',
    month_name      STRING      COMMENT 'Tên tháng (January, ...)',
    lunar_phase     STRING      COMMENT 'Pha mặt trăng — thú vị cho Tarot context!'
)
STORED AS PARQUET
LOCATION 'hdfs://namenode:9000/data/tarot/dim_time/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');


-- ============================================================================
-- AGGREGATION TABLE: agg_daily_stats — Thống kê hàng ngày (pre-computed)
-- ============================================================================
-- Ghi bởi Spark aggregation stream mỗi 5 phút.
-- Dashboard query bảng này thay vì scan toàn bộ fact table.

CREATE EXTERNAL TABLE IF NOT EXISTS tarot_dwh.agg_daily_stats (
    reading_date            STRING      COMMENT 'Ngày (YYYY-MM-DD)',
    total_readings          INT         COMMENT 'Tổng số readings trong ngày',
    unique_sessions         INT         COMMENT 'Số session duy nhất',
    avg_processing_time     DOUBLE      COMMENT 'Thời gian xử lý AI trung bình (giây)',
    avg_tokens_used         DOUBLE      COMMENT 'Token trung bình mỗi reading',
    avg_question_length     DOUBLE      COMMENT 'Độ dài câu hỏi trung bình (từ)',
    avg_response_length     DOUBLE      COMMENT 'Độ dài câu trả lời AI trung bình (ký tự)',
    avg_card_count          DOUBLE      COMMENT 'Số lá bài trung bình mỗi reading',
    reversed_count          INT         COMMENT 'Tổng số lá ngược',
    major_arcana_count      INT         COMMENT 'Tổng số lá Major Arcana',
    anonymous_count         INT         COMMENT 'Số reading ẩn danh',
    total_card_draws        INT         COMMENT 'Tổng số lá bài được rút',
    reversed_ratio          DOUBLE      COMMENT 'Tỷ lệ lá ngược (%)',
    major_arcana_ratio      DOUBLE      COMMENT 'Tỷ lệ Major Arcana (%)'
)
STORED AS PARQUET
LOCATION 'hdfs://namenode:9000/data/tarot/agg_daily_stats/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');


-- ============================================================================
-- CRON: Tự động phát hiện partitions mới
-- ============================================================================
-- Chạy lệnh này sau khi Spark ghi partition mới:
-- MSCK REPAIR TABLE tarot_dwh.fact_card_draws;
-- MSCK REPAIR TABLE tarot_dwh.agg_daily_stats;


-- ============================================================================
-- SAMPLE QUERIES (dùng sau khi có dữ liệu)
-- ============================================================================

-- 1. Lá bài phổ biến nhất
-- SELECT card_name, card_name_vi, COUNT(*) as total_draws
-- FROM tarot_dwh.fact_card_draws
-- GROUP BY card_name, card_name_vi
-- ORDER BY total_draws DESC
-- LIMIT 10;

-- 2. Phân bố loại câu hỏi
-- SELECT category, COUNT(DISTINCT reading_id) as total_readings
-- FROM tarot_dwh.fact_card_draws
-- GROUP BY category
-- ORDER BY total_readings DESC;

-- 3. Tỷ lệ lá ngược vs lá xuôi
-- SELECT orientation, COUNT(*) as total, 
--        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
-- FROM tarot_dwh.fact_card_draws
-- GROUP BY orientation;

-- 4. Thời gian xử lý AI trung bình theo model
-- SELECT ai_model_used, 
--        ROUND(AVG(processing_time_sec), 2) as avg_time,
--        COUNT(DISTINCT reading_id) as total_readings
-- FROM tarot_dwh.fact_card_draws
-- GROUP BY ai_model_used;

-- 5. Readings theo giờ trong ngày
-- SELECT reading_hour, COUNT(DISTINCT reading_id) as total_readings
-- FROM tarot_dwh.fact_card_draws
-- GROUP BY reading_hour
-- ORDER BY reading_hour;

-- 6. Star Schema JOIN: Fact + Dim Cards cho enriched analysis
-- SELECT f.card_name, d.element, d.meaning_upright,
--        COUNT(*) as draws, 
--        ROUND(AVG(f.processing_time_sec), 2) as avg_time
-- FROM tarot_dwh.fact_card_draws f
-- LEFT JOIN tarot_dwh.dim_cards d ON f.card_id = d.card_id
-- GROUP BY f.card_name, d.element, d.meaning_upright
-- ORDER BY draws DESC
-- LIMIT 20;

-- 7. Daily stats overview (from aggregation table)
-- SELECT reading_date, total_readings, unique_sessions,
--        avg_processing_time, reversed_ratio, major_arcana_ratio
-- FROM tarot_dwh.agg_daily_stats
-- ORDER BY reading_date DESC
-- LIMIT 7;
