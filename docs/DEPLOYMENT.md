# 🚀 Deployment Guide

## 🎯 **Tổng quan**

Hướng dẫn deploy Tarot AI Reading System lên các nền tảng miễn phí:

- **Backend**: Render.com (750 giờ/tháng miễn phí)
- **Frontend**: Vercel (100GB bandwidth/tháng miễn phí)
- **Database**: MongoDB Atlas (512MB storage miễn phí)
- **AI**: Ollama local hoặc Groq API

## 📋 **Prerequisites**

### **1. Tài khoản cần thiết**

- [GitHub](https://github.com) - Lưu trữ code
- [Render](https://render.com) - Host backend
- [Vercel](https://vercel.com) - Host frontend
- [MongoDB Atlas](https://cloud.mongodb.com) - Database
- [Groq](https://console.groq.com) - AI API (optional)

### **2. Tools cần thiết**

- Git
- Node.js 18+
- Python 3.11+
- MongoDB Compass (optional)

## 🗄️ **Database Setup**

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
mongodb+srv://tarot_app:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### **2. Seed Database**

#### **Chạy script seed data**

```bash
cd backend
python -c "
import asyncio
from app.database.seed_data import seed_database
asyncio.run(seed_database())
"
```

## 🔧 **Backend Deployment (Render)**

### **1. Chuẩn bị code**

#### **Tạo file `render.yaml`**

```yaml
services:
  - type: web
    name: tarot-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URI
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: OLLAMA_URL
        value: https://api.groq.com/openai/v1
      - key: GROQ_API_KEY
        sync: false
```

#### **Tạo file `Dockerfile` (optional)**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **2. Deploy lên Render**

#### **Connect GitHub**

1. Truy cập [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect GitHub repository
4. Chọn repository `tarot-ai-system`

#### **Cấu hình service**

- **Name**: `tarot-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory**: `backend`

#### **Environment Variables**

```
MONGODB_URI=mongodb+srv://tarot_app:<password>@cluster0.xxxxx.mongodb.net/tarot_system?retryWrites=true&w=majority
SECRET_KEY=your-super-secret-key-for-production
OLLAMA_URL=https://api.groq.com/openai/v1
GROQ_API_KEY=your-groq-api-key
ENVIRONMENT=production
```

#### **Deploy**

1. Click "Create Web Service"
2. Chờ build và deploy hoàn tất
3. Lưu URL: `https://tarot-backend.onrender.com`

### **3. Test Backend**

#### **Health Check**

```bash
curl https://tarot-backend.onrender.com/health
```

#### **API Documentation**

- Swagger UI: `https://tarot-backend.onrender.com/docs`
- ReDoc: `https://tarot-backend.onrender.com/redoc`

## 🌐 **Frontend Deployment (Vercel)**

### **1. Chuẩn bị code**

#### **Tạo file `vercel.json`**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://tarot-backend.onrender.com"
  }
}
```

#### **Cập nhật `next.config.js`**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ["example.com", "your-image-domain.com"],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

module.exports = nextConfig;
```

### **2. Deploy lên Vercel**

#### **Connect GitHub**

1. Truy cập [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import GitHub repository
4. Chọn repository `tarot-ai-system`

#### **Cấu hình project**

- **Framework Preset**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

#### **Environment Variables**

```
NEXT_PUBLIC_API_URL=https://tarot-backend.onrender.com
NEXT_PUBLIC_APP_NAME=Tarot AI Reading System
```

#### **Deploy**

1. Click "Deploy"
2. Chờ build và deploy hoàn tất
3. Lưu URL: `https://tarot-frontend.vercel.app`

### **3. Custom Domain (Optional)**

#### **Thêm custom domain**

1. Vào project settings
2. Click "Domains"
3. Thêm domain: `tarot-app.com`
4. Cấu hình DNS records

## 🤖 **AI Service Setup**

### **Option 1: Groq API (Recommended)**

#### **Đăng ký Groq**

1. Truy cập [Groq Console](https://console.groq.com)
2. Đăng ký tài khoản
3. Lấy API key

#### **Cấu hình Backend**

```python
# app/core/config.py
GROQ_API_KEY: str = "your-groq-api-key"
OLLAMA_URL: str = "https://api.groq.com/openai/v1"
OLLAMA_MODEL: str = "llama3-8b-8192"
```

### **Option 2: Ollama Local**

#### **Setup Ollama trên server**

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3

# Run Ollama
ollama serve
```

#### **Cấu hình Backend**

```python
# app/core/config.py
OLLAMA_URL: str = "http://localhost:11434"
OLLAMA_MODEL: str = "llama3"
```

## 🔒 **Security Configuration**

### **1. Environment Variables**

#### **Production Secrets**

```bash
# Backend (.env)
MONGODB_URI=mongodb+srv://...
SECRET_KEY=your-super-secret-key-32-chars-minimum
GROQ_API_KEY=your-groq-api-key
ENVIRONMENT=production

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://tarot-backend.onrender.com
```

### **2. CORS Configuration**

#### **Backend CORS**

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tarot-frontend.vercel.app",
        "https://tarot-app.com",
        "http://localhost:3000"  # Development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **3. Rate Limiting**

#### **Configure rate limits**

```python
# app/core/config.py
RATE_LIMIT_PER_MINUTE: int = 60
RATE_LIMIT_PER_HOUR: int = 1000
```

## 📊 **Monitoring & Analytics**

### **1. Application Monitoring**

#### **Health Checks**

```bash
# Backend health
curl https://tarot-backend.onrender.com/health

# Frontend health
curl https://tarot-frontend.vercel.app/api/health
```

#### **Logs**

- **Render**: Dashboard → Service → Logs
- **Vercel**: Dashboard → Project → Functions → Logs

### **2. Database Monitoring**

#### **MongoDB Atlas**

1. Vào "Metrics" tab
2. Monitor:
   - Connection count
   - Query performance
   - Storage usage
   - Index usage

### **3. Performance Monitoring**

#### **Vercel Analytics**

1. Enable Vercel Analytics
2. Monitor:
   - Page views
   - Performance metrics
   - User behavior

## 🔄 **CI/CD Pipeline**

### **1. GitHub Actions**

#### **Tạo `.github/workflows/deploy.yml`**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
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

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          # Render auto-deploys on push to main
          echo "Backend deployment triggered"

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Vercel
        run: |
          # Vercel auto-deploys on push to main
          echo "Frontend deployment triggered"
```

### **2. Auto-deployment**

#### **Render Auto-deploy**

- Tự động deploy khi push to `main` branch
- Preview deployments cho pull requests

#### **Vercel Auto-deploy**

- Tự động deploy khi push to `main` branch
- Preview deployments cho pull requests

## 🧪 **Testing**

### **1. Backend Tests**

#### **Unit Tests**

```bash
cd backend
python -m pytest tests/
```

#### **API Tests**

```bash
# Test health endpoint
curl https://tarot-backend.onrender.com/health

# Test API endpoints
curl https://tarot-backend.onrender.com/api/v1/tarot-cards
```

### **2. Frontend Tests**

#### **Unit Tests**

```bash
cd frontend
npm test
```

#### **E2E Tests**

```bash
npm run test:e2e
```

## 📈 **Scaling**

### **1. Database Scaling**

#### **MongoDB Atlas**

- Upgrade từ M0 (free) lên M2/M5
- Enable sharding cho large datasets
- Configure read replicas

### **2. Application Scaling**

#### **Render**

- Upgrade từ free tier lên paid plans
- Enable auto-scaling
- Configure load balancing

#### **Vercel**

- Upgrade từ hobby lên pro plan
- Enable edge functions
- Configure CDN

### **3. AI Scaling**

#### **Groq API**

- Monitor usage limits
- Implement caching
- Use multiple models

## 🔧 **Maintenance**

### **1. Regular Updates**

#### **Dependencies**

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

#### **Security Updates**

- Monitor security advisories
- Update dependencies regularly
- Scan for vulnerabilities

### **2. Backup Strategy**

#### **Database Backup**

- MongoDB Atlas automated backups
- Manual exports for critical data
- Test restore procedures

#### **Code Backup**

- GitHub repository
- Multiple branches
- Tagged releases

### **3. Monitoring**

#### **Uptime Monitoring**

- [UptimeRobot](https://uptimerobot.com) - Free uptime monitoring
- [Pingdom](https://pingdom.com) - Performance monitoring

#### **Error Tracking**

- [Sentry](https://sentry.io) - Error tracking
- [LogRocket](https://logrocket.com) - Session replay

## 🚨 **Troubleshooting**

### **1. Common Issues**

#### **Backend Issues**

```bash
# Check logs
curl https://tarot-backend.onrender.com/health

# Check environment variables
echo $MONGODB_URI
echo $SECRET_KEY
```

#### **Frontend Issues**

```bash
# Check build logs
npm run build

# Check environment variables
echo $NEXT_PUBLIC_API_URL
```

#### **Database Issues**

```bash
# Test connection
mongosh "mongodb+srv://..."

# Check indexes
db.tarot_cards.getIndexes()
```

### **2. Performance Issues**

#### **Slow Queries**

```javascript
// Enable query profiling
db.setProfilingLevel(2);

// Check slow queries
db.system.profile.find().sort({ ts: -1 });
```

#### **Memory Issues**

```bash
# Check memory usage
free -h

# Check process memory
ps aux | grep python
```

## 📞 **Support**

### **1. Documentation**

- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com)

### **2. Community**

- [GitHub Issues](https://github.com/your-username/tarot-ai-system/issues)
- [Stack Overflow](https://stackoverflow.com)
- [Discord Community](https://discord.gg/your-community)

### **3. Professional Support**

- [Render Support](https://render.com/support)
- [Vercel Support](https://vercel.com/support)
- [MongoDB Support](https://www.mongodb.com/support)

## 📊 **Cost Optimization**

### **1. Free Tier Limits**

- **Render**: 750 hours/month
- **Vercel**: 100GB bandwidth/month
- **MongoDB Atlas**: 512MB storage
- **Groq**: 1000 requests/month

### **2. Cost Monitoring**

- Monitor usage regularly
- Set up billing alerts
- Optimize resource usage

### **3. Scaling Strategy**

- Start with free tiers
- Upgrade gradually based on usage
- Consider alternative providers

---

## 🎉 **Deployment Checklist**

- [ ] MongoDB Atlas cluster created
- [ ] Database seeded with tarot cards
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Custom domain configured (optional)
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Security measures in place
- [ ] Performance optimized
- [ ] Testing completed
- [ ] Documentation updated

**🎯 Your Tarot AI Reading System is now live!**


