# 🗄️ Database Schema Documentation

## 🎯 **Tổng quan**

Tarot AI Reading System sử dụng MongoDB làm database chính, với thiết kế schema tối ưu cho:

- Hiệu suất truy vấn cao
- Khả năng mở rộng
- Dữ liệu phi cấu trúc linh hoạt
- Analytics và reporting

## 🏗️ **Kiến trúc Database**

```
MongoDB Atlas (Free Tier)
├── Database: tarot_system
│   ├── Collection: tarot_cards
│   ├── Collection: readings
│   ├── Collection: users
│   ├── Collection: sessions
│   ├── Collection: ai_training_data
│   └── Collection: analytics
```

## 📊 **Collections Schema**

### **1. tarot_cards**

Lưu trữ thông tin 78 lá bài Tarot (Major & Minor Arcana)

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "The Fool",
  "name_vi": "Kẻ Ngốc",
  "suit": "major_arcana",
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
  "image_url": "https://example.com/fool.jpg",
  "card_type": "major",
  "astrological_significance": "Uranus - Innovation and sudden changes",

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
// Performance indexes
db.tarot_cards.createIndex({ name: 1 });
db.tarot_cards.createIndex({ suit: 1 });
db.tarot_cards.createIndex({ number: 1 });
db.tarot_cards.createIndex({ card_type: 1 });

// Search indexes
db.tarot_cards.createIndex({
  name: "text",
  name_vi: "text",
  keywords: "text",
});
```

### **2. readings**

Lưu trữ các lần xem bói và kết quả

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "session_id": "session_123",
  "user_id": ObjectId("507f1f77bcf86cd799439013"), // Optional

  // Reading details
  "question": "Tôi có nên thay đổi công việc không?",
  "reading_type": "three_card",
  "reading_spread": "past_present_future",

  // Cards drawn
  "cards_drawn": [
    {
      "card_id": ObjectId("507f1f77bcf86cd799439011"),
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
  "ai_model_used": "llama3",
  "tokens_used": 1500,
  "processing_time": 2.5,
  "reading_duration": 180.0,

  // Metadata
  "tags": ["career", "change", "decision"],
  "is_public": false,
  "share_url": "https://tarot-app.com/share/abc123",

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
// Performance indexes
db.readings.createIndex({ session_id: 1 });
db.readings.createIndex({ user_id: 1 });
db.readings.createIndex({ reading_type: 1 });
db.readings.createIndex({ created_at: -1 });

// Analytics indexes
db.readings.createIndex({ user_rating: 1 });
db.readings.createIndex({ ai_model_used: 1 });
db.readings.createIndex({ tags: 1 });

// Compound indexes
db.readings.createIndex({
  user_id: 1,
  created_at: -1,
});
db.readings.createIndex({
  reading_type: 1,
  created_at: -1,
});
```

### **3. users**

