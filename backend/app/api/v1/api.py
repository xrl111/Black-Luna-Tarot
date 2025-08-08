# 🎯 Tarot System - Main API Router
"""
Main API router that includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    tarot_cards,
    readings,
    ai_service,
    system,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    tarot_cards.router,
    prefix="/tarot-cards",
    tags=["tarot-cards"]
)

api_router.include_router(
    readings.router,
    prefix="/readings",
    tags=["readings"]
)

api_router.include_router(
    ai_service.router,
    prefix="/ai",
    tags=["ai-service"]
)

api_router.include_router(
    system.router,
    prefix="/system",
    tags=["system"]
)
