#  Tarot System - User Service
"""
Service layer for user management operations
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from datetime import datetime

from app.database.models import User, UserCreate, UserUpdate, UserResponse
from passlib.context import CryptContext

logger = structlog.get_logger()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """
    Service for managing users
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user
        """
        try:
            # Hash the password if provided
            user_dict = user_data.dict()
            if user_dict.get("password"):
                user_dict["password_hash"] = pwd_context.hash(user_dict["password"])
                del user_dict["password"]  # Remove plain password
            
            user = User(**user_dict)
            result = await self.collection.insert_one(user.dict(by_alias=True))
            user.id = result.inserted_id
            
            logger.info("Created new user", user_id=str(user.id), email=user.email)
            return user
            
        except Exception as e:
            logger.error("Failed to create user", error=str(e))
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID
        """
        try:
            from bson import ObjectId
            
            # Handle both string and ObjectId formats
            if isinstance(user_id, str):
                # Try to convert to ObjectId if it's a valid ObjectId string
                try:
                    object_id = ObjectId(user_id)
                    doc = await self.collection.find_one({"_id": object_id})
                except:
                    # If it's not a valid ObjectId, search by string ID
                    doc = await self.collection.find_one({"_id": user_id})
            else:
                object_id = user_id
                doc = await self.collection.find_one({"_id": object_id})
            
            if doc:
                return User(**doc)
            return None
            
        except Exception as e:
            logger.error("Failed to get user", user_id=user_id, error=str(e))
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        """
        try:
            doc = await self.collection.find_one({"email": email})
            if doc:
                return User(**doc)
            return None
            
        except Exception as e:
            logger.error("Failed to get user by email", email=email, error=str(e))
            raise
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[User]:
        """
        Update a user
        """
        try:
            from bson import ObjectId
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            # Handle ObjectId conversion
            try:
                object_id = ObjectId(user_id)
                result = await self.collection.update_one(
                    {"_id": object_id},
                    {"$set": update_dict}
                )
            except:
                # If not a valid ObjectId, try as string
                result = await self.collection.update_one(
                    {"_id": user_id},
                    {"$set": update_dict}
                )
            
            if result.modified_count > 0:
                return await self.get_user_by_id(user_id)
            return None
            
        except Exception as e:
            logger.error("Failed to update user", user_id=user_id, error=str(e))
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user
        """
        try:
            from bson import ObjectId
            
            # Handle ObjectId conversion
            try:
                object_id = ObjectId(user_id)
                result = await self.collection.delete_one({"_id": object_id})
            except:
                # If not a valid ObjectId, try as string
                result = await self.collection.delete_one({"_id": user_id})
            
            if result.deleted_count > 0:
                logger.info("Deleted user", user_id=user_id)
                return True
            return False
            
        except Exception as e:
            logger.error("Failed to delete user", user_id=user_id, error=str(e))
            raise
    
    async def get_users_paginated(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """
        Get paginated list of users
        """
        try:
            total = await self.collection.count_documents({})
            cursor = self.collection.find({}).skip(skip).limit(limit).sort("created_at", -1)
            
            users = []
            async for doc in cursor:
                users.append(User(**doc))
            
            return {
                "users": users,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            logger.error("Failed to get users paginated", error=str(e))
            raise
    
    async def update_user_statistics(self, user_id: str, reading_data: Dict[str, Any]) -> bool:
        """
        Update user statistics after a reading
        """
        try:
            from bson import ObjectId
            
            # Update statistics based on reading data
            update_data = {
                "statistics.total_readings": {"$inc": 1},
                "statistics.last_reading_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Update average rating if provided
            if "user_rating" in reading_data:
                update_data["statistics.average_rating"] = {
                    "$avg": ["$statistics.average_rating", reading_data["user_rating"]]
                }
            
            # Handle ObjectId conversion
            try:
                object_id = ObjectId(user_id)
                result = await self.collection.update_one(
                    {"_id": object_id},
                    {"$set": update_data}
                )
            except:
                # If not a valid ObjectId, try as string
                result = await self.collection.update_one(
                    {"_id": user_id},
                    {"$set": update_data}
                )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("Failed to update user statistics", user_id=user_id, error=str(e))
            raise

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        """
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            
            # Check if user has password hash (for email auth)
            if not user.password_hash:
                return None
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                return None
            
            return user
            
        except Exception as e:
            logger.error("Failed to authenticate user", email=email, error=str(e))
            raise

    async def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp
        """
        try:
            from bson import ObjectId
            
            # Handle ObjectId conversion
            try:
                object_id = ObjectId(user_id)
                result = await self.collection.update_one(
                    {"_id": object_id},
                    {
                        "$set": {
                            "last_login": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            except:
                # If not a valid ObjectId, try as string
                result = await self.collection.update_one(
                    {"_id": user_id},
                    {
                        "$set": {
                            "last_login": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("Failed to update last login", user_id=user_id, error=str(e))
            raise