Lưu trữ thông tin người dùng (optional)

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "email": "user@example.com",
  "name": "Nguyễn Văn A",
  "avatar_url": "https://example.com/avatar.jpg",

  // Authentication
  "password_hash": "$2b$12$...", // Optional
  "auth_provider": "email",
  "auth_provider_id": null,

  // User preferences
  "preferences": {
    "reading_style": "detailed",
    "language": "vi",
    "theme": "auto",
    "notifications": {
      "email": true,
      "push": false
    }
  },

  // User statistics
  "statistics": {
    "total_readings": 25,
    "favorite_cards": ["The Fool", "The Magician"],
    "average_rating": 4.5,
    "last_reading_date": ISODate("2024-01-01T00:00:00Z"),
    "reading_streak": 5
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
// Performance indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ auth_provider: 1, auth_provider_id: 1 });
db.users.createIndex({ is_active: 1 });

// Analytics indexes
db.users.createIndex({ created_at: -1 });
db.users.createIndex({ last_login: -1 });
```

### **4. sessions**

Lưu trữ thông tin session người dùng

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "session_id": "session_123",
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",

  // Session data
  "readings_count": 5,
  "total_duration": 45.5, // minutes
  "last_activity": ISODate("2024-01-01T00:00:00Z"),

  // Device information
  "device_info": {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "ip_address": "192.168.1.1",
    "country": "VN",
    "city": "Ho Chi Minh",
    "timezone": "Asia/Ho_Chi_Minh",
    "language": "vi",
    "screen_resolution": "1920x1080",
    "device_type": "desktop"
  },

  // User behavior
  "behavior": {
    "reading_types_used": ["three_card", "celtic_cross"],
    "average_rating": 4.2,
    "engagement_score": 0.85,
    "return_visitor": true
  },

  // Session status
  "is_active": true,
  "expires_at": ISODate("2024-01-02T00:00:00Z"),

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
// Performance indexes
db.sessions.createIndex({ session_id: 1 }, { unique: true });
db.sessions.createIndex({ session_token: 1 });
db.sessions.createIndex({ is_active: 1 });
db.sessions.createIndex({ expires_at: 1 });

// Analytics indexes
db.sessions.createIndex({ created_at: -1 });
db.sessions.createIndex({ last_activity: -1 });
db.sessions.createIndex({ "device_info.country": 1 });
```

### **5. ai_training_data**

Lưu trữ dữ liệu training cho AI

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439015"),
  "reading_id": ObjectId("507f1f77bcf86cd799439012"),
  "user_id": ObjectId("507f1f77bcf86cd799439013"), // Optional
  "session_id": "session_123",

  // Training data
  "question": "Tôi có nên thay đổi công việc không?",
  "question_category": "career",
  "question_complexity": "medium",

  // Context data
  "cards_context": "The Fool (upright) - Past: New beginnings...",
  "cards_combination": ["The Fool", "The Magician", "The High Priestess"],
  "spread_type": "past_present_future",

  // AI response data
  "ai_response": "Dựa trên các lá bài được rút...",
  "ai_response_length": 1500,
  "ai_response_tone": "encouraging",

  // User feedback
  "user_rating": 5,
  "user_feedback": "Rất chính xác và hữu ích!",
  "user_satisfaction": "very_satisfied",
  "user_action_taken": "will_consider_change",

  // Training metadata
  "training_status": "pending",
  "model_version": "llama3-v1.0",
  "training_priority": 8,
  "quality_score": 0.95,

  // Timestamps
  "processed_at": null,
  "trained_at": null,
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
// Performance indexes
db.ai_training_data.createIndex({ reading_id: 1 });
db.ai_training_data.createIndex({ user_id: 1 });
db.ai_training_data.createIndex({ training_status: 1 });
db.ai_training_data.createIndex({ model_version: 1 });

// Training indexes
db.ai_training_data.createIndex({ training_priority: -1 });
db.ai_training_data.createIndex({ quality_score: -1 });
db.ai_training_data.createIndex({ question_category: 1 });
```

### **6. analytics**

Lưu trữ dữ liệu analytics và metrics

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439016"),
  "date": ISODate("2024-01-01T00:00:00Z"),
  "period": "daily",

  // Usage metrics
  "total_readings": 150,
  "total_users": 45,
  "active_sessions": 25,
  "new_users": 12,

  // Performance metrics
  "average_response_time": 2.5,
  "success_rate": 0.98,
  "error_rate": 0.02,

  // Content metrics
  "popular_cards": [
    {"name": "The Fool", "count": 25},
    {"name": "The Magician", "count": 20}
  ],
  "reading_types": [
    {"type": "three_card", "count": 80},
    {"type": "celtic_cross", "count": 40}
  ],

  // User engagement
  "average_rating": 4.5,
  "average_session_duration": 15.5,
  "bounce_rate": 0.25,

  // AI metrics
  "ai_models_used": {
    "llama3": 120,
    "mistral": 30
  },
  "total_tokens_used": 150000,

  // Timestamps
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**

```javascript
// Performance indexes
db.analytics.createIndex({ date: -1 });
db.analytics.createIndex({ period: 1, date: -1 });

// Query indexes
db.analytics.createIndex({ total_readings: -1 });
db.analytics.createIndex({ average_rating: -1 });
```

## 🔍 **Query Examples**

### **1. Lấy bài Tarot theo suit**

```javascript
db.tarot_cards.find({ suit: "major_arcana" });
```

### **2. Tìm kiếm bài Tarot**

```javascript
db.tarot_cards.find({
  $text: { $search: "fool" },
});
```

### **3. Lấy xem bói của user**

```javascript
db.readings
  .find({
    user_id: ObjectId("507f1f77bcf86cd799439013"),
  })
  .sort({ created_at: -1 });
```

### **4. Thống kê xem bói theo ngày**

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

### **6. Session analytics**

```javascript
db.sessions.aggregate([
  {
    $match: {
      created_at: {
        $gte: new Date("2024-01-01"),
        $lt: new Date("2024-01-02"),
      },
    },
  },
  {
    $group: {
      _id: "$device_info.country",
      sessions: { $sum: 1 },
      avg_duration: { $avg: "$total_duration" },
    },
  },
]);
```

## 📈 **Performance Optimization**

### **1. Index Strategy**

- **Single field indexes**: Cho các trường thường query
- **Compound indexes**: Cho queries phức tạp
- **Text indexes**: Cho tìm kiếm full-text
- **TTL indexes**: Cho dữ liệu tạm thời

### **2. Query Optimization**

```javascript
// Sử dụng projection để giảm data transfer
db.readings.find({}, { question: 1, created_at: 1 });

// Sử dụng limit để giảm memory usage
db.readings.find().limit(100);

// Sử dụng aggregation cho complex queries
db.readings.aggregate([
  { $match: { user_rating: { $gte: 4 } } },
  { $group: { _id: "$reading_type", count: { $sum: 1 } } },
]);
```

### **3. Data Modeling**

- **Embedded documents**: Cho dữ liệu ít thay đổi
- **Referenced documents**: Cho dữ liệu thường xuyên thay đổi
- **Denormalization**: Cho queries phức tạp

## 🔒 **Security**

### **1. Access Control**

```javascript
// Tạo user với limited permissions
db.createUser({
  user: "tarot_app",
  pwd: "secure_password",
  roles: [{ role: "readWrite", db: "tarot_system" }],
});
```

### **2. Data Validation**

```javascript
// Schema validation
db.runCommand({
  collMod: "readings",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["question", "reading_type"],
      properties: {
        question: { bsonType: "string", minLength: 1 },
        reading_type: { enum: ["one_card", "three_card", "celtic_cross"] },
      },
    },
  },
});
```

## 📊 **Backup & Recovery**

### **1. Automated Backups**

```bash
# MongoDB Atlas tự động backup
# Hoặc manual backup
mongodump --db tarot_system --out /backup/
```

### **2. Data Export**

```bash
# Export collections
mongoexport --db tarot_system --collection tarot_cards --out tarot_cards.json
mongoexport --db tarot_system --collection readings --out readings.json
```

## 🔧 **Maintenance**

### **1. Index Maintenance**

```javascript
// Rebuild indexes
db.tarot_cards.reIndex();

