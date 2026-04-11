from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from typing import Any

from app.core.database import get_database
from app.core.security import get_current_user
from app.database.models import User, UserPreferences

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.postgres import get_pg_db
from app.database.pg_models import PGUser

logger = structlog.get_logger()
router = APIRouter()

@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: PGUser = Depends(get_current_user)
) -> Any:
    """
    Get current user profile and preferences from Postgres but mapped to Pydantic Model.
    """
    return current_user.to_pydantic_dict()

@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: PGUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_pg_db)
) -> Any:
    """
    Update current user's AI personalization preferences into Postgres.
    """
    try:
        # Convert preferences to dict, excluding unset fields
        prefs_dict = preferences.dict(exclude_unset=True)
        
        # We need to map pydantic fields to Postgres columns
        mapping = {
            "experience_level": "experience_level",
            "belief_system": "belief_system",
            "cultural_background": "cultural_background",
            "reading_frequency": "reading_frequency",
            "reading_style": "preferred_style",
            "language": "language_preference",
            "tarot_tradition": "tarot_tradition"
        }
        
        # Fetch the user again inside this session to update
        res = await session.execute(select(PGUser).where(PGUser.id == current_user.id))
        user_to_update = res.scalar_one()

        # Update columns in Postgres
        for key, value in prefs_dict.items():
            if key in mapping:
                setattr(user_to_update, mapping[key], value)
            
        await session.commit()
        
        logger.info("Updated user preferences in Postgres", user_id=str(current_user.id))
        return user_to_update.to_pydantic_dict().get("preferences")
        
    except Exception as e:
        logger.error("Failed to update user preferences", user_id=str(current_user.id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )
