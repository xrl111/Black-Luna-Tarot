#  Deployment Guide

##  **Tổng quan**

Hướng dẫn deploy Black Luna Tarot lên các nền tảng miễn phí:

- **Backend**: Render.com (750 giờ/tháng miễn phí)
- **Frontend**: Vercel (100GB bandwidth/tháng miễn phí)
- **Database**: MongoDB Atlas (512MB storage miễn phí)
- **AI**: Ollama local hoặc Groq API (fallback)

##  **Prerequisites**

### **1. Tài khoản cần thiết**

- [GitHub](https://github.com) — Lưu trữ code
- [Render](https://render.com) — Host backend
- [Vercel](https://vercel.com) — Host frontend
- [MongoDB Atlas](https://cloud.mongodb.com) — Database
- [Groq](https://console.groq.com) — AI API (optional, fallback)

### **2. Tools cần thiết**

- Git
- Node.js 18+
- Python 3.11+

---

##  **Database Setup**

### **1. MongoDB Atlas**

#### **Tạo cluster miễn phí**

1. Truy cập [MongoDB Atlas](https://cloud.mongodb.com)
2. Đăng ký tài khoản miễn phí
3. Tạo project mới
4. Chọn "Build a Database"
5. Chọn "FREE" tier (M0)
6. Chọn cloud provider và region
7. Click "Create"

#### **Cấu hình Network Access**

1. Vào "Network Access"
2. Click "Add IP Address"
3. Chọn "Allow Access from Anywhere" (0.0.0.0/0)
4. Click "Confirm"

#### **Tạo Database User**

1. Vào "Database Access"
2. Click "Add New Database User"
3. Username: `tarot_app`
4. Password: Tạo password mạnh
5. Role: "Read and write to any database"
6. Click "Add User"

#### **Lấy Connection String**

1. Vào "Database" → "Connect"
2. Chọn "Connect your application"
3. Copy connection string:

```
mongodb+srv://tarot_app:<password>@cluster0.xxxxx.mongodb.net/tarot_system?retryWrites=true&w=majority
```

### **2. Seed Database**

```bash
cd backend
python -c "
import asyncio
from app.database.seed_data import seed_database
asyncio.run(seed_database())
"
```

---

##  **Backend Deployment (Render)**

### **1. Chuẩn bị code**

#### **Tạo file `render.yaml`** (nếu chưa có)

```yaml
services:
  - type: web
    name: black-luna-tarot-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    rootDir: backend
    envVars:
      - key: MONGODB_URI
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: GROQ_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
```

### **2. Deploy lên Render**

#### **Connect GitHub**

1. Truy cập [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect GitHub repository
4. Chọn repository `Black-Luna-Tarot`

#### **Cấu hình service**

- **Name**: `black-luna-tarot-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `backend`

#### **Environment Variables**

```bash
MONGODB_URI=mongodb+srv://tarot_app:<password>@cluster0.xxxxx.mongodb.net/tarot_system?retryWrites=true&w=majority
SECRET_KEY=your-super-secret-key-for-production-at-least-32-chars
ENVIRONMENT=production
GROQ_API_KEY=your-groq-api-key       # Optional fallback
OLLAMA_URL=http://localhost:11434      # Hoặc remote Ollama URL
OLLAMA_MODEL=qwen2.5:1.5b
SHOW_DOCS_IN_PROD=true                # Bật Swagger docs
```

#### **Deploy**

1. Click "Create Web Service"
2. Chờ build và deploy hoàn tất
3. Lưu URL: `https://your-backend.onrender.com`

### **3. Test Backend**

```bash
# Health check
curl https://your-backend.onrender.com/health

# API Documentation
# Swagger UI: https://your-backend.onrender.com/docs
# ReDoc: https://your-backend.onrender.com/redoc
```

---

##  **Frontend Deployment (Vercel)**

### **1. Chuẩn bị code**

Frontend sử dụng **Vite + React 19** (SPA), cần cấu hình Vercel cho static site.

#### **Tạo file `vercel.json`** trong `frontend/`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

> **Lưu ý:** `rewrites` cần thiết cho SPA routing — mọi path đều fallback về `index.html` để React Router xử lý.

### **2. Deploy lên Vercel**

#### **Connect GitHub**

1. Truy cập [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import GitHub repository
4. Chọn repository `Black-Luna-Tarot`

#### **Cấu hình project**

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

#### **Environment Variables**

```bash
VITE_API_ORIGIN=https://your-backend.onrender.com
```

#### **Deploy**

1. Click "Deploy"
2. Chờ build và deploy hoàn tất
3. Lưu URL: `https://your-frontend.vercel.app`

### **3. Custom Domain (Optional)**

1. Vào project settings → "Domains"
2. Thêm custom domain
3. Cấu hình DNS records theo hướng dẫn Vercel

---

##  **AI Service Setup**

### **Option 1: Ollama Local (Development)**

```bash
# Cài đặt Ollama
# Windows
irm https://ollama.com/install.ps1 | iex
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model mặc định
ollama pull qwen2.5:1.5b

# Chạy Ollama
ollama serve
```

Backend config:
```bash
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b
```

### **Option 2: Groq API (Production fallback)**

1. Đăng ký tại [Groq Console](https://console.groq.com)
2. Lấy API key
3. Cấu hình backend:

```bash
GROQ_API_KEY=your-groq-api-key
```

---

##  **Security Configuration**

### **1. Environment Variables**

#### **Backend (Production)**

```bash
MONGODB_URI=mongodb+srv://...
SECRET_KEY=your-super-secret-key-32-chars-minimum
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend.vercel.app"]
TRUSTED_HOSTS=["your-backend.onrender.com"]
ENABLE_RATE_LIMITING=true
ENABLE_SECURITY_HEADERS=true
```

#### **Frontend (Production)**

```bash
VITE_API_ORIGIN=https://your-backend.onrender.com
```

### **2. CORS Configuration**

CORS origins được cấu hình thông qua `CORS_ORIGINS` env var. Trong production, chỉ cho phép domains cụ thể:

```bash
CORS_ORIGINS=["https://your-frontend.vercel.app","https://your-custom-domain.com"]
```

### **3. Rate Limiting**

```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
ENABLE_RATE_LIMITING=true
```

---

##  **Monitoring & Analytics**

### **1. Health Checks**

```bash
# Full health check (kiểm tra MongoDB + Ollama)
curl https://your-backend.onrender.com/health

# Simple health check (không kiểm tra external services)
curl https://your-backend.onrender.com/health/simple

# Chi tiết system connections
curl https://your-backend.onrender.com/api/v1/system/connections

# Force refresh connections
curl -X POST https://your-backend.onrender.com/api/v1/system/connections/refresh
```

### **2. Logs**

- **Render**: Dashboard → Service → Logs (backend sử dụng structlog JSON)
- **Vercel**: Dashboard → Project → Deployments → Logs

### **3. Database Monitoring**

MongoDB Atlas Dashboard:
- Connection count
- Query performance
- Storage usage
- Index usage

---

##  **CI/CD Pipeline**

### **Auto-deployment**

Cả Render và Vercel hỗ trợ auto-deploy khi push to `main` branch:

- **Render**: Tự động build & deploy backend
- **Vercel**: Tự động build & deploy frontend
- Preview deployments cho pull requests

### **GitHub Actions** (Optional)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python -m pytest

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: "18"
      - name: Install and build
        run: |
          cd frontend
          npm install
          npm run build
```

---

##  **Maintenance**

### **Dependencies**

```bash
# Backend
cd backend
pip list --outdated
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm outdated
npm update
```

### **Backup Strategy**

- MongoDB Atlas: Automated backups (free tier)
- Code: GitHub repository + tagged releases

---

##  **Cost Optimization**

### **Free Tier Limits**

| Service | Free Tier |
|---------|-----------|
| **Render** | 750 hours/month |
| **Vercel** | 100GB bandwidth/month |
| **MongoDB Atlas** | 512MB storage |
| **Groq** | Limited requests/month |

### **Tips**

- Sử dụng Ollama local cho development (0 cost)
- Monitor usage regularly ở mỗi service dashboard
- Implement caching cho AI responses để giảm API calls

---

##  **Deployment Checklist**

- [ ] MongoDB Atlas cluster created
- [ ] Database seeded with tarot cards
- [ ] Backend deployed to Render
- [ ] Backend env vars configured (MONGODB_URI, SECRET_KEY, ENVIRONMENT=production)
- [ ] Frontend deployed to Vercel
- [ ] Frontend env var configured (VITE_API_ORIGIN)
- [ ] CORS settings updated for production domains
- [ ] Health checks passing (`/health`)
- [ ] API documentation accessible (`/docs`)
- [ ] AI service connected (Ollama hoặc Groq)
- [ ] Custom domain configured (optional)

** Your Black Luna Tarot system is now live!**
