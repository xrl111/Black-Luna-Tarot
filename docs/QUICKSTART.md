# ⚡ Quick Start Guide

## 🎯 **Bắt đầu nhanh trong 5 phút**

Hướng dẫn cài đặt và chạy Black Luna Tarot trên máy local của bạn.

## 📋 **Yêu cầu hệ thống**

- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.11+
- **Node.js**: 18+
- **RAM**: Tối thiểu 4GB (8GB khuyến nghị cho Ollama)
- **Storage**: 2GB trống

## 🚀 **Cài đặt nhanh**

### **Bước 1: Clone dự án**

```bash
git clone https://github.com/xrl111/Black-Luna-Tarot.git
cd Black-Luna-Tarot
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
# Chỉnh sửa .env với thông tin MongoDB và Ollama

# Frontend (nếu cần thay đổi API origin)
cd ../frontend
# Tạo file .env với nội dung:
# VITE_API_ORIGIN=http://localhost:8000
```

### **Bước 5: Cài đặt Ollama (AI local)**

```bash
# Windows (PowerShell)
irm https://ollama.com/install.ps1 | iex

# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Tải model mặc định
ollama pull qwen2.5:1.5b

# Hoặc sử dụng model khác
ollama pull llama3
ollama pull mistral
```

### **Bước 6: Chạy dự án**

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Frontend
cd frontend
npm run dev
```

## 🌐 **Truy cập ứng dụng**

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Health Check (Simple)**: http://localhost:8000/health/simple

## 🎴 **Sử dụng lần đầu**

### **1. Xem bói cơ bản**

1. Mở http://localhost:5173
2. Chọn loại xem bói
3. Nhập câu hỏi: "Tôi có nên thay đổi công việc không?"
4. Nhấn "Xem bói"
5. Đọc kết quả AI phân tích

### **2. Khám phá bài Tarot**

1. Vào trang "Cards" (`/cards`)
2. Tìm hiểu ý nghĩa từng lá bài
3. Lọc theo suit: Wands, Cups, Swords, Pentacles, Major
4. Xem chi tiết lá bài (`/cards/:id`)

### **3. Trang Giới thiệu**

1. Vào trang "About" (`/about`)
2. Đọc hướng dẫn chi tiết về hệ thống

## 🔧 **Cấu hình nâng cao**

### **Database Options**

#### **Option 1: MongoDB Atlas (Khuyến nghị)**

1. Tạo tài khoản tại [MongoDB Atlas](https://cloud.mongodb.com)
2. Tạo cluster miễn phí (M0)
3. Lấy connection string
4. Cập nhật `MONGODB_URI` trong `backend/.env`

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

#### **Option 1: Ollama Local (Khuyến nghị)**

```bash
# Cài đặt Ollama (xem Bước 5 ở trên)

# Model mặc định (cấu hình trong backend/.env)
OLLAMA_MODEL=qwen2.5:1.5b

# Các model khác có thể sử dụng
ollama pull llama3
ollama pull mistral
```

#### **Option 2: Groq API (Fallback)**

1. Đăng ký tại [Groq Console](https://console.groq.com)
2. Lấy API key
3. Cập nhật `GROQ_API_KEY` trong `backend/.env`

### **Backend Environment Variables**

Các biến môi trường quan trọng trong `backend/.env`:

```bash
# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=tarot_system

# AI
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_TIMEOUT=30
GROQ_API_KEY=           # Optional fallback

# Security
SECRET_KEY=your-secret-key-at-least-32-characters
ENVIRONMENT=development

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## 🧪 **Test nhanh**

### **Test Backend**

```bash
# Health check
curl http://localhost:8000/health

# Health check đơn giản
curl http://localhost:8000/health/simple

# Kiểm tra connections (MongoDB + Ollama)
curl http://localhost:8000/api/v1/system/connections

# Lấy danh sách bài Tarot
curl http://localhost:8000/api/v1/tarot-cards

# Lấy bài Tarot theo suit
curl http://localhost:8000/api/v1/tarot-cards/suit/major

# Lấy bài ngẫu nhiên
curl http://localhost:8000/api/v1/tarot-cards/random/3

# Tạo AI reading
curl -X POST http://localhost:8000/api/v1/ai/generate-reading \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test question",
    "cards": [{"name": "The Fool", "name_vi": "Kẻ Ngốc"}],
    "reading_type": "general"
  }'
```

### **Test Frontend**

1. Mở http://localhost:5173
2. Kiểm tra trang Home (`/`)
3. Kiểm tra trang Cards (`/cards`)
4. Kiểm tra trang Reading (`/reading`)
5. Kiểm tra trang About (`/about`)
6. Kiểm tra responsive trên mobile (F12 → Device toolbar)

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

# Kiểm tra connection qua API
curl http://localhost:8000/api/v1/system/connections/mongodb
```

#### **4. Ollama không chạy**

```bash
# Kiểm tra Ollama
ollama list

# Restart Ollama
ollama serve

# Kiểm tra connection qua API
curl http://localhost:8000/api/v1/system/connections/ollama

# Test model
ollama run qwen2.5:1.5b "Hello, world!"
```

### **Logs và Debug**

#### **Backend Logs**

```bash
# Chạy với debug mode
python -m uvicorn app.main:app --reload --log-level debug

# Backend sử dụng structlog với JSON format
# Logs hiển thị trực tiếp trong console
```

#### **Frontend Logs**

```bash
# Chạy Vite dev server
npm run dev

# Xem console logs trong browser
F12 → Console
```

## 📊 **Performance Tips**

### **Backend Optimization**

```bash
# Sử dụng production server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Frontend Optimization**

```bash
# Build production
npm run build

# Preview production build
npm run preview
```

## 🔒 **Security Checklist**

- [ ] Đổi `SECRET_KEY` mặc định
- [ ] Cấu hình CORS đúng domain (trong `backend/app/core/config.py`)
- [ ] Bật rate limiting (`ENABLE_RATE_LIMITING=true`)
- [ ] Sử dụng HTTPS (production)
- [ ] Set `ENVIRONMENT=production` khi deploy

## 📚 **Tài liệu tham khảo**

- [API Documentation](./API.md)
- [Database Schema](./DATABASE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Vite Docs](https://vitejs.dev)
- [React Docs](https://react.dev)
- [MongoDB Docs](https://docs.mongodb.com)
- [Ollama Docs](https://ollama.ai)

---

**🎉 Chúc mừng! Bạn đã sẵn sàng sử dụng Black Luna Tarot!**
