# 🎴 Black Luna Tarot

> **Hệ thống xem bói Tarot AI hoàn toàn miễn phí - 0 đồng**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF.svg)](https://vitejs.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://mongodb.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local-orange.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 **Tính năng chính**

- **🤖 AI xem bói thông minh** — Sử dụng Ollama local (Qwen2, Llama 3, Mistral)
- **🎴 78 lá bài Tarot** — Đầy đủ Major & Minor Arcana
- **🌐 Giao diện đẹp** — React 19 + TypeScript + Tailwind CSS + Shadcn/UI
- **📱 Responsive** — Hoạt động tốt trên mọi thiết bị
- **⚡ Streaming** — AI response hiển thị real-time
- **🔒 Bảo mật** — Rate limiting, security headers, CORS
- **🚀 Miễn phí 100%** — Không tốn chi phí vận hành

## 🏗️ **Kiến trúc hệ thống**

```
Black-Luna-Tarot/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/  # API endpoints (tarot_cards, readings, ai_service, system)
│   │   ├── core/              # Config, database, middleware, exceptions
│   │   ├── database/          # Pydantic models & seed data
│   │   └── services/          # Business logic (11 service files)
│   └── requirements.txt
├── frontend/               # Vite + React Frontend
│   ├── src/
│   │   ├── pages/           # Page components (Home, Cards, Reading, About)
│   │   ├── components/      # Navbar, SEO, Shadcn/UI
│   │   └── lib/             # API client & utilities
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
git clone https://github.com/xrl111/Black-Luna-Tarot.git
cd Black-Luna-Tarot
```

### **2. Cài đặt Backend**

```bash
cd backend
pip install -r requirements.txt
```

### **3. Cài đặt Frontend**

```bash
cd ../frontend
npm install
```

### **4. Cài đặt Ollama & Model**

```bash
# Windows
irm https://ollama.com/install.ps1 | iex

# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Tải model mặc định
ollama pull qwen2.5:1.5b
```

### **5. Cấu hình môi trường**

```bash
# Backend
cd backend
cp .env.example .env
# Chỉnh sửa .env với thông tin MongoDB và Ollama
```

### **6. Chạy dự án**

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
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 **API Endpoints**

| Group | Prefix | Chức năng |
|-------|--------|-----------|
| **Tarot Cards** | `/api/v1/tarot-cards` | CRUD, search, filter, random, images |
| **Readings** | `/api/v1/readings` | Tạo, xem, cập nhật, xóa readings |
| **AI Service** | `/api/v1/ai` | Generate & stream AI readings |
| **System** | `/api/v1/system` | Health checks, connection status |

## 🔧 **Cấu hình AI**

```bash
# Tải models khác (optional)
ollama pull llama3
ollama pull mistral
```

Model mặc định có thể thay đổi qua `OLLAMA_MODEL` trong `.env`.

## 🚀 **Deployment**

- **Backend**: Render.com (miễn phí)
- **Frontend**: Vercel (miễn phí)
- **Database**: MongoDB Atlas (miễn phí 512MB)

Xem chi tiết tại [Deployment Guide](./docs/DEPLOYMENT.md).

## 📚 **Documentation**

- [Quick Start Guide](./docs/QUICKSTART.md)
- [API Documentation](./docs/API.md)
- [Database Schema](./docs/DATABASE.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 🤝 **Đóng góp**

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit thay đổi (`git commit -m 'feat: add amazing feature'`)
4. Push lên branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📝 **License**

Dự án này được cấp phép theo [MIT License](LICENSE).

## 🙏 **Cảm ơn**

- [Ollama](https://ollama.ai) — AI local
- [FastAPI](https://fastapi.tiangolo.com) — Backend framework
- [React](https://react.dev) — Frontend library
- [Vite](https://vitejs.dev) — Frontend build tool
- [MongoDB](https://mongodb.com) — Database
- [Shadcn/UI](https://ui.shadcn.com) — UI components

---

⭐ **Nếu dự án này hữu ích, hãy cho chúng tôi một ngôi sao!**
