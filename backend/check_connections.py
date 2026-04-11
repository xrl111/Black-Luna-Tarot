#!/usr/bin/env python3
#  Tarot System - Connection Check Script
"""
Command-line script to check MongoDB and Ollama connections
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.connection_service import log_connection_status, connection_service
from app.core.config import settings
import structlog

# Configure structured logging for script
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

async def main():
    """Main function to check all connections"""
    
    print("=" * 60)
    print(" Tarot System - Connection Check")
    print("=" * 60)
    
    logger.info("Starting connection checks...")
    
    try:
        # Check all connections with detailed logging
        summary = await log_connection_status(detailed=True)
        
        print("\n" + "=" * 60)
        print(" SUMMARY")
        print("=" * 60)
        
        if summary["all_connected"]:
            print(" Status: ALL SERVICES CONNECTED")
            print(f" Connected: {summary['connected_services']}/{summary['total_services']}")
            print(" System is ready for operation!")
        else:
            print(" Status: SOME SERVICES DISCONNECTED")
            print(f"  Connected: {summary['connected_services']}/{summary['total_services']}")
            print(" Please check the error messages above and ensure all services are running")
        
        print("\n Tips:")
        print("   • MongoDB: Ensure MongoDB is running on", settings.MONGODB_URI)
        print("   • Ollama: Ensure Ollama is running on", settings.OLLAMA_URL)
        print("   • Check firewall and network connectivity")
        
        print("\n API Endpoints:")
        print(f"   • Health Check: http://{settings.HOST}:{settings.PORT}/health")
        print(f"   • Connection Status: http://{settings.HOST}:{settings.PORT}/api/v1/system/connections")
        print(f"   • Refresh Connections: http://{settings.HOST}:{settings.PORT}/api/v1/system/connections/refresh")
        
        # Exit with appropriate code
        if summary["all_connected"]:
            print("\n All checks passed!")
            sys.exit(0)
        else:
            print("\n  Some checks failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error("Connection check failed", error=str(e))
        print(f"\n Connection check failed: {e}")
        sys.exit(1)

async def check_individual_services():
    """Check individual services separately"""
    
    print("\n Individual Service Checks")
    print("-" * 40)
    
    # Check MongoDB
    print("\n Checking MongoDB...")
    mongodb_status = await connection_service.check_mongodb_connection()
    if mongodb_status.connected:
        print(" MongoDB: Connected")
        if mongodb_status.details:
            print(f"   • Database: {mongodb_status.details.get('database')}")
            print(f"   • Version: {mongodb_status.details.get('server_version')}")
            print(f"   • Response Time: {mongodb_status.details.get('response_time_ms')}ms")
    else:
        print(" MongoDB: Disconnected")
        print(f"   • Error: {mongodb_status.error}")
    
    # Check Ollama
    print("\n Checking Ollama...")
    ollama_status = await connection_service.check_ollama_connection()
    if ollama_status.connected:
        print(" Ollama: Connected")
        if ollama_status.details:
            print(f"   • URL: {ollama_status.details.get('url')}")
            print(f"   • Default Model: {ollama_status.details.get('default_model')}")
            print(f"   • Model Available: {ollama_status.details.get('default_model_available')}")
            print(f"   • Total Models: {ollama_status.details.get('model_count')}")
            print(f"   • Response Time: {ollama_status.details.get('response_time_ms')}ms")
    else:
        print(" Ollama: Disconnected")
        print(f"   • Error: {ollama_status.error}")

if __name__ == "__main__":
    # Check if we should run individual checks
    if len(sys.argv) > 1 and sys.argv[1] == "--individual":
        asyncio.run(check_individual_services())
    else:
        asyncio.run(main())
