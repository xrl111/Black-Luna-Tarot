# 📚 API Documentation

## 🎯 **Tổng quan**

Tarot AI Reading System API được xây dựng với FastAPI, cung cấp các endpoints để:

- Quản lý bài Tarot
- Tạo và lấy xem bói
- Quản lý người dùng và session
- Tích hợp AI service
- Analytics và báo cáo

## 🔗 **Base URL**

```
Development: http://localhost:8000
Production: https://your-api-domain.com
API Version: /api/v1
```

## 🔐 **Authentication**

### **Session-based (Anonymous)**

- Không cần đăng nhập
- Sử dụng session token tự động
- Dữ liệu được lưu tạm thời

### **User-based (Optional)**

- JWT token authentication
- Lưu lịch sử và preferences
- Cá nhân hóa nâng cao

## 📋 **Endpoints**

### **1. Health Check**

#### `GET /health`

Kiểm tra trạng thái server

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### **2. Tarot Cards**

#### `GET /api/v1/tarot-cards`

Lấy danh sách bài Tarot

**Query Parameters:**

- `page` (int): Trang hiện tại (default: 1)
- `limit` (int): Số lượng mỗi trang (default: 10, max: 100)
- `suit` (str): Lọc theo suit (major_arcana, wands, cups, swords, pentacles)
- `card_type` (str): Lọc theo loại (major, minor)
- `search` (str): Tìm kiếm theo tên

**Response:**

```json
{
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "The Fool",
      "name_vi": "Kẻ Ngốc",
      "suit": "major_arcana",
      "number": 0,
      "meaning_upright": "New beginnings, innocence...",
      "meaning_reversed": "Recklessness, risk-taking...",
      "keywords": ["new beginnings", "innocence", "adventure"],
      "image_url": "https://example.com/fool.jpg",
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

Lấy chi tiết một lá bài

**Response:**

```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "The Fool",
  "name_vi": "Kẻ Ngốc",
  "suit": "major_arcana",
  "number": 0,
  "meaning_upright": "New beginnings, innocence...",
  "meaning_reversed": "Recklessness, risk-taking...",
  "description": "The Fool represents new beginnings...",
  "keywords": ["new beginnings", "innocence", "adventure"],
  "element": "air",
  "planet": "uranus",
  "zodiac": null,
  "image_url": "https://example.com/fool.jpg",
  "card_type": "major",
  "astrological_significance": "Uranus - Innovation and sudden changes"
}
```

### **3. Readings**

#### `POST /api/v1/readings`

Tạo xem bói mới

**Request Body:**

```json
{
  "session_id": "session_123",
  "question": "Tôi có nên thay đổi công việc không?",
  "reading_type": "three_card",
  "reading_spread": "past_present_future",
  "cards_drawn": [
    {
      "card_id": "507f1f77bcf86cd799439011",
      "position": 1,
      "orientation": "upright",
      "position_meaning": "Quá khứ"
    }
  ]
}
```

**Response:**

```json
{
  "id": "507f1f77bcf86cd799439012",
  "session_id": "session_123",
  "question": "Tôi có nên thay đổi công việc không?",
  "reading_type": "three_card",
  "reading_spread": "past_present_future",
  "cards_drawn": [
    {
      "card_id": "507f1f77bcf86cd799439011",
      "position": 1,
      "orientation": "upright",
      "position_meaning": "Quá khứ",
      "interpretation": "Trong quá khứ, bạn đã...",
      "keywords": ["new beginnings", "change"]
    }
  ],
  "ai_response": "Dựa trên các lá bài được rút...",
  "ai_summary": "Có vẻ như đây là thời điểm tốt để thay đổi...",
  "ai_advice": "Hãy cân nhắc kỹ lưỡng trước khi quyết định...",
  "ai_model_used": "llama3",
  "tokens_used": 1500,
  "processing_time": 2.5,
  "created_at": "2024-01-01T00:00:00Z",
  "tags": ["career", "change", "decision"]
}
```

#### `GET /api/v1/readings/{reading_id}`

Lấy chi tiết xem bói

#### `GET /api/v1/readings`

Lấy danh sách xem bói (cần authentication)

**Query Parameters:**

- `page` (int): Trang hiện tại
- `limit` (int): Số lượng mỗi trang
- `reading_type` (str): Lọc theo loại xem bói
- `date_from` (str): Từ ngày (YYYY-MM-DD)
- `date_to` (str): Đến ngày (YYYY-MM-DD)

#### `PUT /api/v1/readings/{reading_id}`

Cập nhật xem bói (rating, feedback)

**Request Body:**

```json
{
  "user_rating": 5,
  "user_feedback": "Rất chính xác và hữu ích!",
  "user_emotion": "satisfied"
}
```

### **4. Sessions**

#### `POST /api/v1/sessions`

Tạo session mới

**Request Body:**

```json
{
  "device_info": {
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1",
    "country": "VN",
    "city": "Ho Chi Minh",
    "timezone": "Asia/Ho_Chi_Minh",
    "language": "vi",
    "screen_resolution": "1920x1080",
    "device_type": "desktop"
  }
}
```

**Response:**

```json
{
  "session_id": "session_123",
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_at": "2024-01-02T00:00:00Z"
}
```

#### `GET /api/v1/sessions/{session_id}`

Lấy thông tin session

#### `PUT /api/v1/sessions/{session_id}`

Cập nhật session (readings_count, behavior)

### **5. AI Service**

#### `POST /api/v1/ai/generate-reading`

Tạo xem bói với AI

**Request Body:**

```json
{
  "question": "Tôi có nên thay đổi công việc không?",
  "cards": [
    {
      "name": "The Fool",
      "orientation": "upright",
      "position": "past"
    }
  ],
  "reading_type": "three_card",
  "language": "vi"
}
```

**Response:**

```json
{
  "ai_response": "Dựa trên các lá bài được rút...",
  "ai_summary": "Có vẻ như đây là thời điểm tốt...",
  "ai_advice": "Hãy cân nhắc kỹ lưỡng...",
  "model_used": "llama3",
  "tokens_used": 1500,
  "processing_time": 2.5
}
```

#### `POST /api/v1/ai/chat`

Chat với AI về xem bói

**Request Body:**

```json
{
  "message": "Bạn có thể giải thích thêm về lá The Fool không?",
  "context": {
    "reading_id": "507f1f77bcf86cd799439012",
    "cards": ["The Fool", "The Magician"]
  }
}
```

### **6. Analytics**

#### `GET /api/v1/analytics/overview`

Thống kê tổng quan

**Response:**

```json
{
  "total_readings": 1500,
  "total_users": 500,
  "active_sessions": 25,
  "popular_cards": [
    { "name": "The Fool", "count": 150 },
    { "name": "The Magician", "count": 120 }
  ],
  "reading_types": [
    { "type": "three_card", "count": 800 },
    { "type": "celtic_cross", "count": 400 }
  ],
  "average_rating": 4.5
}
```

#### `GET /api/v1/analytics/readings`

Thống kê xem bói

**Query Parameters:**

- `period` (str): daily, weekly, monthly, yearly
- `date_from` (str): Từ ngày
- `date_to` (str): Đến ngày

#### `GET /api/v1/analytics/cards`

Thống kê bài Tarot

### **7. Users (Optional)**

#### `POST /api/v1/users/register`

Đăng ký tài khoản

#### `POST /api/v1/users/login`

Đăng nhập

#### `GET /api/v1/users/profile`

Lấy thông tin profile

#### `PUT /api/v1/users/profile`

Cập nhật profile

## 🚨 **Error Responses**

### **400 Bad Request**

```json
{
  "success": false,
  "error": "Validation error",
  "details": {
    "field": "question",
    "message": "Question is required"
  }
}
```

### **404 Not Found**

```json
{
  "success": false,
  "error": "Resource not found",
  "details": {
    "resource": "tarot_card",
    "id": "507f1f77bcf86cd799439011"
  }
}
```

### **500 Internal Server Error**

```json
{
  "success": false,
  "error": "Internal server error",
  "details": {
    "message": "Database connection failed"
  }
}
```

## 📊 **Rate Limiting**

- **Anonymous**: 60 requests/minute, 1000 requests/hour
- **Authenticated**: 120 requests/minute, 2000 requests/hour
- **AI endpoints**: 10 requests/minute, 100 requests/hour

## 🔒 **Security**

- **CORS**: Configured for frontend domain
- **Rate Limiting**: Per IP and per user
- **Input Validation**: Pydantic models
- **SQL Injection**: Protected by ORM
- **XSS**: Input sanitization

## 📈 **Monitoring**

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus format
- **Logging**: Structured JSON logs
- **Error Tracking**: Sentry integration

## 🧪 **Testing**

### **Test Endpoints**

```bash
# Health check
curl http://localhost:8000/health

