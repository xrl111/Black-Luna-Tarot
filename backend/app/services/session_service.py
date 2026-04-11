#  Tarot System - Session Service
"""
Service layer for session management operations
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from datetime import datetime, timedelta, timezone
import secrets

from app.database.models import Session, SessionCreate, SessionUpdate
from app.core.config import settings

logger = structlog.get_logger()

class SessionService:
    """
    Service for managing user sessions
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create_session(self, session_data: SessionCreate) -> Session:
        """
        Create a new session
        """
        try:
            session = Session(**session_data.dict())
            result = await self.collection.insert_one(session.dict(by_alias=True))
            session.id = result.inserted_id
            
            logger.info("Created new session", session_id=session.session_id)
            return session
            
        except Exception as e:
            logger.error("Failed to create session", error=str(e))
            # Return a mock session for development when database is not available
            if "Connection refused" in str(e) or "No connection" in str(e):
                logger.warning("Database not available, returning mock session for development")
                session = Session(**session_data.dict())
                session.id = "mock_session_id"
                return session
            raise
    
    async def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """
        Get a session by session ID
        """
        try:
            if not session_id or not session_id.strip():
                return None
            
            doc = await self.collection.find_one({"session_id": session_id})
            if doc:
                return Session(**doc)
            return None
            
        except Exception as e:
            logger.error("Failed to get session", session_id=session_id, error=str(e))
            return None  # Return None instead of raising exception
    
    async def get_session_by_token(self, session_token: str) -> Optional[Session]:
        """
        Get a session by session token
        """
        try:
            if not session_token or not session_token.strip():
                return None
            
            doc = await self.collection.find_one({"session_token": session_token})
            if doc:
                return Session(**doc)
            return None
            
        except Exception as e:
            logger.error("Failed to get session by token", error=str(e))
            return None  # Return None instead of raising exception
    
    async def update_session(self, session_id: str, update_data: SessionUpdate) -> Optional[Session]:
        """
        Update a session
        """
        try:
            if not session_id or not session_id.strip():
                return None
            
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.now(timezone.utc)
            
            result = await self.collection.update_one(
                {"session_id": session_id},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return await self.get_session_by_id(session_id)
            return None
            
        except Exception as e:
            logger.error("Failed to update session", session_id=session_id, error=str(e))
            return None  # Return None instead of raising exception
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        """
        try:
            if not session_id or not session_id.strip():
                return False
            
            result = await self.collection.delete_one({"session_id": session_id})
            
            if result.deleted_count > 0:
                logger.info("Deleted session", session_id=session_id)
                return True
            return False
            
        except Exception as e:
            logger.error("Failed to delete session", session_id=session_id, error=str(e))
            return False  # Return False instead of raising exception
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        """
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.now(timezone.utc)}
            })
            
            if result.deleted_count > 0:
                logger.info("Cleaned up expired sessions", count=result.deleted_count)
            
            return result.deleted_count
            
        except Exception as e:
            logger.error("Failed to cleanup expired sessions", error=str(e))
            return 0  # Return 0 instead of raising exception
    
    async def generate_session_token(self) -> str:
        """
        Generate a secure session token
        """
        return secrets.token_urlsafe(32)
    
    async def create_anonymous_session(self, device_info: Dict[str, Any]) -> Session:
        """
        Create an anonymous session for new users
        """
        try:
            session_id = secrets.token_urlsafe(16)
            session_token = await self.generate_session_token()
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
            
            session_data = SessionCreate(
                session_id=session_id,
                session_token=session_token,
                device_info=device_info,
                expires_at=expires_at
            )
            
            return await self.create_session(session_data)
            
        except Exception as e:
            logger.error("Failed to create anonymous session", error=str(e))
            raise
    
    async def update_session_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp
        """
        try:
            result = await self.collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "last_activity": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("Failed to update session activity", session_id=session_id, error=str(e))
            raise
    
    async def get_active_sessions_count(self) -> int:
        """
        Get count of active sessions
        """
        try:
            count = await self.collection.count_documents({
                "is_active": True,
                "expires_at": {"$gt": datetime.now(timezone.utc)}
            })
            
            return count
            
        except Exception as e:
            logger.error("Failed to get active sessions count", error=str(e))
            return 0  # Return 0 instead of raising exception

    async def create_session_for_user(self, user_id: str) -> Session:
        """
        Create a session for a specific user
        """
        try:
            session_id = secrets.token_urlsafe(16)
            session_token = await self.generate_session_token()
            expires_at = datetime.now(timezone.utc) + timedelta(days=settings.SESSION_EXPIRE_DAYS)
            
            # Create basic device info
            device_info = {
                "user_agent": "Unknown",
                "ip_address": "Unknown",
                "country": None,
                "city": None,
                "timezone": None,
                "language": None,
                "screen_resolution": None,
                "device_type": "Unknown"
            }
            
            session_data = SessionCreate(
                session_id=session_id,
                session_token=session_token,
                device_info=device_info,
                expires_at=expires_at
            )
            
            # Create session and add user_id
            session = await self.create_session(session_data)
            
            # Update session with user_id
            await self.collection.update_one(
                {"session_id": session_id},
                {"$set": {"user_id": user_id}}
            )
            
            # Return updated session
            return await self.get_session_by_id(session_id)
            
        except Exception as e:
            logger.error("Failed to create session for user", user_id=user_id, error=str(e))
            raise

    async def invalidate_user_sessions(self, user_id: str) -> bool:
        """
        Invalidate all sessions for a user
        """
        try:
            result = await self.collection.update_many(
                {"user_id": user_id, "is_active": True},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info("Invalidated user sessions", user_id=user_id, count=result.modified_count)
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("Failed to invalidate user sessions", user_id=user_id, error=str(e))
            raise


