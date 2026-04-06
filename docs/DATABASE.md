# 🗄️ Database Schema Documentation

## 🎯 **Tổng quan**

Black Luna Tarot sử dụng MongoDB làm database chính, với Motor (async driver) cho Python. Schema được thiết kế cho:

- Hiệu suất truy vấn cao (async operations)
- Dữ liệu phi cấu trúc linh hoạt
- Hỗ trợ 78 lá bài Tarot đầy đủ (Major & Minor Arcana)
- Lưu trữ readings và AI training data

## 🏗️ **Kiến trúc Database**

```
MongoDB (Local hoặc Atlas Free Tier)
├── Database: tarot_system
│   ├── Collection: tarot_cards       ← 78 lá bài Tarot
│   ├── Collection: readings          ← Lịch sử readings
│   ├── Collection: users             ← Người dùng (optional)
│   ├── Collection: sessions          ← Anonymous sessions
│   └── Collection: ai_training_data  ← Dữ liệu training AI
```

## 📊 **Collections Schema**

### **1. tarot_cards**

Lưu trữ thông tin 78 lá bài Tarot (Major & Minor Arcana).

```javascript
{
  "_id": ObjectId("689483ffac8d159543c982d4"),
  "name": "The Fool",
  "name_vi": "Kẻ Ngốc",
  "suit": "major",
  "number": 0,
  "court_rank": null,

  // Meanings
  "meaning_upright": "New beginnings, innocence, spontaneity, free spirit",
  "meaning_reversed": "Recklessness, risk-taking, inconsideration",
  "description": "The Fool represents new beginnings, having faith in the future...",

  // Keywords and associations
  "keywords": ["new beginnings", "innocence", "adventure", "spontaneity", "faith"],
  "element": "air",
  "planet": "uranus",
  "zodiac": null,

  // Visual and metadata
  "image_url": "/uploads/tarot-cards/m00.jpg",
  "card_type": "major",
  "astrological_significance": "Uranus - Innovation and sudden changes",

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Suits hợp lệ:** `major`, `wands`, `cups`, `swords`, `pentacles`

**Indexes:**

```javascript
db.tarot_cards.createIndex({ name: 1 });
db.tarot_cards.createIndex({ suit: 1 });
db.tarot_cards.createIndex({ number: 1 });
db.tarot_cards.createIndex({ card_type: 1 });

// Text search index
db.tarot_cards.createIndex({
  name: "text",
  name_vi: "text",
  keywords: "text",
});
```

---

### **2. readings**

Lưu trữ các lần xem bói và kết quả.

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "session_id": "session_abc123",
  "user_id": ObjectId("507f1f77bcf86cd799439013"),     // Optional

  // Reading details
  "question": "Tôi có nên thay đổi công việc không?",
  "reading_type": "three_card",
  "reading_spread": "past_present_future",

  // Cards drawn
  "cards_drawn": [
    {
      "card_id": ObjectId("689483ffac8d159543c982d4"),
      "position": 1,
      "orientation": "upright",
      "position_meaning": "Quá khứ",
      "interpretation": "Trong quá khứ, bạn đã...",
      "keywords": ["new beginnings", "change"]
    }
  ],

  // AI response
  "ai_response": "Dựa trên các lá bài được rút...",
  "ai_summary": "Có vẻ như đây là thời điểm tốt để thay đổi...",
  "ai_advice": "Hãy cân nhắc kỹ lưỡng trước khi quyết định...",

  // User feedback
  "user_rating": 5,
  "user_feedback": "Rất chính xác và hữu ích!",
  "user_emotion": "satisfied",

  // Technical details
  "ai_model_used": "qwen2.5:1.5b",
  "tokens_used": 1500,
  "processing_time": 2.5,

  // Metadata
  "tags": ["career", "change", "decision"],

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
db.readings.createIndex({ session_id: 1 });
db.readings.createIndex({ user_id: 1 });
db.readings.createIndex({ reading_type: 1 });
db.readings.createIndex({ created_at: -1 });

// Compound indexes
db.readings.createIndex({ user_id: 1, created_at: -1 });
db.readings.createIndex({ session_id: 1, created_at: -1 });
```

---

### **3. users**

