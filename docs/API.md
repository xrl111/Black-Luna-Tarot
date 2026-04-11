#  API Documentation

##  **Tổng quan**

Black Luna Tarot API được xây dựng với FastAPI, cung cấp các endpoints để:

- Quản lý bài Tarot (CRUD, search, filter, images)
- Tạo và quản lý readings
- Tích hợp AI service (generate & streaming)
- Kiểm tra system health & connections

##  **Base URL**

```
Development: http://localhost:8000
Production:  https://your-api-domain.com
API Version: /api/v1
```

##  **Interactive API Docs**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

> Swagger UI chỉ hiển thị khi `DEBUG=true` hoặc `SHOW_DOCS_IN_PROD=true`.

---

##  **Endpoints**

### **1. Health Check (Root)**

#### `GET /health`

Kiểm tra trạng thái server với thông tin service connections.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1710000000.0,
  "services": { "mongodb": "connected", "ollama": "connected" },
  "summary": { "connected": 2, "total": 2 }
}
```

#### `GET /health/simple`

Health check nhanh, không kiểm tra external services.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1710000000.0
}
```

#### `GET /`

Root endpoint.

**Response:**

```json
{
  "message": "Welcome to Tarot AI Reading System",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### **2. Tarot Cards** — `/api/v1/tarot-cards`

#### `GET /api/v1/tarot-cards`

Lấy danh sách bài Tarot có phân trang và filter.

**Query Parameters:**

| Parameter | Type | Mô tả |
|-----------|------|--------|
| `page` | int | Trang hiện tại (default: 1) |
| `limit` | int | Số lượng mỗi trang (default: 10, max: 100) |
| `suit` | str | Lọc theo suit: `wands`, `cups`, `swords`, `pentacles`, `major` |
| `card_type` | str | Lọc theo loại: `major`, `minor` |
| `element` | str | Lọc theo element: `fire`, `water`, `air`, `earth` |
| `search` | str | Tìm kiếm theo tên và keywords |

**Response:**

```json
{
  "items": [
    {
      "id": "689483ffac8d159543c982d4",
      "name": "The Fool",
      "name_vi": "Kẻ Ngốc",
      "suit": "major",
      "number": 0,
      "meaning_upright": "New beginnings, innocence...",
      "meaning_reversed": "Recklessness, risk-taking...",
      "keywords": ["new beginnings", "innocence", "adventure"],
      "image_url": "/uploads/tarot-cards/m00.jpg",
      "card_type": "major"
    }
  ],
  "total": 78,
  "page": 1,
  "limit": 10,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

#### `GET /api/v1/tarot-cards/{card_id}`

Lấy chi tiết một lá bài theo ID.

#### `POST /api/v1/tarot-cards`

Tạo lá bài Tarot mới.

**Request Body:** TarotCard model (xem schema trong Swagger)

**Error Responses:**
- `409`: Card with this name already exists

#### `POST /api/v1/tarot-cards/with-image`

Tạo lá bài Tarot mới kèm upload hình ảnh (multipart/form-data).

#### `PUT /api/v1/tarot-cards/{card_id}`

Cập nhật thông tin lá bài.

#### `DELETE /api/v1/tarot-cards/{card_id}`

Xóa lá bài.

---

#### **Search & Filter**

#### `GET /api/v1/tarot-cards/search/{query}`

Tìm kiếm bài Tarot theo tên, keywords, description. Query tối thiểu 2 ký tự.

#### `GET /api/v1/tarot-cards/suit/{suit}`

Lấy tất cả bài theo suit. Giá trị hợp lệ: `wands`, `cups`, `swords`, `pentacles`, `major`.

#### `GET /api/v1/tarot-cards/random/{count}`

Lấy ngẫu nhiên N lá bài (1–78). Hỗ trợ filter theo `suit` qua query parameter.

#### `GET /api/v1/tarot-cards/stats/overview`

Thống kê tổng quan về bộ bài Tarot.

---

#### **Image Endpoints**

#### `GET /api/v1/tarot-cards/image/{card_id}`

Lấy hình ảnh lá bài theo card ID. Trả về file ảnh (JPEG/PNG/WebP).

#### `GET /api/v1/tarot-cards/image/filename/{image_filename}`

Lấy hình ảnh lá bài theo tên file (vd: `m00.jpg`, `c01.jpg`).

#### `GET /api/v1/tarot-cards/images/list`

Liệt kê tất cả file ảnh có sẵn trong thư mục `uploads/tarot-cards`.

**Response:**

```json
{
  "total_images": 78,
  "images": ["c01.jpg", "c02.jpg", "m00.jpg", "..."]
}
```

---

### **3. Readings** — `/api/v1/readings`

#### `POST /api/v1/readings`

Tạo reading mới.

**Request Body:**

```json
{
  "session_id": "session_abc123",
  "question": "Tôi có nên thay đổi công việc không?",
  "reading_type": "three_card",
  "cards_drawn": [
    {
      "card_id": "689483ffac8d159543c982d4",
      "position": 1,
      "orientation": "upright",
      "position_meaning": "Quá khứ"
    }
  ],
  "ai_response": "Dựa trên các lá bài được rút..."
}
```

> **Lưu ý**: Cần cung cấp `session_id`, `question`, ít nhất 1 card trong `cards_drawn`, và `ai_response`.

#### `GET /api/v1/readings/{reading_id}`

Lấy chi tiết reading theo ID.

#### `GET /api/v1/readings/session/{session_id}`

Lấy danh sách readings theo session. Hỗ trợ `limit` query parameter (default: 10, max: 100).

#### `PUT /api/v1/readings/{reading_id}`

Cập nhật reading (rating, feedback).

**Request Body:**

```json
{
  "user_rating": 5,
  "user_feedback": "Rất chính xác và hữu ích!"
}
```

#### `DELETE /api/v1/readings/{reading_id}`

Xóa reading.

#### `GET /api/v1/readings/stats/overview`

Thống kê readings. Hỗ trợ filter theo `session_id` query parameter.

---

### **4. AI Service** — `/api/v1/ai`

#### `POST /api/v1/ai/generate-reading`

Tạo AI tarot reading. Gửi câu hỏi và danh sách lá bài, nhận kết quả phân tích từ AI.

**Request Body:**

```json
{
  "question": "Tôi nên tập trung điều gì trong 3 tháng tới?",
  "cards": [
    {
      "id": "689483ffac8d159543c982d4",
      "name": "King of Pentacles",
      "name_vi": "Vua Đồng Tiền"
    }
  ],
  "reading_type": "general",
  "reading_detail": "quick"
}
```

| Field | Type | Mô tả |
|-------|------|--------|
| `question` | string | Câu hỏi của người dùng |
| `cards` | list | Danh sách lá bài đã rút (với id, name, name_vi) |
| `reading_type` | string | Loại reading (optional, default: `"general"`) |
| `reading_detail` | string | `"quick"` hoặc `"full"` (optional, default: `"quick"`) |

**Response:**

```json
{
  "ai_response": "Dựa trên các lá bài được rút...",
  "ai_summary": null,
  "ai_advice": null,
  "cards_interpreted": 1,
  "response_length": 350,
  "model_used": "qwen2.5:1.5b",
  "generated_at": "2026-03-17T23:30:00Z"
}
```

#### `POST /api/v1/ai/generate-reading/stream`

Streaming version — phản hồi AI được gửi từng phần qua `text/plain` stream. Cùng request body như endpoint trên.

**Response**: `text/plain` streaming (chunks gửi liên tục khi AI generate).

#### `POST /api/v1/ai/train-model`

Submit training data cho AI model.

**Request Body:** list of training data objects.

---

### **5. System** — `/api/v1/system`

#### `GET /api/v1/system/connections`

Kiểm tra tất cả service connections (MongoDB + Ollama).

**Response:**

```json
{
  "status": "success",
  "connections": {
    "mongodb": { "connected": true, "latency_ms": 15 },
    "ollama": { "connected": true, "latency_ms": 25 }
  },
  "summary": {
    "connected": 2,
    "total": 2,
    "all_connected": true
  }
}
```

#### `GET /api/v1/system/connections/mongodb`

Kiểm tra MongoDB connection.

#### `GET /api/v1/system/connections/ollama`

Kiểm tra Ollama connection.

#### `POST /api/v1/system/connections/refresh`

Force refresh tất cả connections (bypass cache).

#### `GET /api/v1/system/health/detailed`

Health check chi tiết với thông tin đầy đủ các service.

---

##  **Error Responses**

Tất cả errors trả về format JSON:

### **400 Bad Request**

```json
{
  "detail": "Invalid suit. Must be one of: wands, cups, swords, pentacles, major"
}
```

### **404 Not Found**

```json
{
  "detail": "Card not found"
}
```

### **409 Conflict**

```json
{
  "detail": "Card with this name already exists"
}
```

### **500 Internal Server Error**

```json
{
  "detail": "Failed to generate reading"
}
```

##  **Rate Limiting**

- **Default**: 60 requests/minute, 1000 requests/hour
- Rate limiting có thể bật/tắt qua `ENABLE_RATE_LIMITING` env var

##  **Security**

- **CORS**: Configurable via `CORS_ORIGINS` env var
- **Trusted Hosts**: Configurable via `TRUSTED_HOSTS` env var
- **Rate Limiting**: Per IP middleware
- **Security Headers**: Toggleable via `ENABLE_SECURITY_HEADERS`
- **Cache Control**: Toggleable via `ENABLE_CACHE_HEADERS`
- **Input Validation**: Pydantic models cho tất cả request/response

##  **Monitoring**

- **Health Checks**: `/health` (full) và `/health/simple`
- **System Connections**: `/api/v1/system/connections`
- **Logging**: Structured JSON logs via `structlog`
- **Error Tracking**: Sentry integration (optional, qua `SENTRY_DSN`)

##  **Testing**

### **Test với cURL**

```bash
# Health check
curl http://localhost:8000/health

# Get tarot cards
curl "http://localhost:8000/api/v1/tarot-cards?limit=5"

# Search cards
curl http://localhost:8000/api/v1/tarot-cards/search/fool

# Random cards
curl http://localhost:8000/api/v1/tarot-cards/random/3

# Check system connections
curl http://localhost:8000/api/v1/system/connections

# Generate AI reading
curl -X POST http://localhost:8000/api/v1/ai/generate-reading \
  -H "Content-Type: application/json" \
  -d '{"question": "Should I change jobs?", "cards": [{"name": "The Fool"}]}'
```

### **Test với Swagger UI**

1. Truy cập http://localhost:8000/docs
2. Chọn endpoint cần test
3. Click "Try it out"
4. Nhập parameters và Execute
