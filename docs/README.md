# 📚 Documentation Index

## 🎯 **Tổng quan**

Chào mừng bạn đến với documentation của **Black Luna Tarot** - Hệ thống xem bói Tarot AI hoàn toàn miễn phí!

## 📖 **Tài liệu chính**

### **🚀 [Quick Start Guide](./QUICKSTART.md)**

- Cài đặt nhanh trong 5 phút
- Hướng dẫn sử dụng cơ bản
- Troubleshooting thường gặp
- **Bắt đầu từ đây nếu bạn mới!**

### **📚 [API Documentation](./API.md)**

- Tất cả API endpoints
- Request/Response examples
- Error handling
- Testing với Swagger UI

### **🗄️ [Database Schema](./DATABASE.md)**

- MongoDB collections design
- Indexes & performance
- Query examples
- Backup & recovery

### **🚀 [Deployment Guide](./DEPLOYMENT.md)**

- Deploy lên Render + Vercel
- MongoDB Atlas setup
- Environment configuration
- Monitoring & maintenance

## 🎴 **Tính năng hệ thống**

### **🤖 AI Integration**

- **Ollama Local**: Qwen2 7B (mặc định), Llama 3, Mistral
- **Groq API**: Fast inference (fallback)
- **Streaming**: Hỗ trợ streaming response real-time
- **Prompt Engineering**: Optimized cho tarot readings tiếng Việt

### **🎴 Tarot Cards**

- **78 lá bài**: Major & Minor Arcana
- **Đa ngôn ngữ**: Tiếng Việt + English
- **Chi tiết**: Meanings, keywords, associations
- **Hình ảnh**: Phục vụ qua API endpoint

### **📊 System Monitoring**

- **Health checks**: Full & simple endpoints
- **Connection status**: MongoDB & Ollama
- **Structured logging**: JSON format với structlog
- **Rate limiting**: Per IP

### **🔒 Security**

- **Session-based**: Anonymous users
- **Rate limiting**: Per minute & per hour
- **Security headers**: Middleware tích hợp
- **CORS**: Configured domains
- **Input validation**: Pydantic models

## 🏗️ **Kiến trúc hệ thống**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│ (Vite + React)  │◄──►│   (FastAPI)     │◄──►│  (MongoDB)      │
│                 │    │                 │    │                 │
│ • React 19      │    │ • Python 3.11   │    │ • Atlas Cloud   │
│ • TypeScript    │    │ • Async/Await   │    │ • Collections   │
│ • Tailwind CSS  │    │ • Pydantic      │    │ • Indexes       │
│ • React Router  │    │ • Motor         │    │ • Aggregation   │
│ • TanStack Query│    │ • structlog     │    │                 │
│ • Framer Motion │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Library    │    │   AI Service    │    │   Monitoring    │
│                 │    │                 │    │                 │
│ • Shadcn/UI     │    │ • Ollama Local  │    │ • Health Checks │
│ • Radix UI      │    │ • Groq API      │    │ • Connection    │
│ • Lucide Icons  │    │ • Streaming     │    │   Status        │
│                 │    │ • Training Data │    │ • Structured    │
│                 │    │                 │    │   Logs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 **Development Workflow**

### **Local Development**

```bash
# 1. Clone repository
git clone https://github.com/xrl111/Black-Luna-Tarot.git

# 2. Setup environment
cd Black-Luna-Tarot
cp backend/.env.example backend/.env
# Edit .env with your settings

# 3. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Run development servers
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Ollama (optional)
ollama serve
```

### **Truy cập ứng dụng**

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### **Code Quality**

```bash
# Backend linting
cd backend && black . && isort . && flake8 .

# Frontend linting
cd frontend && npm run lint

# Frontend type checking
cd frontend && tsc -b
```

## 🚀 **API Endpoints Overview**

| Group | Prefix | Chức năng |
|-------|--------|-----------|
| **Tarot Cards** | `/api/v1/tarot-cards` | CRUD, search, filter, images |
| **Readings** | `/api/v1/readings` | Tạo, xem, cập nhật readings |
| **AI Service** | `/api/v1/ai` | Generate & stream AI readings |
| **System** | `/api/v1/system` | Health checks, connection status |

## 🚀 **Deployment Options**

### **Free Tier (0 đồng)**

- **Backend**: Render.com (750h/month)
- **Frontend**: Vercel (100GB bandwidth)
- **Database**: MongoDB Atlas (512MB)
- **AI**: Ollama local hoặc Groq API

## 📈 **Scaling Strategy**

### **Phase 1: MVP (Hiện tại)**

- Single server deployment
- Ollama local AI
- Essential features only

### **Phase 2: Growth**

- User authentication
- Advanced AI models
- Analytics dashboard

### **Phase 3: Enterprise**

- Microservices architecture
- Multi-region deployment
- Custom integrations

## 🎉 **Getting Started**

### **For Users**

1. 📖 Read [Quick Start Guide](./QUICKSTART.md)
2. 🚀 Deploy your instance
3. 🎴 Start using the system

### **For Developers**

1. 📚 Read [API Documentation](./API.md)
2. 🗄️ Understand [Database Schema](./DATABASE.md)
3. 🔧 Set up development environment
4. 🚀 Deploy to production via [Deployment Guide](./DEPLOYMENT.md)

---

**🎯 Ready to start your tarot AI journey? Choose your path above!**
