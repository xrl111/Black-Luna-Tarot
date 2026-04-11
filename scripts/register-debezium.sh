#!/bin/bash
# ============================================================================
#  Black Luna Tarot — Đăng ký Debezium CDC Connector
# ============================================================================
# Chạy script này SAU KHI kafka-connect đã khởi động hoàn tất.
# Script gửi REST API tới Kafka Connect để đăng ký PostgreSQL connector.
# ============================================================================

CONNECT_URL="http://localhost:8083"
CONNECTOR_CONFIG="./debezium/register-postgres-connector.json"

echo "  Đang kiểm tra Kafka Connect..."

# Chờ Kafka Connect sẵn sàng (tối đa 60 giây)
for i in $(seq 1 12); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" $CONNECT_URL/connectors)
    if [ "$STATUS" = "200" ]; then
        echo "  Kafka Connect đã sẵn sàng!"
        break
    fi
    echo "  Chờ Kafka Connect khởi động... ($i/12)"
    sleep 5
done

if [ "$STATUS" != "200" ]; then
    echo "  Kafka Connect không phản hồi sau 60 giây. Hủy."
    exit 1
fi

echo ""
echo "  Đang đăng ký Debezium PostgreSQL Connector..."

# Đăng ký connector
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d @$CONNECTOR_CONFIG \
    $CONNECT_URL/connectors)

echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "  Danh sách connectors hiện tại:"
curl -s $CONNECT_URL/connectors | python -m json.tool 2>/dev/null

echo ""
echo "  Trạng thái connector:"
curl -s $CONNECT_URL/connectors/tarot-postgres-connector/status | python -m json.tool 2>/dev/null

echo ""
echo "  Hoàn tất! Debezium đang giám sát bảng 'users' trong PostgreSQL."
echo "    Topic CDC: dbserver1.public.users"