# Get tarot cards
curl http://localhost:8000/api/v1/tarot-cards

# Create reading
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question", "reading_type": "one_card"}'
```

### **Test with Swagger UI**

1. Truy cập http://localhost:8000/docs
2. Chọn endpoint cần test
3. Click "Try it out"
4. Nhập parameters và execute

## 📚 **SDK Examples**

### **Python**

```python
import requests

# Get tarot cards
response = requests.get("http://localhost:8000/api/v1/tarot-cards")
cards = response.json()

# Create reading
reading_data = {
    "question": "Should I change jobs?",
    "reading_type": "three_card"
}
response = requests.post("http://localhost:8000/api/v1/readings", json=reading_data)
reading = response.json()
```

### **JavaScript**

```javascript
// Get tarot cards
const response = await fetch("http://localhost:8000/api/v1/tarot-cards");
const cards = await response.json();

// Create reading
const readingData = {
  question: "Should I change jobs?",
  reading_type: "three_card",
};
const response = await fetch("http://localhost:8000/api/v1/readings", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(readingData),
});
const reading = await response.json();
```

## 🔄 **Webhooks**

### **Reading Completed**

```json
{
  "event": "reading.completed",
  "data": {
    "reading_id": "507f1f77bcf86cd799439012",
    "user_id": "507f1f77bcf86cd799439013",
    "question": "Should I change jobs?",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### **User Registered**

```json
{
  "event": "user.registered",
  "data": {
    "user_id": "507f1f77bcf86cd799439013",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## 📞 **Support**

- **Documentation**: https://your-api-domain.com/docs
- **GitHub Issues**: https://github.com/your-username/tarot-ai-system/issues
- **Email**: api-support@your-domain.com


