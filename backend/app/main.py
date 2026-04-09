# 🎯 Tarot System - Main Application
"""
FastAPI application entry point with extensible architecture
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
import asyncio
import structlog

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.core.middleware import RequestLoggingMiddleware
from app.core.exceptions import setup_exception_handlers
from app.services.connection_service import log_connection_status, get_health_summary

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🎯 Starting Tarot AI Backend", version=settings.VERSION)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")
    
    # Wait a moment for database to be fully ready
    await asyncio.sleep(0.5)
    
    # Initialize Kafka producer (Big Data pipeline)
    if settings.KAFKA_ENABLED:
        try:
            from app.services.kafka_producer import get_kafka_producer
            kafka_producer = get_kafka_producer()
            await kafka_producer.start()
        except Exception as e:
            logger.warning("⚠️ Kafka producer failed to start (non-blocking)", error=str(e))
    
    # Check and log all service connections
    try:
        connection_summary = await log_connection_status(detailed=True)
        if connection_summary["all_connected"]:
            logger.info("🚀 All services are ready - Application startup complete!")
        else:
            logger.warning("⚠️  Some services are unavailable - Application started with limited functionality")
            logger.info("💡 Check service configurations and ensure MongoDB and Ollama are running")
    except Exception as e:
        logger.error("Failed to check service connections during startup", error=str(e))
    
    yield
    
    # Shutdown
    # Stop Kafka producer
    if settings.KAFKA_ENABLED:
        try:
            from app.services.kafka_producer import get_kafka_producer
            kafka_producer = get_kafka_producer()
            await kafka_producer.stop()
        except Exception as e:
            logger.warning("Error stopping Kafka producer", error=str(e))
    
    logger.info("Shutting down Tarot AI Backend")

def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    docs_url = "/docs" if (settings.DEBUG or settings.SHOW_DOCS_IN_PROD) else None
    redoc_url = "/redoc" if (settings.DEBUG or settings.SHOW_DOCS_IN_PROD) else None

    app = FastAPI(
        title=settings.PROJECT_NAME,
        lifespan=lifespan,
        description="""
        # 🎯 Tarot AI System API
        
        ## Overview
        A comprehensive AI-powered tarot reading system with advanced features for personal growth and spiritual guidance. This system includes a complete 78-card Rider-Waite tarot deck with Vietnamese translations.
        
        ## Endpoints
        - **Tarot Cards**: Danh sách/chi tiết/lọc, và truy xuất ảnh thẻ
        - **AI Readings**: Tạo giải thích bằng AI (có streaming)
        - **Readings**: Lưu và truy vấn các reading đã tạo
        - **System**: Health-check và kiểm tra kết nối dịch vụ
        
        ## Support
        For API support, please contact the development team.
        """,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=docs_url,
        redoc_url=redoc_url,
        # Simplified API tags for the endpoints in use
        openapi_tags=[
            {
                "name": "ai-service", 
                "description": "AI-powered tarot readings (support streaming)",
            },
            {
                "name": "tarot-cards", 
                "description": "Tarot card catalog: list, filter, detail, image",
            },
            {
                "name": "readings", 
                "description": "Lưu và truy vấn các reading đã tạo",
            },
            {
                "name": "system", 
                "description": "Health-check & kết nối dịch vụ",
            },
            {
                "name": "bigdata", 
                "description": "Big Data pipeline: status, stats, dead-letter queue, replay",
            },
        ]
    )



    # Setup Trusted Host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS
    )

    # Optional security & logging middleware (toggle via settings)
    try:
        if settings.ENABLE_SECURITY_HEADERS:
            from app.core.middleware import SecurityMiddleware
            app.add_middleware(SecurityMiddleware)
    except Exception as e:
        logger.warning(f"Failed to add SecurityMiddleware: {e}")

    try:
        if settings.ENABLE_RATE_LIMITING:
            from app.core.middleware import RateLimitMiddleware
            app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
    except Exception as e:
        logger.warning(f"Failed to add RateLimitMiddleware: {e}")

    try:
        if settings.ENABLE_CACHE_HEADERS:
            from app.core.middleware import CacheControlMiddleware
            app.add_middleware(CacheControlMiddleware)
    except Exception as e:
        logger.warning(f"Failed to add CacheControlMiddleware: {e}")

    # Setup exception handlers
    setup_exception_handlers(app)

    # Setup CORS (MUST BE LAST to be outermost middleware and handle CORS for early returns like 429)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

   

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Enhanced health check with service connection status"""
        try:
            health_summary = await get_health_summary()
            return {
                "status": health_summary["status"],
                "version": settings.VERSION,
                "timestamp": time.time(),
                "services": health_summary["services"],
                "summary": health_summary["summary"]
            }
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "error",
                "version": settings.VERSION,
                "timestamp": time.time(),
                "error": str(e)
            }
    
    # Simple health check endpoint
    @app.get("/health/simple")
    async def simple_health_check():
        """Simple health check without external service checks"""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "timestamp": time.time()
        }

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Tarot AI Reading System",
            "version": settings.VERSION,
            "docs": "/docs",
            "health": "/health"
        }

    return app

# Create application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
