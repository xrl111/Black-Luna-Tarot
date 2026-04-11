#  Tarot System - Database Connection
"""
MongoDB database connection and initialization
"""

import motor.motor_asyncio
from typing import Optional
import structlog
from app.core.config import settings

logger = structlog.get_logger()

# Global database client
client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

async def init_db() -> None:
    """
    Initialize database connection
    """
    global client, database
    
    try:
        logger.info("Initializing database connection", uri=settings.MONGODB_URI)
        
        # Create motor client
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
        )
        
        # Get database
        database = client[settings.DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        
        logger.info("Database connection established successfully")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        logger.warning("Running in demo mode without database. Some features may not work.")
        # Set to None to indicate no database connection
        client = None
        database = None

async def close_db() -> None:
    """
    Close database connection
    """
    global client
    
    if client:
        client.close()
        logger.info("Database connection closed")

async def create_indexes() -> None:
    """
    Create database indexes for optimal performance
    """
    try:
        logger.info("Creating database indexes")
        
        # Tarot cards indexes
        await database.tarot_cards.create_index([("suit", 1), ("number", 1)])
        await database.tarot_cards.create_index([("name", 1)])
        await database.tarot_cards.create_index([("keywords", 1)])
        await database.tarot_cards.create_index([("element", 1)])
        await database.tarot_cards.create_index([("card_type", 1)])
        await database.tarot_cards.create_index([("name", "text"), ("name_vi", "text"), ("keywords", "text"), ("description", "text")])
        
        # Users indexes
        await database.users.create_index([("email", 1)], unique=True)
        await database.users.create_index([("auth_provider", 1), ("auth_provider_id", 1)])
        await database.users.create_index([("created_at", -1)])
        await database.users.create_index([("last_login", -1)])
        
        # Readings indexes
        await database.readings.create_index([("user_id", 1), ("created_at", -1)])
        await database.readings.create_index([("session_id", 1), ("created_at", -1)])
        await database.readings.create_index([("reading_type", 1)])
        await database.readings.create_index([("created_at", -1)])
        await database.readings.create_index([("tags", 1)])
        await database.readings.create_index([("ai_model_used", 1)])
        
        # AI training data indexes
        await database.ai_training_data.create_index([("training_status", 1)])
        await database.ai_training_data.create_index([("user_id", 1), ("created_at", -1)])
        await database.ai_training_data.create_index([("question_category", 1)])
        await database.ai_training_data.create_index([("training_priority", -1)])
        await database.ai_training_data.create_index([("quality_score", -1)])
        await database.ai_training_data.create_index([("question_complexity", 1)])
        await database.ai_training_data.create_index([("question_emotion", 1)])
        await database.ai_training_data.create_index([("ai_response_tone", 1)])
        await database.ai_training_data.create_index([("verified_user", 1)])
        await database.ai_training_data.create_index([("return_visitor", 1)])
        await database.ai_training_data.create_index([("user_rating", -1)])
        await database.ai_training_data.create_index([("reading_duration", -1)])
        
        # Enhanced readings indexes
        await database.readings.create_index([("question_category", 1)])
        await database.readings.create_index([("question_complexity", 1)])
        await database.readings.create_index([("question_emotion", 1)])
        await database.readings.create_index([("ai_response_tone", 1)])
        await database.readings.create_index([("user_rating", -1)])
        await database.readings.create_index([("reading_duration", -1)])
        await database.readings.create_index([("cards_explored", 1)])
        await database.readings.create_index([("shared_reading", 1)])
        await database.readings.create_index([("saved_reading", 1)])
        await database.readings.create_index([("revisited_reading", 1)])
        
        # Conversation sessions indexes
        await database.conversation_sessions.create_index([("session_id", 1)], unique=True)
        await database.conversation_sessions.create_index([("user_id", 1), ("created_at", -1)])
        await database.conversation_sessions.create_index([("reading_id", 1)])
        await database.conversation_sessions.create_index([("conversation_flow", 1)])
        await database.conversation_sessions.create_index([("user_engagement_level", 1)])
        await database.conversation_sessions.create_index([("conversation_quality_score", -1)])
        await database.conversation_sessions.create_index([("is_completed", 1)])
        
        # Sessions indexes
        await database.sessions.create_index([("session_id", 1)], unique=True)
        await database.sessions.create_index([("last_activity", 1)])
        await database.sessions.create_index([("expires_at", 1)])
        await database.sessions.create_index([("device_info.country", 1)])
        await database.sessions.create_index([("is_active", 1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error("Failed to create indexes", error=str(e))
        raise

def get_database() -> Optional[motor.motor_asyncio.AsyncIOMotorDatabase]:
    """
    Get database instance
    """
    return database

def get_client() -> Optional[motor.motor_asyncio.AsyncIOMotorClient]:
    """
    Get database client
    """
    return client

# Collection getters for easy access
def get_tarot_cards_collection():
    """Get tarot cards collection"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database not available. Please install and start MongoDB.")
    return db.tarot_cards

def get_users_collection():
    """Get users collection"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database not available. Please install and start MongoDB.")
    return db.users

def get_readings_collection():
    """Get readings collection"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database not available. Please install and start MongoDB.")
    return db.readings

def get_ai_training_data_collection():
    """Get AI training data collection"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database not available. Please install and start MongoDB.")
    return db.ai_training_data

def get_sessions_collection():
    """Get sessions collection"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database not available. Please install and start MongoDB.")
    return db.sessions

def get_conversation_sessions_collection():
    """Get conversation sessions collection"""
    db = get_database()
    if db is None:
        raise RuntimeError("Database not available. Please install and start MongoDB.")
    return db.conversation_sessions
