#  Tarot System - System Management Endpoints
"""
System management and monitoring endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import structlog

from app.services.connection_service import (
    check_all_connections, 
    log_connection_status,
    get_health_summary,
    connection_service
)

logger = structlog.get_logger()
router = APIRouter()

@router.get("/connections", tags=["system"])
async def check_connections() -> Dict[str, Any]:
    """
    Check all service connections
    
    Returns detailed status for MongoDB and Ollama connections
    """
    try:
        connections = await check_all_connections()
        
        return {
            "status": "success",
            "connections": {
                name: status.to_dict() 
                for name, status in connections.items()
            },
            "summary": {
                "connected": sum(1 for s in connections.values() if s.connected),
                "total": len(connections),
                "all_connected": all(s.connected for s in connections.values())
            }
        }
    except Exception as e:
        logger.error("Failed to check connections", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to check connections: {str(e)}")

@router.get("/connections/mongodb", tags=["system"])
async def check_mongodb_connection() -> Dict[str, Any]:
    """Check MongoDB connection status"""
    try:
        status = await connection_service.check_mongodb_connection()
        return {
            "status": "success",
            "connection": status.to_dict()
        }
    except Exception as e:
        logger.error("Failed to check MongoDB connection", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to check MongoDB connection: {str(e)}")

@router.get("/connections/ollama", tags=["system"])
async def check_ollama_connection() -> Dict[str, Any]:
    """Check Ollama connection status"""
    try:
        status = await connection_service.check_ollama_connection()
        return {
            "status": "success",
            "connection": status.to_dict()
        }
    except Exception as e:
        logger.error("Failed to check Ollama connection", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to check Ollama connection: {str(e)}")

@router.post("/connections/refresh", tags=["system"])
async def refresh_connections() -> Dict[str, Any]:
    """
    Refresh and check all service connections (bypass cache)
    
    Forces a fresh check of all service connections and logs the results
    """
    try:
        # Clear cache and perform fresh checks
        connection_service.connection_cache.clear()
        
        # Log detailed connection status
        summary = await log_connection_status(detailed=True)
        
        return {
            "status": "success",
            "message": "Connection checks completed",
            "summary": summary
        }
    except Exception as e:
        logger.error("Failed to refresh connections", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to refresh connections: {str(e)}")

@router.get("/health/detailed", tags=["system"])
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with comprehensive service information
    """
    try:
        return await get_health_summary()
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