// Check index usage
db.readings.getIndexes();
```

### **2. Data Cleanup**

```javascript
// Xóa sessions expired
db.sessions.deleteMany({
  expires_at: { $lt: new Date() },
});

// Archive old analytics
db.analytics.deleteMany({
  date: { $lt: new Date("2023-01-01") },
});
```

## 📞 **Monitoring**

### **1. Database Metrics**

- **Connection count**: Số lượng connections
- **Query performance**: Thời gian thực thi queries
- **Index usage**: Sử dụng indexes
- **Storage usage**: Dung lượng database

### **2. Application Metrics**

- **Error rate**: Tỷ lệ lỗi
- **Response time**: Thời gian phản hồi
- **Throughput**: Số requests/giây
- **User engagement**: Thời gian sử dụng

## 🚀 **Scaling**

### **1. Horizontal Scaling**

- **Sharding**: Phân chia dữ liệu theo key
- **Replica sets**: Backup và read scaling
- **Load balancing**: Phân tải requests

### **2. Vertical Scaling**

- **Memory**: Tăng RAM cho cache
- **CPU**: Tăng processing power
- **Storage**: Tăng dung lượng disk

## 📚 **Resources**

- [MongoDB Documentation](https://docs.mongodb.com)
- [MongoDB Atlas](https://cloud.mongodb.com)
- [MongoDB Compass](https://www.mongodb.com/products/compass)
- [MongoDB University](https://university.mongodb.com)


