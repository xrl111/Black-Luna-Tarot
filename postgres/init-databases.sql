-- ============================================================================
-- 🎯 Black Luna Tarot — PostgreSQL Initialization Script
-- ============================================================================
-- File này chạy TỰ ĐỘNG lần đầu tiên khi container postgres khởi tạo.
-- Tạo 2 database trong cùng 1 instance PostgreSQL:
--   1. app_db  → Lưu bảng users cho CDC (Debezium giám sát)
--   2. hive_db → Hive Metastore lưu schema bảng SQL
-- ============================================================================

-- ============================================================================
-- DATABASE 1: hive_db (dành cho Hive Metastore — không cần thao tác thủ công)
-- ============================================================================
CREATE DATABASE hive_db;

-- ============================================================================
-- DATABASE 2: app_db (dành cho ứng dụng — Debezium CDC sẽ giám sát)
-- ============================================================================
-- (Đang kết nối vào app_db vì POSTGRES_DB=app_db trong docker-compose)

-- Bảng Users — cấu trúc relational phù hợp cho PostgreSQL
-- Các trường này được rút ra từ model User trong MongoDB hiện tại,
-- nhưng đơn giản hóa cho phù hợp với relational schema.
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    name            VARCHAR(255) NOT NULL,
    avatar_url      VARCHAR(500),
    auth_provider   VARCHAR(50) DEFAULT 'email',
    auth_provider_id VARCHAR(255),

    -- Preferences (flatten từ nested object trong MongoDB)
    experience_level    VARCHAR(50)  DEFAULT 'beginner',
    belief_system       VARCHAR(100) DEFAULT 'spiritual_but_practical',
    cultural_background VARCHAR(100) DEFAULT 'vietnamese',
    reading_frequency   VARCHAR(50)  DEFAULT 'occasional',
    preferred_style     VARCHAR(50)  DEFAULT 'detailed',
    language_preference VARCHAR(10)  DEFAULT 'vi',
    tarot_tradition     VARCHAR(50)  DEFAULT 'rider_waite',

    -- Statistics (flatten từ nested object trong MongoDB)
    total_readings      INT          DEFAULT 0,
    average_rating      DECIMAL(3,2) DEFAULT 0.00,
    engagement_score    DECIMAL(3,2) DEFAULT 0.00,
    last_reading_date   TIMESTAMP,

    -- Account status
    is_active       BOOLEAN   DEFAULT true,
    is_verified     BOOLEAN   DEFAULT false,
    role            VARCHAR(20) DEFAULT 'user',

    -- Timestamps
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DỮ LIỆU MẪU (để Debezium CDC có thứ để bắt khi test)
-- ============================================================================
INSERT INTO users (email, name, experience_level, belief_system, cultural_background) VALUES
    ('an.nguyen@example.com',   'An Nguyễn',   'beginner',     'spiritual',                'vietnamese'),
    ('binh.tran@example.com',   'Bình Trần',   'intermediate', 'practical',                'vietnamese'),
    ('chau.le@example.com',     'Châu Lê',     'advanced',     'spiritual_but_practical',  'vietnamese'),
    ('dung.pham@example.com',   'Dũng Phạm',   'beginner',     'open_minded',              'vietnamese'),
    ('em.vo@example.com',       'Em Võ',        'intermediate', 'spiritual',                'vietnamese');

-- ============================================================================
-- BẬT CDC: Tạo Publication cho Debezium
-- ============================================================================
-- Debezium sẽ đọc WAL (Write-Ahead Log) để bắt mọi thay đổi trên bảng users.
-- Publication cho phép Debezium biết nên theo dõi bảng nào.
CREATE PUBLICATION tarot_publication FOR TABLE users;

-- ============================================================================
-- INDEX cho hiệu suất truy vấn
-- ============================================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_created ON users(created_at);
