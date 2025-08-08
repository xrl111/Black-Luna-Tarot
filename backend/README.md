# 🎯 Tarot System - Backend

## 📋 Overview

FastAPI backend for the Tarot AI Reading System with extensible architecture, MongoDB integration, and AI service capabilities.

## 🏗️ Architecture

### **Extensible Design Pattern**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── middleware.py      # Custom middleware
│   ├── api/                   # API layer
│   │   └── v1/
│   │       ├── api.py         # Main API router
│   │       └── endpoints/     # API endpoints
│   │           ├── tarot_cards.py
│   │           ├── readings.py
│   │           ├── users.py
│   │           ├── sessions.py
│   │           ├── ai_service.py
│   │           └── analytics.py
│   ├── services/              # Business logic layer
│   │   ├── tarot_service.py
│   │   ├── reading_service.py
│   │   ├── user_service.py
│   │   ├── session_service.py
│   │   ├── ai_service.py
│   │   └── analytics_service.py
│   └── database/              # Database models
│       └── models.py
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 1. **Environment Setup**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Environment Variables**

Create `.env` file:

```env
# Application
ENVIRONMENT=development
DEBUG=true

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/tarot_system
DATABASE_NAME=tarot_system

# Security
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# AI Services
OLLAMA_URL=http://localhost:11434
GROQ_API_KEY=your-groq-api-key

# Server
HOST=0.0.0.0
PORT=8000
```

### 3. **Run Application**

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode (docs hidden by default)
ENVIRONMENT=production DEBUG=false uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. **Access API Documentation**

- In development: **Swagger UI** http://localhost:8000/docs, **ReDoc** http://localhost:8000/redoc
- In production, docs are hidden by default. Set `SHOW_DOCS_IN_PROD=true` to expose them.
- **Health Check**: http://localhost:8000/health

## 🏗️ Architecture Principles

### **1. Layered Architecture**

```
┌─────────────────────────────────────┐
│           API Layer                 │  ← FastAPI endpoints
├─────────────────────────────────────┤
│         Service Layer               │  ← Business logic
├─────────────────────────────────────┤
│        Data Access Layer            │  ← MongoDB operations
├─────────────────────────────────────┤
│         Database Layer              │  ← MongoDB
└─────────────────────────────────────┘
```

### **2. Dependency Injection**

```python
# Example: Service injection
@router.get("/tarot-cards")
async def get_tarot_cards(
    service: TarotCardService = Depends(get_tarot_service)
):
    return await service.get_cards()
```

### **3. Extensible Design**

- **Modular Services**: Each domain has its own service
- **Plugin Architecture**: Easy to add new features
- **Configuration Driven**: Environment-based settings
- **Middleware Stack**: Customizable request processing

## 📊 API Endpoints

### **Tarot Cards**

- `GET /api/v1/tarot-cards/` - Get paginated cards
- `GET /api/v1/tarot-cards/{card_id}` - Get specific card
- `GET /api/v1/tarot-cards/suit/{suit}` - Get cards by suit
- `GET /api/v1/tarot-cards/random/{count}` - Get random cards
- `GET /api/v1/tarot-cards/search/{query}` - Search cards

### **Readings**

- `POST /api/v1/readings/` - Create new reading
- `GET /api/v1/readings/{reading_id}` - Get reading
- `PUT /api/v1/readings/{reading_id}` - Update reading

### **Users**

- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user

### **Sessions**

- `POST /api/v1/sessions/` - Create session
- `GET /api/v1/sessions/{session_id}` - Get session

### **AI Service**

- `POST /api/v1/ai/generate-reading` - Generate AI reading
- `POST /api/v1/ai/train-model` - Train AI model

### **Analytics**

- `GET /api/v1/analytics/overview` - Get analytics overview
- `GET /api/v1/analytics/user-engagement` - Get engagement metrics

## 🔧 Configuration

### **Environment-Specific Settings**

