# 🎴 Tarot AI Reading System

> **Hệ thống xem bói Tarot AI hoàn toàn miễn phí - 0 đồng**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://mongodb.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 **Tính năng chính**

- **🤖 AI xem bói thông minh** - Sử dụng Ollama local với Llama 3
- **🎴 78 lá bài Tarot** - Đầy đủ Major & Minor Arcana
- **🌐 Giao diện đẹp** - Next.js 14 với UI/UX hiện đại
- **📱 Responsive** - Hoạt động tốt trên mọi thiết bị
- **🔒 Bảo mật** - Không lưu trữ dữ liệu cá nhân
- **🚀 Miễn phí 100%** - Không tốn chi phí vận hành
- **📊 Analytics** - Thống kê và báo cáo chi tiết
- **🎯 Cá nhân hóa** - Học từ phản hồi người dùng

## 🏗️ **Kiến trúc hệ thống**

```
tarot-system/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration & middleware
│   │   ├── database/       # Models & database
│   │   └── services/       # Business logic
│   └── requirements.txt
├── frontend/               # Next.js Frontend
│   ├── app/               # App Router
│   ├── components/        # React components
│   └── package.json
└── docs/                  # Documentation
```

## 🚀 **Cài đặt nhanh**

### **Yêu cầu hệ thống**

- Python 3.11+
- Node.js 18+
- MongoDB (local hoặc Atlas)
- Ollama (cho AI local)

### **1. Clone dự án**

```bash
git clone https://github.com/your-username/tarot-ai-system.git
cd tarot-ai-system
```

### **2. Cài đặt Backend**

```bash
cd backend
pip install -r requirements.txt
```

### **3. Cài đặt Frontend**

```bash
cd frontend
npm install
```

### **4. Cấu hình môi trường**

```bash
# Backend
cp .env.example .env
# Chỉnh sửa .env với thông tin MongoDB và Ollama

# Frontend
cp .env.example .env.local
# Chỉnh sửa .env.local với URL backend
```

### **5. Chạy dự án**

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Ollama (nếu chưa chạy)
ollama serve
```

## 📖 **API Documentation**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Base URL**: http://localhost:8000/api/v1

### **Endpoints chính**

- `GET /api/v1/tarot-cards` - Lấy danh sách bài Tarot
- `POST /api/v1/readings` - Tạo xem bói mới
- `GET /api/v1/readings/{id}` - Lấy chi tiết xem bói
- `POST /api/v1/sessions` - Tạo session mới

## 🎯 **Cách sử dụng**

### **1. Xem bói cơ bản**

1. Truy cập http://localhost:3000
2. Chọn loại xem bói (1 lá, 3 lá, Celtic Cross)
3. Nhập câu hỏi của bạn
4. Nhấn "Xem bói" và chờ AI phân tích
5. Đọc kết quả và đánh giá

### **2. Xem bói nâng cao**

1. Đăng ký tài khoản (tùy chọn)
2. Lưu lịch sử xem bói
3. Nhận gợi ý cá nhân hóa
4. Tham gia cộng đồng

## 🔧 **Cấu hình nâng cao**

### **Ollama Models**

```bash
# Tải model Llama 3
ollama pull llama3

# Hoặc sử dụng model khác
ollama pull mistral
ollama pull codellama
```

### **MongoDB Atlas**

1. Tạo cluster miễn phí tại [MongoDB Atlas](https://cloud.mongodb.com)
2. Lấy connection string
3. Cập nhật `MONGODB_URI` trong `.env`

### **Deployment**

- **Backend**: Render.com (miễn phí)
- **Frontend**: Vercel (miễn phí)
- **Database**: MongoDB Atlas (miễn phí 512MB)

## 📊 **Tính năng AI**

### **Mô hình sử dụng**

- **Local**: Ollama + Llama 3 (khuyến nghị)
- **Cloud**: Groq API (fallback)
- **Training**: LoRA/QLoRA cho cá nhân hóa

### **Prompt Engineering**

```python
# Ví dụ prompt cho xem bói
prompt = f"""
Bạn là một nhà xem bói Tarot chuyên nghiệp.
Hãy phân tích câu hỏi: "{question}"
Với các lá bài: {cards}
Đưa ra lời khuyên chi tiết và hữu ích.
"""
```

## 🤝 **Đóng góp**

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit thay đổi (`git commit -m 'Add amazing feature'`)
4. Push lên branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📝 **License**

Dự án này được cấp phép theo [MIT License](LICENSE).

## 🙏 **Cảm ơn**

- [Ollama](https://ollama.ai) - AI local
- [FastAPI](https://fastapi.tiangolo.com) - Backend framework
- [Next.js](https://nextjs.org) - Frontend framework
- [MongoDB](https://mongodb.com) - Database
- [Vercel](https://vercel.com) - Hosting

## 📞 **Liên hệ**

- **Email**: your-email@example.com
- **GitHub**: [@your-username](https://github.com/your-username)
- **Website**: https://your-tarot-app.com

---

⭐ **Nếu dự án này hữu ích, hãy cho chúng tôi một ngôi sao!**
