from datetime import datetime, timezone
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.config import settings
from app.core.database import get_database

async def get_rate_limits_collection() -> AsyncIOMotorCollection:
    """Get the rate_limits collection"""
    db = get_database()
    return db["rate_limits"]

async def check_and_increment_quota(identifier: str, is_guest: bool = True) -> dict:
    """
    Check if the user/IP has exceeded their daily quota.
    If not, increment their usage count.
    
    Args:
        identifier: The IP address (for guest) or user email/ID (for logged in users)
        is_guest: Boolean indicating which quota limit to apply
        
    Returns:
        dict: Usage statistics {"used": X, "limit": Y}
        
    Raises:
        HTTPException(429) if quota exceeded
    """
    collection = await get_rate_limits_collection()
    
    # Use UTC date string as partition key for daily reset
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    limit = settings.GUEST_DAILY_LIMIT if is_guest else settings.ACCOUNT_DAILY_LIMIT
    
    # Atomic find and modify (or insert if not exists)
    doc = await collection.find_one_and_update(
        {"identifier": identifier, "date": today_str},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True  # Return the document AFTER update
    )
    
    current_count = doc.get("count", 1)
    
    if current_count > limit:
        # We still incremented it in DB, but we will block the request.
        # This acts as a soft penalty for spamming, showing how much they spammed.
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily quota exceeded. Limit is {limit} readings per day for {'Guest' if is_guest else 'Account'} users."
        )
        
    return {
        "used": current_count,
        "limit": limit
    }
