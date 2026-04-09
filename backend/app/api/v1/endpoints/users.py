from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from typing import Any

from app.core.database import get_database
from app.core.security import get_current_user
from app.database.models import User, UserPreferences

logger = structlog.get_logger()
router = APIRouter()

def get_users_collection() -> AsyncIOMotorCollection:
    db = get_database()
    return db["users"]

@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user profile and preferences.
    """
    return current_user

@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    collection: AsyncIOMotorCollection = Depends(get_users_collection)
) -> Any:
    """
    Update current user's AI personalization preferences.
    """
    try:
        # Convert preferences to dict, excluding unset fields
        prefs_dict = preferences.dict(exclude_unset=True)
        
        # Build update query for MongoDB dot notation
        update_query = {}
        for key, value in prefs_dict.items():
            update_query[f"preferences.{key}"] = value
            
        if not update_query:
            return current_user.preferences

        # Update in MongoDB
        await collection.update_one(
            {"_id": current_user.id},
            {"$set": update_query}
        )
        
        # Merge updated preferences into current_user object to return
        for key, value in prefs_dict.items():
            setattr(current_user.preferences, key, value)
            
        logger.info("Updated user preferences", user_id=str(current_user.id))
        return current_user.preferences
        
    except Exception as e:
        logger.error("Failed to update user preferences", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )
