# ⚡ Quick Start Guide

## 🎯 **Bắt đầu nhanh trong 5 phút**

Hướng dẫn cài đặt và chạy Tarot AI Reading System trên máy local của bạn.

## 📋 **Yêu cầu hệ thống**

- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.11+
- **Node.js**: 18+
- **RAM**: Tối thiểu 4GB (8GB khuyến nghị)
- **Storage**: 2GB trống

## 🚀 **Cài đặt nhanh**

### **Bước 1: Clone dự án**

```bash
git clone https://github.com/your-username/tarot-ai-system.git
cd tarot-ai-system
```

### **Bước 2: Cài đặt Backend**

```bash
cd backend
pip install -r requirements.txt
```

### **Bước 3: Cài đặt Frontend**

```bash
cd ../frontend
npm install
```

### **Bước 4: Cấu hình môi trường**

```bash
# Backend
cd ../backend
cp .env.example .env
# Chỉnh sửa .env với thông tin MongoDB

# Frontend
cd ../frontend
cp .env.example .env.local
# Chỉnh sửa .env.local với URL backend
```

### **Bước 5: Chạy dự án**

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Ollama (nếu sử dụng local AI)
ollama serve
```

## 🌐 **Truy cập ứng dụng**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎴 **Sử dụng lần đầu**

### **1. Xem bói cơ bản**

1. Mở http://localhost:3000
2. Chọn "Xem bói 1 lá"
3. Nhập câu hỏi: "Tôi có nên thay đổi công việc không?"
4. Nhấn "Xem bói"
5. Đọc kết quả và đánh giá

### **2. Xem bói nâng cao**

1. Chọn "Xem bói 3 lá"
2. Chọn spread: "Quá khứ - Hiện tại - Tương lai"
3. Nhập câu hỏi chi tiết
4. Chờ AI phân tích
5. Đọc kết quả chi tiết

### **3. Khám phá bài Tarot**

1. Vào "Thư viện bài Tarot"
2. Tìm hiểu ý nghĩa từng lá bài
3. Xem các spread khác nhau
4. Đọc hướng dẫn xem bói

## 🔧 **Cấu hình nâng cao**

### **Database Options**

#### **Option 1: MongoDB Atlas (Khuyến nghị)**

1. Tạo tài khoản tại [MongoDB Atlas](https://cloud.mongodb.com)
2. Tạo cluster miễn phí
3. Lấy connection string
4. Cập nhật `MONGODB_URI` trong `.env`

#### **Option 2: MongoDB Local**

```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Windows
# Tải MongoDB từ https://www.mongodb.com/try/download/community
```

### **AI Options**

#### **Option 1: Groq API (Khuyến nghị)**

1. Đăng ký tại [Groq Console](https://console.groq.com)
2. Lấy API key
3. Cập nhật `GROQ_API_KEY` trong `.env`

#### **Option 2: Ollama Local**

```bash
# Cài đặt Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Tải model
ollama pull llama3

# Chạy Ollama
ollama serve
```

## 🧪 **Test nhanh**

### **Test Backend**

```bash
# Health check
curl http://localhost:8000/health

# Lấy danh sách bài Tarot
curl http://localhost:8000/api/v1/tarot-cards

# Tạo xem bói test
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test question",
    "reading_type": "one_card",
    "session_id": "test_session"
  }'
```

### **Test Frontend**

1. Mở http://localhost:3000
2. Kiểm tra tất cả trang load đúng
3. Test chức năng xem bói
4. Kiểm tra responsive trên mobile

## 🚨 **Troubleshooting**

### **Lỗi thường gặp**

#### **1. Port đã được sử dụng**

```bash
# Kiểm tra port đang sử dụng
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Kill process
taskkill /PID <process_id>    # Windows
kill <process_id>             # macOS/Linux
```

#### **2. Module không tìm thấy**

```bash
# Cài đặt lại dependencies
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

#### **3. Database connection failed**

```bash
# Kiểm tra MongoDB
mongosh "mongodb://localhost:27017"

# Hoặc test connection string
python -c "
import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient('your-connection-string')
print('Connection successful')
"
```

#### **4. Ollama không chạy**

```bash
# Kiểm tra Ollama
ollama list

# Restart Ollama
ollama serve

# Test model
ollama run llama3 "Hello, world!"
```

### **Logs và Debug**

#### **Backend Logs**

```bash
# Chạy với debug mode
python -m uvicorn app.main:app --reload --log-level debug

# Xem logs chi tiết
tail -f logs/app.log
```

#### **Frontend Logs**

```bash
# Chạy với debug mode
npm run dev -- --debug

# Xem console logs trong browser
F12 → Console
```

## 📊 **Performance Tips**

### **Backend Optimization**

```bash
# Sử dụng production server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Enable caching
pip install redis
```

### **Frontend Optimization**

```bash
# Build production
npm run build
npm start

# Enable compression
npm install compression
```

## 🔒 **Security Checklist**

- [ ] Đổi `SECRET_KEY` mặc định
- [ ] Cấu hình CORS đúng domain
- [ ] Bật rate limiting
- [ ] Validate input data
- [ ] Sử dụng HTTPS (production)

## 📚 **Tài liệu tham khảo**

- [API Documentation](./API.md)
- [Database Schema](./DATABASE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)
- [MongoDB Docs](https://docs.mongodb.com)

## 🆘 **Hỗ trợ**

### **Community Support**

- [GitHub Issues](https://github.com/your-username/tarot-ai-system/issues)
- [Discord Server](https://discord.gg/your-community)
- [Stack Overflow](https://stackoverflow.com)

### **Professional Support**

- Email: support@your-domain.com
- Documentation: https://docs.your-domain.com
- Status Page: https://status.your-domain.com

## 🎉 **Chúc mừng!**

Bạn đã thành công cài đặt và chạy Tarot AI Reading System!

**Bước tiếp theo:**

1. Khám phá các tính năng
2. Tùy chỉnh giao diện
3. Thêm dữ liệu bài Tarot
4. Deploy lên production
5. Chia sẻ với cộng đồng

---

**⭐ Nếu hướng dẫn này hữu ích, hãy cho chúng tôi một ngôi sao trên GitHub!**


