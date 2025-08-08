# 🎯 Ollama Setup Guide for Tarot System

## 📋 Overview

Ollama là một platform để chạy Large Language Models (LLMs) locally trên máy của bạn. Đây là giải pháp AI cho hệ thống Tarot của chúng ta.

## 🚀 Quick Setup

### Option 1: Automatic Setup (Recommended)

```bash
# Chạy script tự động
python setup_ollama.py
```

### Option 2: Manual Setup

#### Bước 1: Cài đặt Ollama

1. **Windows**:

   - Truy cập: https://ollama.ai/download
   - Tải file `.msi` cho Windows
   - Chạy installer

2. **macOS**:

   ```bash
   brew install ollama
   ```

3. **Linux**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

#### Bước 2: Khởi động Ollama

```bash
# Khởi động service
ollama serve
```

#### Bước 3: Download Model

```bash
# Download model Llama2 (recommended)
ollama pull llama2

# Hoặc model nhỏ hơn
ollama pull llama2:7b
```

#### Bước 4: Test Model

```bash
# Test với câu hỏi đơn giản
ollama run llama2 "Hello, tell me about tarot cards"
```

## 🔧 Configuration

### File `.env` Configuration

```env
# AI Services
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=30
```

### Python Integration

```python
import requests

def ask_ollama(prompt: str, model: str = "llama2"):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)
    return response.json()["response"]
```

## 📊 Available Models

| Model        | Size   | Speed  | Quality      | Recommended |
| ------------ | ------ | ------ | ------------ | ----------- |
| `llama2`     | ~3.8GB | Medium | Good         | ✅ Yes      |
| `llama2:7b`  | ~3.8GB | Fast   | Good         | ✅ Yes      |
| `llama2:13b` | ~7.3GB | Slow   | Better       | ❌ No       |
| `mistral`    | ~4.1GB | Fast   | Good         | ✅ Yes      |
| `codellama`  | ~3.8GB | Medium | Code-focused | ❌ No       |

## 🧪 Testing

### Test Connection

```bash
# Kiểm tra Ollama có chạy không
curl http://localhost:11434/api/tags
```

### Test Model

```bash
# Test với prompt tarot
ollama run llama2 "Give me a brief tarot reading for today"
```

### Test Python Integration

```python
# Test script
python -c "
import requests
response = requests.get('http://localhost:11434/api/tags')
print('Ollama Status:', response.status_code)
"
```

## 🔍 Troubleshooting

### Problem: Ollama không khởi động

```bash
# Kiểm tra process
tasklist | findstr ollama

# Restart service
ollama serve
```

### Problem: Model download failed

```bash
# Clear cache
ollama rm llama2

# Download lại
ollama pull llama2
```

### Problem: Connection timeout

```bash
# Kiểm tra port
netstat -an | findstr 11434

# Restart service
ollama serve
```

## 📈 Performance Tips

### 1. Model Selection

- **Development**: `llama2:7b` (fast)
- **Production**: `llama2` (balanced)
- **High Quality**: `llama2:13b` (slow)

### 2. System Requirements

- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: 10GB+ free space
- **CPU**: Multi-core recommended
- **GPU**: Optional, but speeds up inference

### 3. Optimization

```bash
# Set environment variables
export OLLAMA_HOST=0.0.0.0
export OLLAMA_ORIGINS=*

# Run with specific settings
ollama run llama2 --numa --num-threads 4
```

## 🔗 Integration with Tarot System

### Backend Integration

```python
# app/services/ai_service.py
from app.core.config import settings
import requests

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL

    async def generate_tarot_reading(self, cards: list, question: str):
        prompt = f"""
        You are a professional tarot reader.
        Cards drawn: {', '.join(cards)}
        Question: {question}

        Please provide a detailed, insightful tarot reading.
        """

        return await self._call_ollama(prompt)
```

### API Endpoint

```python
# app/api/v1/endpoints/ai_service.py
@router.post("/generate-reading")
async def generate_reading(
    request: TarotReadingRequest,
    ai_service: OllamaService = Depends()
):
    reading = await ai_service.generate_tarot_reading(
        cards=request.cards,
        question=request.question
    )
    return {"reading": reading}
```

## 📚 Resources

- **Official Docs**: https://ollama.ai/docs
- **Model Library**: https://ollama.ai/library
- **API Reference**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Community**: https://github.com/ollama/ollama/discussions

## ✅ Checklist

- [ ] Ollama installed
- [ ] Service running on port 11434
- [ ] Model downloaded (llama2)
- [ ] Connection test passed
- [ ] Python integration working
- [ ] Tarot system integration ready

## 🎯 Next Steps

1. **Test Ollama**: Chạy test script
2. **Integrate**: Kết nối với Tarot backend
3. **Optimize**: Tune performance settings
4. **Deploy**: Setup cho production

---

**Need Help?** Check the troubleshooting section or create an issue in the project repository.
