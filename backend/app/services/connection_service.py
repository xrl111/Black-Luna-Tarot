# 🎯 Tarot System - Connection Service
"""
Service for checking connections to external services (MongoDB, Ollama, Kafka)
"""

import asyncio
import time
from typing import Dict, Any, Optional
import structlog
import motor.motor_asyncio
import httpx

from app.core.config import settings
from app.core.database import client, database
from app.services.ollama_service import OllamaService

logger = structlog.get_logger()

class ConnectionStatus:
    """Connection status model"""
    
    def __init__(self, service_name: str, connected: bool, details: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.service_name = service_name
        self.connected = connected
        self.details = details or {}
        self.error = error
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service_name,
            "connected": self.connected,
            "details": self.details,
            "error": self.error,
            "timestamp": self.timestamp,
            "status": "✅ Connected" if self.connected else "❌ Disconnected"
        }

class ConnectionService:
    """
    Service for checking and monitoring external service connections
    """
    
    def __init__(self):
        self.connection_cache: Dict[str, ConnectionStatus] = {}
        self.cache_duration = 30  # seconds
    
    async def check_mongodb_connection(self) -> ConnectionStatus:
        """Check MongoDB connection status"""
        service_name = "MongoDB"
        
        try:
            # Import fresh references each time to avoid stale references
            from app.core.database import client, database
            
            if client is None or database is None:
                # Try to create a fresh connection to test
                try:
                    test_client = motor.motor_asyncio.AsyncIOMotorClient(
                        settings.MONGODB_URI,
                        serverSelectionTimeoutMS=5000,
                        connectTimeoutMS=10000
                    )
                    await test_client.admin.command('ping')
                    test_client.close()  # close() is not async in motor
                    
                    return ConnectionStatus(
                        service_name=service_name,
                        connected=False,
                        error="Database client not initialized but MongoDB is reachable",
                        details={
                            "uri": settings.MONGODB_URI.replace(settings.MONGODB_URI.split('@')[-1].split('/')[0], '***') if '@' in settings.MONGODB_URI else settings.MONGODB_URI,
                            "database": settings.DATABASE_NAME,
                            "note": "MongoDB is running but not properly initialized in application"
                        }
                    )
                except Exception as test_error:
                    return ConnectionStatus(
                        service_name=service_name,
                        connected=False,
                        error=f"Database client not initialized and MongoDB not reachable: {test_error}"
                    )
            
            # Test connection with ping
            start_time = time.time()
            await client.admin.command('ping')
            response_time = (time.time() - start_time) * 1000  # convert to ms
            
            # Get server info
            server_info = await client.admin.command('buildinfo')
            server_status = await client.admin.command('serverStatus')
            
            details = {
                "uri": settings.MONGODB_URI.replace(settings.MONGODB_URI.split('@')[-1].split('/')[0], '***') if '@' in settings.MONGODB_URI else settings.MONGODB_URI,
                "database": settings.DATABASE_NAME,
                "server_version": server_info.get('version', 'Unknown'),
                "response_time_ms": round(response_time, 2),
                "connections": server_status.get('connections', {}),
                "uptime_seconds": server_status.get('uptime', 0)
            }
            
            logger.info("MongoDB connection check successful", **details)
            
            return ConnectionStatus(
                service_name=service_name,
                connected=True,
                details=details
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error("MongoDB connection check failed", error=error_msg)
            
            return ConnectionStatus(
                service_name=service_name,
                connected=False,
                error=error_msg,
                details={
                    "uri": settings.MONGODB_URI.replace(settings.MONGODB_URI.split('@')[-1].split('/')[0], '***') if '@' in settings.MONGODB_URI else settings.MONGODB_URI,
                    "database": settings.DATABASE_NAME
                }
            )
    
    async def check_ollama_connection(self) -> ConnectionStatus:
        """Check Ollama connection status"""
        service_name = "Ollama"
        
        try:
            async with OllamaService() as ollama:
                start_time = time.time()
                is_healthy = await ollama.health_check()
                response_time = (time.time() - start_time) * 1000  # convert to ms
                
                if not is_healthy:
                    return ConnectionStatus(
                        service_name=service_name,
                        connected=False,
                        error="Health check failed",
                        details={
                            "url": settings.OLLAMA_URL,
                            "model": settings.OLLAMA_MODEL,
                            "timeout": settings.OLLAMA_TIMEOUT
                        }
                    )
                
                # Get available models
                models = await ollama.list_models()
                model_names = [model.get('name', 'Unknown') for model in models]
                
                # Check if default model is available
                default_model_available = any(
                    settings.OLLAMA_MODEL in model_name 
                    for model_name in model_names
                )
                
                details = {
                    "url": settings.OLLAMA_URL,
                    "default_model": settings.OLLAMA_MODEL,
                    "default_model_available": default_model_available,
                    "available_models": model_names,
                    "model_count": len(models),
                    "response_time_ms": round(response_time, 2),
                    "timeout": settings.OLLAMA_TIMEOUT
                }
                
                logger.info("Ollama connection check successful", **details)
                
                return ConnectionStatus(
                    service_name=service_name,
                    connected=True,
                    details=details
                )
                
        except Exception as e:
            error_msg = str(e)
            logger.error("Ollama connection check failed", error=error_msg)
            
            return ConnectionStatus(
                service_name=service_name,
                connected=False,
                error=error_msg,
                details={
                    "url": settings.OLLAMA_URL,
                    "model": settings.OLLAMA_MODEL,
                    "timeout": settings.OLLAMA_TIMEOUT
                }
            )

    async def check_kafka_connection(self) -> ConnectionStatus:
        """Check Kafka broker connectivity"""
        service_name = "Kafka"
        
        if not settings.KAFKA_ENABLED:
            return ConnectionStatus(
                service_name=service_name,
                connected=True,
                details={"status": "disabled", "note": "KAFKA_ENABLED=False"}
            )
        
        try:
            from app.services.kafka_producer import get_kafka_producer
            producer = get_kafka_producer()
            
            if producer._is_running:
                metrics = producer.get_metrics()
                return ConnectionStatus(
                    service_name=service_name,
                    connected=True,
                    details={
                        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                        "topic": settings.KAFKA_TOPIC_READINGS,
                        "events_sent": metrics.get("events_sent", 0),
                        "events_failed": metrics.get("events_failed", 0),
                        "success_rate": metrics.get("success_rate", 0),
                        "avg_latency_ms": metrics.get("avg_latency_ms", 0),
                    }
                )
            else:
                return ConnectionStatus(
                    service_name=service_name,
                    connected=False,
                    error="Producer not running",
                    details={
                        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                        "topic": settings.KAFKA_TOPIC_READINGS,
                    }
                )
        except Exception as e:
            error_msg = str(e)
            logger.error("Kafka connection check failed", error=error_msg)
            return ConnectionStatus(
                service_name=service_name,
                connected=False,
                error=error_msg,
                details={
                    "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                }
            )
    
    async def check_all_connections(self, use_cache: bool = True) -> Dict[str, ConnectionStatus]:
        """Check all service connections"""
        
        current_time = time.time()
        
        # Check cache if enabled
        if use_cache:
            cached_results = {}
            for service, status in self.connection_cache.items():
                if current_time - status.timestamp < self.cache_duration:
                    cached_results[service] = status
            
            if len(cached_results) == 3:  # MongoDB, Ollama, and Kafka
                return cached_results
        
        # Run connection checks in parallel
        mongodb_task = asyncio.create_task(self.check_mongodb_connection())
        ollama_task = asyncio.create_task(self.check_ollama_connection())
        kafka_task = asyncio.create_task(self.check_kafka_connection())
        
        try:
            mongodb_status, ollama_status, kafka_status = await asyncio.gather(
                mongodb_task, 
                ollama_task,
                kafka_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(mongodb_status, Exception):
                mongodb_status = ConnectionStatus(
                    service_name="MongoDB",
                    connected=False,
                    error=str(mongodb_status)
                )
            
            if isinstance(ollama_status, Exception):
                ollama_status = ConnectionStatus(
                    service_name="Ollama",
                    connected=False,
                    error=str(ollama_status)
                )
            
            if isinstance(kafka_status, Exception):
                kafka_status = ConnectionStatus(
                    service_name="Kafka",
                    connected=False,
                    error=str(kafka_status)
                )
            
            # Update cache
            self.connection_cache["mongodb"] = mongodb_status
            self.connection_cache["ollama"] = ollama_status
            self.connection_cache["kafka"] = kafka_status
            
            return {
                "mongodb": mongodb_status,
                "ollama": ollama_status,
                "kafka": kafka_status,
            }
            
        except Exception as e:
            logger.error("Failed to check connections", error=str(e))
            return {
                "mongodb": ConnectionStatus("MongoDB", False, error=str(e)),
                "ollama": ConnectionStatus("Ollama", False, error=str(e)),
                "kafka": ConnectionStatus("Kafka", False, error=str(e)),
            }
    
    async def log_connection_status(self, detailed: bool = True) -> Dict[str, Any]:
        """Log connection status to console and return summary"""
        
        logger.info("🔍 Checking service connections...")
        
        connections = await self.check_all_connections(use_cache=False)
        
        # Log individual service status
        for service_name, status in connections.items():
            if status.connected:
                if detailed and status.details:
                    logger.info(
                        f"✅ {status.service_name} connection successful",
                        **status.details
                    )
                else:
                    logger.info(f"✅ {status.service_name} connection successful")
            else:
                logger.error(
                    f"❌ {status.service_name} connection failed",
                    error=status.error,
                    details=status.details
                )
        
        # Log overall status
        connected_count = sum(1 for status in connections.values() if status.connected)
        total_count = len(connections)
        
        if connected_count == total_count:
            logger.info(f"🎯 All services connected ({connected_count}/{total_count})")
        else:
            logger.warning(f"⚠️  Some services disconnected ({connected_count}/{total_count})")
        
        return {
            "connected_services": connected_count,
            "total_services": total_count,
            "all_connected": connected_count == total_count,
            "services": {name: status.to_dict() for name, status in connections.items()}
        }
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for API endpoints"""
        connections = await self.check_all_connections()
        
        return {
            "status": "healthy" if all(s.connected for s in connections.values()) else "degraded",
            "timestamp": time.time(),
            "services": {name: status.to_dict() for name, status in connections.items()},
            "summary": {
                "connected": sum(1 for s in connections.values() if s.connected),
                "total": len(connections),
                "percentage": round(
                    (sum(1 for s in connections.values() if s.connected) / len(connections)) * 100, 1
                ) if connections else 0
            }
        }

# Global service instance
connection_service = ConnectionService()

# Convenience functions
async def check_all_connections() -> Dict[str, ConnectionStatus]:
    """Convenience function to check all connections"""
    return await connection_service.check_all_connections()

async def log_connection_status(detailed: bool = True) -> Dict[str, Any]:
    """Convenience function to log connection status"""
    return await connection_service.log_connection_status(detailed)

async def get_health_summary() -> Dict[str, Any]:
    """Convenience function to get health summary"""
    return await connection_service.get_health_summary()
