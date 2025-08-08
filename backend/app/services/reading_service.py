# 🎯 Tarot System - Reading Service
"""
Service layer for tarot reading operations
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from datetime import datetime

from app.database.models import Reading, ReadingCreate, ReadingUpdate, ReadingResponse

logger = structlog.get_logger()

class ReadingService:
    """
    Service for managing tarot readings
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create_reading(self, reading_data: ReadingCreate) -> Reading:
        """
        Create a new tarot reading
        """
        try:
            reading = Reading(**reading_data.dict())
            result = await self.collection.insert_one(reading.dict(by_alias=True))
            reading.id = result.inserted_id
            
            logger.info("Created new reading", reading_id=str(reading.id))
            return reading
            
        except Exception as e:
            logger.error("Failed to create reading", error=str(e))
            raise
    
    async def get_reading_by_id(self, reading_id: str) -> Optional[Reading]:
        """
        Get a reading by ID
        """
        try:
            if not reading_id or not reading_id.strip():
                return None
            
            from bson import ObjectId
            if not ObjectId.is_valid(reading_id):
                logger.warning("Invalid ObjectId format", reading_id=reading_id)
                return None
            
            doc = await self.collection.find_one({"_id": ObjectId(reading_id)})
            if doc:
                return Reading(**doc)
            return None
            
        except Exception as e:
            logger.error("Failed to get reading", reading_id=reading_id, error=str(e))
            return None  # Return None instead of raising exception
    
    async def get_readings_by_session(self, session_id: str, limit: int = 10) -> List[Reading]:
        """
        Get readings for a specific session
        """
        try:
            if not session_id or not session_id.strip():
                return []
            
            if limit <= 0 or limit > 100:
                limit = 10
            
            cursor = self.collection.find({"session_id": session_id}).sort("created_at", -1).limit(limit)
            readings = []
            async for doc in cursor:
                readings.append(Reading(**doc))
            
            logger.info("Retrieved readings by session", session_id=session_id, count=len(readings))
            return readings
            
        except Exception as e:
            logger.error("Failed to get readings by session", session_id=session_id, error=str(e))
            return []  # Return empty list instead of raising exception
    
    async def update_reading(self, reading_id: str, update_data: ReadingUpdate) -> Optional[Reading]:
        """
        Update a reading
        """
        try:
            if not reading_id or not reading_id.strip():
                return None
            
            from bson import ObjectId
            if not ObjectId.is_valid(reading_id):
                logger.warning("Invalid ObjectId format", reading_id=reading_id)
                return None
            
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(reading_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return await self.get_reading_by_id(reading_id)
            return None
            
        except Exception as e:
            logger.error("Failed to update reading", reading_id=reading_id, error=str(e))
            return None  # Return None instead of raising exception
    
    async def delete_reading(self, reading_id: str) -> bool:
        """
        Delete a reading
        """
        try:
            if not reading_id or not reading_id.strip():
                return False
            
            from bson import ObjectId
            if not ObjectId.is_valid(reading_id):
                logger.warning("Invalid ObjectId format", reading_id=reading_id)
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(reading_id)})
            
            if result.deleted_count > 0:
                logger.info("Deleted reading", reading_id=reading_id)
                return True
            return False
            
        except Exception as e:
            logger.error("Failed to delete reading", reading_id=reading_id, error=str(e))
            return False  # Return False instead of raising exception
    
    async def get_readings_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get reading statistics
        """
        try:
            pipeline = []
            
            if session_id and session_id.strip():
                pipeline.append({"$match": {"session_id": session_id}})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_readings": {"$sum": 1},
                        "avg_rating": {"$avg": "$user_rating"},
                        "total_tokens": {"$sum": "$tokens_used"},
                        "avg_processing_time": {"$avg": "$processing_time"}
                    }
                }
            ])
            
            result = await self.collection.aggregate(pipeline).to_list(1)
            
            if result:
                stats = result[0]
                return {
                    "total_readings": stats.get("total_readings", 0),
                    "average_rating": round(stats.get("avg_rating", 0), 2),
                    "total_tokens_used": stats.get("total_tokens", 0),
                    "average_processing_time": round(stats.get("avg_processing_time", 0), 2)
                }
            
            return {
                "total_readings": 0,
                "average_rating": 0,
                "total_tokens_used": 0,
                "average_processing_time": 0
            }
            
        except Exception as e:
            logger.error("Failed to get reading stats", error=str(e))
            return {
                "total_readings": 0,
                "average_rating": 0,
                "total_tokens_used": 0,
                "average_processing_time": 0
            }  # Return empty stats instead of raising exception

