# 🎯 Tarot System - Custom Middleware
"""
Custom middleware for logging, rate limiting, and request processing
"""

import time
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import RateLimitException

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start time
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_length=request.headers.get("content-length")
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=round(process_time, 4),
                content_length=response.headers.get("content-length")
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=round(process_time, 4),
                exc_info=True
            )
            
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > minute_ago
            ]
        else:
            self.requests[client_ip] = []
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                requests_count=len(self.requests[client_ip])
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "details": {
                        "limit": self.requests_per_minute,
                        "window": "1 minute"
                    }
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.requests[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(int(minute_ago + 60))
        
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Basic CSP (adjust if you use external CDNs)
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
        )
        
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add CORS headers
        origin = request.headers.get("origin")
        if origin in settings.ALLOWED_HOSTS or "*" in settings.ALLOWED_HOSTS:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

class CacheControlMiddleware(BaseHTTPMiddleware):
    """Set Cache-Control headers for selected routes."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if not settings.ENABLE_CACHE_HEADERS:
            return response

        path = request.url.path
        # Images served from backend
        if path.startswith("/api/v1/tarot-cards/image/"):
            response.headers["Cache-Control"] = settings.IMAGE_CACHE_CONTROL
        # Default for API
        elif path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", settings.API_CACHE_CONTROL_DEFAULT)

        return response

# Middleware factory
def create_middleware_stack():
    """
    Create middleware stack for the application
    """
    return [
        RequestLoggingMiddleware,
        SecurityMiddleware,
        CORSMiddleware,
        RateLimitMiddleware,
        CacheControlMiddleware,
    ]