```python
# Development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

### **Feature Flags**

```python
# Enable/disable features
ENABLE_USER_REGISTRATION=true
ENABLE_AI_TRAINING=true
ENABLE_ANALYTICS=true
```

## 🔐 Security Features

### **1. Authentication & Authorization**

- JWT token-based authentication
- Role-based access control
- Session management

### **2. Data Protection**

- Input validation with Pydantic
- SQL injection prevention (MongoDB)
- XSS protection headers
- CORS configuration

### **3. Rate Limiting**

- Per-IP rate limiting
- Configurable limits
- Rate limit headers

### **4. Logging & Monitoring**

- Structured logging with structlog
- Request/response logging
- Error tracking
- Performance monitoring

## 🧪 Testing

### **Run Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_tarot_service.py

# Run with verbose output
pytest -v
```

### **Test Structure**

```
tests/
├── conftest.py              # Test configuration
├── test_api/               # API tests
├── test_services/          # Service tests
├── test_database/          # Database tests
└── test_integration/       # Integration tests
```

## 📈 Performance Optimization

### **1. Database Optimization**

- Connection pooling
- Indexed queries
- Aggregation pipelines
- Caching strategies

### **2. API Optimization**

- Async/await patterns
- Response compression
- Pagination
- Caching headers

### **3. Monitoring**

- Request timing
- Database query performance
- Memory usage
- Error rates

## 🚀 Deployment

### **1. Docker Deployment**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **2. Render.com Deployment**

```yaml
# render.yaml
services:
  - type: web
    name: tarot-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URI
        value: mongodb+srv://...
      - key: SECRET_KEY
        generateValue: true
```

### **3. Environment Variables**

```bash
# Production environment variables
ENVIRONMENT=production
MONGODB_URI=mongodb+srv://...
SECRET_KEY=your-production-secret-key
OLLAMA_URL=http://your-ollama-instance:11434
```

## 🔄 Extensibility

### **Adding New Features**

1. **Create Service Layer**

```python
# app/services/new_feature_service.py
class NewFeatureService:
    def __init__(self, collection):
        self.collection = collection

    async def new_method(self):
        # Business logic here
        pass
```

2. **Create API Endpoints**

```python
# app/api/v1/endpoints/new_feature.py
@router.get("/new-feature")
async def get_new_feature():
    # API logic here
    pass
```

3. **Register in Main Router**

```python
# app/api/v1/api.py
api_router.include_router(
    new_feature.router,
    prefix="/new-feature",
    tags=["new-feature"]
)
```

### **Plugin System**

```python
# Example plugin structure
plugins/
├── __init__.py
├── base.py
├── tarot_plugin.py
├── ai_plugin.py
└── analytics_plugin.py
```

## 📚 Documentation

### **API Documentation**

- Auto-generated with OpenAPI/Swagger
- Interactive testing interface
- Request/response examples
- Schema validation

### **Code Documentation**

- Type hints throughout
- Docstrings for all functions
- Architecture diagrams
- Setup guides

## 🤝 Contributing

### **Development Workflow**

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes**
4. **Add tests**
5. **Update documentation**
6. **Submit pull request**

### **Code Standards**

- **Type Hints**: Required for all functions
- **Docstrings**: All public methods
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging with context
- **Testing**: Minimum 80% coverage

## 🐛 Troubleshooting

### **Common Issues**

1. **Database Connection**

```bash
# Check MongoDB connection
python -c "import motor; client = motor.AsyncIOMotorClient('your-uri'); print('Connected')"
```

2. **Environment Variables**

```bash
# Check environment
python -c "from app.core.config import settings; print(settings.MONGODB_URI)"
```

3. **Dependencies**

```bash
# Update dependencies
pip install -r requirements.txt --upgrade
```

## 📞 Support

- **Documentation**: Check `/docs` endpoint
- **Issues**: GitHub issues
- **Discussions**: GitHub discussions
- **Email**: support@tarot-ai.com

---

**Built with ❤️ for the Tarot AI Reading System**
