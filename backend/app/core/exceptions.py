# 🎯 Tarot System - Exception Handling
"""
Custom exception classes and handlers
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

logger = structlog.get_logger()

class TarotException(Exception):
    """Base exception for Tarot system"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DatabaseException(TarotException):
    """Database operation exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=500, details=details)

class ValidationException(TarotException):
    """Data validation exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=422, details=details)

class AuthenticationException(TarotException):
    """Authentication exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=401, details=details)

class AuthorizationException(TarotException):
    """Authorization exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=403, details=details)

class NotFoundException(TarotException):
    """Resource not found exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=404, details=details)

class RateLimitException(TarotException):
    """Rate limiting exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=429, details=details)

class AIServiceException(TarotException):
    """AI service exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=503, details=details)

async def tarot_exception_handler(request: Request, exc: TarotException):
    """Handle Tarot system exceptions"""
    logger.error(
        "Tarot exception occurred",
        path=request.url.path,
        method=request.method,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
            "method": request.method
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions"""
    logger.warning(
        "Validation error",
        path=request.url.path,
        method=request.method,
        errors=exc.errors()
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": {
                "errors": exc.errors(),
                "body": exc.body
            },
            "path": str(request.url.path),
            "method": request.method
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        "HTTP exception",
        path=request.url.path,
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "path": str(request.url.path),
            "method": request.method
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=type(exc).__name__,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "path": str(request.url.path),
            "method": request.method
        }
    )

def setup_exception_handlers(app: FastAPI):
    """Setup all exception handlers"""
    
    # Custom exceptions
    app.add_exception_handler(TarotException, tarot_exception_handler)
    app.add_exception_handler(DatabaseException, tarot_exception_handler)
    app.add_exception_handler(ValidationException, tarot_exception_handler)
    app.add_exception_handler(AuthenticationException, tarot_exception_handler)
    app.add_exception_handler(AuthorizationException, tarot_exception_handler)
    app.add_exception_handler(NotFoundException, tarot_exception_handler)
    app.add_exception_handler(RateLimitException, tarot_exception_handler)
    app.add_exception_handler(AIServiceException, tarot_exception_handler)
    
    # FastAPI exceptions
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # General exceptions (must be last)
    app.add_exception_handler(Exception, general_exception_handler)
