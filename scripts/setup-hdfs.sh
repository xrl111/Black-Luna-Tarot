#!/bin/bash
# ============================================================================
# 🎯 Black Luna Tarot — Khởi tạo thư mục HDFS
# ============================================================================
# Chạy script này SAU KHI namenode + datanode đã healthy.
# Cách chạy: docker exec namenode bash /setup-hdfs.sh
# Hoặc mount file này vào container và chạy.
# ============================================================================

echo "🗄️  Đang tạo thư mục HDFS cho Tarot Data Warehouse..."

# Thư mục chứa dữ liệu fact table (Parquet files)
hdfs dfs -mkdir -p /data/tarot/fact_card_draws

# Thư mục checkpoint cho Spark Streaming (đảm bảo exactly-once)
hdfs dfs -mkdir -p /checkpoints/tarot_streaming

# Thư mục Hive warehouse
hdfs dfs -mkdir -p /user/hive/warehouse

# Đặt quyền mở rộng (dev mode)
hdfs dfs -chmod -R 777 /data
hdfs dfs -chmod -R 777 /checkpoints
hdfs dfs -chmod -R 777 /user

echo "✅  Tạo thư mục HDFS thành công!"
echo ""
echo "📁  Cấu trúc HDFS:"
hdfs dfs -ls -R /data
hdfs dfs -ls -R /checkpoints
hdfs dfs -ls /user/hive