Lưu trữ thông tin người dùng (optional — Phase 2).

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "email": "user@example.com",
  "name": "Nguyễn Văn A",
  "avatar_url": "https://example.com/avatar.jpg",

  // Authentication
  "password_hash": "$2b$12$...",
  "auth_provider": "email",

  // User preferences
  "preferences": {
    "reading_style": "detailed",
    "language": "vi",
    "theme": "auto"
  },

  // Account status
  "is_active": true,
  "is_verified": false,
  "role": "user",
  "last_login": ISODate("2024-01-01T00:00:00Z"),

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ is_active: 1 });
db.users.createIndex({ created_at: -1 });
```

---

### **4. sessions**

Lưu trữ thông tin session người dùng anonymous.

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "session_id": "session_abc123",

  // Session data
  "readings_count": 5,
  "last_activity": ISODate("2024-01-01T00:00:00Z"),

  // Device information
  "device_info": {
    "user_agent": "Mozilla/5.0 ...",
    "ip_address": "192.168.1.1",
    "language": "vi",
    "device_type": "desktop"
  },

  // Session status
  "is_active": true,
  "expires_at": ISODate("2024-01-31T00:00:00Z"),

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
db.sessions.createIndex({ session_id: 1 }, { unique: true });
db.sessions.createIndex({ is_active: 1 });
db.sessions.createIndex({ expires_at: 1 });
db.sessions.createIndex({ created_at: -1 });
```

---

### **5. ai_training_data**

Lưu trữ dữ liệu training cho AI.

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439015"),
  "reading_id": ObjectId("507f1f77bcf86cd799439012"),
  "session_id": "session_abc123",

  // Training data
  "question": "Tôi có nên thay đổi công việc không?",
  "question_category": "career",

  // Context
  "cards_context": "The Fool (upright) - Past: New beginnings...",
  "cards_combination": ["The Fool", "The Magician", "The High Priestess"],
  "spread_type": "past_present_future",

  // AI response
  "ai_response": "Dựa trên các lá bài được rút...",

  // User feedback
  "user_rating": 5,
  "user_feedback": "Rất chính xác và hữu ích!",

  // Training metadata
  "training_status": "pending",
  "model_version": "qwen2-v1.0",
  "quality_score": 0.95,

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
db.ai_training_data.createIndex({ reading_id: 1 });
db.ai_training_data.createIndex({ training_status: 1 });
db.ai_training_data.createIndex({ question_category: 1 });
db.ai_training_data.createIndex({ quality_score: -1 });
```

---

## 🔍 **Query Examples**

### **1. Lấy bài Tarot theo suit**

```javascript
db.tarot_cards.find({ suit: "major" });
```

### **2. Tìm kiếm bài Tarot**

```javascript
db.tarot_cards.find({
  $text: { $search: "fool" },
});
```

### **3. Lấy readings của session**

```javascript
db.readings
  .find({ session_id: "session_abc123" })
  .sort({ created_at: -1 })
  .limit(10);
```

### **4. Thống kê readings theo ngày**

```javascript
db.readings.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      count: { $sum: 1 },
      avg_rating: { $avg: "$user_rating" },
    },
  },
  { $sort: { _id: -1 } },
]);
```

### **5. Bài Tarot phổ biến nhất**

```javascript
db.readings.aggregate([
  { $unwind: "$cards_drawn" },
  {
    $group: {
      _id: "$cards_drawn.card_id",
      count: { $sum: 1 },
    },
  },
  { $sort: { count: -1 } },
  { $limit: 10 },
]);
```

---

## 📈 **Performance Optimization**

### **Index Strategy**

- **Single field indexes**: Cho các trường thường query
- **Compound indexes**: Cho queries phức tạp (vd: session_id + created_at)
- **Text indexes**: Cho tìm kiếm full-text (name, name_vi, keywords)

### **Query Optimization**

```javascript
// Sử dụng projection để giảm data transfer
db.readings.find({}, { question: 1, created_at: 1 });

// Sử dụng limit
db.readings.find().limit(100);
```

## 📊 **Backup & Recovery**

### **Automated Backups**

```bash
# MongoDB Atlas tự động backup
# Hoặc manual backup
mongodump --db tarot_system --out /backup/
```

### **Data Export**

```bash
mongoexport --db tarot_system --collection tarot_cards --out tarot_cards.json
mongoexport --db tarot_system --collection readings --out readings.json
```

## 🔧 **Maintenance**

### **Data Cleanup**

```javascript
// Xóa sessions expired
db.sessions.deleteMany({
  expires_at: { $lt: new Date() },
});
```

## 📚 **Resources**

- [MongoDB Documentation](https://docs.mongodb.com)
- [MongoDB Atlas](https://cloud.mongodb.com)
- [Motor (Async MongoDB Driver)](https://motor.readthedocs.io)
