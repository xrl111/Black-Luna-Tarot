#  Tarot System - Readings API Endpoints
"""
API endpoints for tarot readings
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from typing import List, Optional

from app.core.database import get_readings_collection
from app.database.models import Reading, ReadingCreate, ReadingResponse, ReadingUpdate, User
from app.services.reading_service import ReadingService
from app.core.security import get_optional_current_user
from app.services.rate_limit import check_and_increment_quota

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=ReadingResponse)
async def create_reading(
    request: Request,
    reading_data: ReadingCreate,
    collection: AsyncIOMotorCollection = Depends(get_readings_collection),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Create a new tarot reading (With Rate Limiting and Guest Restrictions)
    """
    try:
        # Rate Limiting Logic (REMOVED: saving should not consume quota when generating already did)
        is_guest = current_user is None
        # identifier = request.client.host if is_guest else str(current_user.id)
        # await check_and_increment_quota(identifier, is_guest=is_guest)

        # Apply Feature Restrictions for Guest Users
        if is_guest:
            # Force guest users to use default local model to save API quota
            reading_data.ai_model_used = "qwen2.5:1.5b"
            
            # Remove personalization payload if any
            if hasattr(reading_data, "user_context"):
                reading_data.user_context = None
        else:
            # Optionally set user_id if they are logged in and omitted it
            if not reading_data.user_id:
                reading_data.user_id = str(current_user.id)
        # Additional validation
        if not reading_data.session_id or not reading_data.session_id.strip():
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        if not reading_data.question or not reading_data.question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        if not reading_data.cards_drawn:
            raise HTTPException(status_code=400, detail="At least one card must be drawn")
        
        if not reading_data.ai_response or not reading_data.ai_response.strip():
            raise HTTPException(status_code=400, detail="AI response is required")
        
        service = ReadingService(collection)
        reading = await service.create_reading(reading_data)
        
        logger.info("Created new reading", reading_id=str(reading.id))
        return reading
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create reading", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create reading")

@router.get("/{reading_id}", response_model=ReadingResponse)
async def get_reading(
    reading_id: str,
    collection: AsyncIOMotorCollection = Depends(get_readings_collection)
):
    """
    Get a specific reading by ID
    """
    try:
        if not reading_id or not reading_id.strip():
            raise HTTPException(status_code=400, detail="Reading ID is required")
        
        service = ReadingService(collection)
        reading = await service.get_reading_by_id(reading_id)
        
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")
        
        return reading
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get reading", reading_id=reading_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get reading")

@router.get("/session/{session_id}", response_model=List[ReadingResponse])
async def get_readings_by_session(
    session_id: str,
    limit: int = 10,
    collection: AsyncIOMotorCollection = Depends(get_readings_collection)
):
    """
    Get readings for a specific session
    """
    try:
        if not session_id or not session_id.strip():
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        if limit <= 0 or limit > 100:
            limit = 10
        
        service = ReadingService(collection)
        readings = await service.get_readings_by_session(session_id, limit)
        
        logger.info("Retrieved readings by session", session_id=session_id, count=len(readings))
        return readings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get readings by session", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get readings by session")

@router.put("/{reading_id}", response_model=ReadingResponse)
async def update_reading(
    reading_id: str,
    update_data: ReadingUpdate,
    collection: AsyncIOMotorCollection = Depends(get_readings_collection)
):
    """
    Update a reading
    """
    try:
        if not reading_id or not reading_id.strip():
            raise HTTPException(status_code=400, detail="Reading ID is required")
        
        service = ReadingService(collection)
        reading = await service.update_reading(reading_id, update_data)
        
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")
        
        logger.info("Updated reading", reading_id=reading_id)
        return reading
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update reading", reading_id=reading_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update reading")

@router.delete("/{reading_id}")
async def delete_reading(
    reading_id: str,
    collection: AsyncIOMotorCollection = Depends(get_readings_collection)
):
    """
    Delete a reading
    """
    try:
        if not reading_id or not reading_id.strip():
            raise HTTPException(status_code=400, detail="Reading ID is required")
        
        service = ReadingService(collection)
        deleted = await service.delete_reading(reading_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Reading not found")
        
        logger.info("Deleted reading", reading_id=reading_id)
        return {"message": "Reading deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete reading", reading_id=reading_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete reading")

@router.get("/stats/overview")
async def get_readings_stats(
    session_id: Optional[str] = None,
    collection: AsyncIOMotorCollection = Depends(get_readings_collection)
):
    """
    Get reading statistics
    """
    try:
        service = ReadingService(collection)
        stats = await service.get_readings_stats(session_id)
        
        logger.info("Retrieved reading stats", session_id=session_id)
        return stats
        
    except Exception as e:
        logger.error("Failed to get reading stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get reading stats")
