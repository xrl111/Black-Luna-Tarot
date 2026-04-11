#  Tarot System - Configuration Management
"""
Application configuration with environment variables support
"""

import os
from typing import List, Optional, Union
from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """
    
    # Application
    PROJECT_NAME: str = "Tarot AI Reading System"
    PROJECT_DESCRIPTION: str = "AI-powered Tarot Reading System Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # CORS & Hosts
    CORS_ORIGINS: List[str] = ["*"]
    TRUSTED_HOSTS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "tarot_system"
    POSTGRES_URI: str = "postgresql+asyncpg://admin:admin123@localhost:5433/app_db"
    
    # Security & Auth
    SECRET_KEY: str = "your-super-secret-key-for-tarot-system-development-only-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    GOOGLE_CLIENT_ID: Optional[str] = None
    
    # Advanced Rate Limiting Limits
    GUEST_DAILY_LIMIT: int = 3
    ACCOUNT_DAILY_LIMIT: int = 20
    
    # AI Services
    OLLAMA_URL: str = "http://localhost:11434"
    # Default to a faster multilingual-friendly model; override in .env as needed
    OLLAMA_MODEL: str = "qwen2.5:1.5b"
    OLLAMA_TIMEOUT: int = 30
    # Generation options (tunable for latency/quality tradeoff)
    OLLAMA_NUM_PREDICT: int = 1500
    OLLAMA_TOP_K: int = 40
    OLLAMA_TOP_P: float = 0.9
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_NUM_CTX: int = 4096
    OLLAMA_KEEP_ALIVE: str = "5m"
    OLLAMA_NUM_THREAD: int | None = None
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 600
    RATE_LIMIT_PER_HOUR: int = 5000
    ENABLE_RATE_LIMITING: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SHOW_DOCS_IN_PROD: bool = False
    ENABLE_SECURITY_HEADERS: bool = True
    ENABLE_CACHE_HEADERS: bool = True
    API_CACHE_CONTROL_DEFAULT: str = "no-store"
    IMAGE_CACHE_CONTROL: str = "public, max-age=604800, immutable"
    
    # Session Management
    SESSION_EXPIRE_DAYS: int = 30
    MAX_SESSIONS_PER_IP: int = 10
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # External Services
    SENTRY_DSN: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Kafka (Big Data Pipeline)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9094"
    KAFKA_TOPIC_READINGS: str = "tarot-events"
    KAFKA_ENABLED: bool = False
    KAFKA_PRODUCER_TIMEOUT: int = 10
    
    # Feature Flags
    ENABLE_USER_REGISTRATION: bool = True
    ENABLE_AI_TRAINING: bool = True
    ENABLE_ANALYTICS: bool = True
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("MONGODB_URI")
    def validate_mongodb_uri(cls, v: str) -> str:
        if not v:
            raise ValueError("MONGODB_URI is required")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if v == "your-secret-key-here":
            raise ValueError("Please set a proper SECRET_KEY")
        if len(v) < 32 and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()

# Global settings instance
settings = get_settings()

# Environment-specific configurations
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ALLOWED_HOSTS: List[str] = ["*"]

class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    CORS_ORIGINS: List[str] = [
        "https://your-domain.com",
        "https://www.your-domain.com"
    ]
    TRUSTED_HOSTS: List[str] = [
        "your-domain.com",
        "www.your-domain.com"
    ]

class TestingSettings(Settings):
    DEBUG: bool = True
    DATABASE_NAME: str = "tarot_system_test"
    MONGODB_URI: str = "mongodb://localhost:27017"
    SECRET_KEY: str = "test-secret-key-for-testing-only"

def get_environment_settings() -> Settings:
    """
    Get environment-specific settings
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Export settings based on environment
settings = get_environment_settings()

