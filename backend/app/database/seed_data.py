#  Tarot System - Seed Data
"""
Initial data for tarot cards collection
"""

import asyncio
import motor.motor_asyncio
from datetime import datetime
import os
# from dotenv import load_dotenv  # Commented out to avoid .env file issues

# Load environment variables
# load_dotenv()  # Commented out to avoid .env file issues

# Database configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tarot_system")

# Sample tarot cards data (Major Arcana subset)
TAROT_CARDS_DATA = [
    {
        "name": "The Fool",
        "name_vi": "Kẻ Ngốc",
        "suit": "major_arcana",
        "number": 0,
        "meaning_upright": "New beginnings, innocence, spontaneity, free spirit",
        "meaning_reversed": "Recklessness, risk-taking, inconsideration",
        "description": "The Fool represents new beginnings, having faith in the future, being inexperienced, not knowing what to expect, having beginner's luck, improvisation and believing in the universe.",
        "keywords": ["new beginnings", "innocence", "adventure", "spontaneity", "faith"],
        "element": "air",
        "planet": "uranus",
        "zodiac": None,
        "image_url": "https://example.com/fool.jpg",
        "card_type": "major",
        "astrological_significance": "Uranus - Innovation and sudden changes",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "The Magician",
        "name_vi": "Pháp Sư",
        "suit": "major_arcana",
        "number": 1,
        "meaning_upright": "Manifestation, resourcefulness, power, inspired action",
        "meaning_reversed": "Manipulation, poor planning, untapped talents",
        "description": "The Magician represents your ability to take action and manifest your desires. You have all the tools and resources you need to succeed.",
        "keywords": ["manifestation", "power", "skill", "concentration", "action"],
        "element": "air",
        "planet": "mercury",
        "zodiac": "gemini",
        "image_url": "https://example.com/magician.jpg",
        "card_type": "major",
        "astrological_significance": "Mercury - Communication and intellect",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "The High Priestess",
        "name_vi": "Nữ Tư Tế",
        "suit": "major_arcana",
        "number": 2,
        "meaning_upright": "Intuition, sacred knowledge, divine feminine, subconscious mind",
        "meaning_reversed": "Secrets, disconnected from intuition, withdrawal",
        "description": "The High Priestess represents intuition, mystery, spirituality and inner knowledge. She encourages you to trust your instincts and listen to your inner voice.",
        "keywords": ["intuition", "mystery", "spirituality", "inner knowledge", "divine feminine"],
        "element": "water",
        "planet": "moon",
        "zodiac": "cancer",
        "image_url": "https://example.com/high-priestess.jpg",
        "card_type": "major",
        "astrological_significance": "Moon - Emotions and intuition",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "The Empress",
        "name_vi": "Hoàng Hậu",
        "suit": "major_arcana",
        "number": 3,
        "meaning_upright": "Femininity, beauty, nature, abundance, nurturing",
        "meaning_reversed": "Creative block, dependence on others, emptiness",
        "description": "The Empress represents abundance, nurturing, fertility and the natural world. She embodies the divine feminine and the power of creation.",
        "keywords": ["femininity", "beauty", "nature", "abundance", "nurturing", "fertility"],
        "element": "earth",
        "planet": "venus",
        "zodiac": "taurus",
        "image_url": "https://example.com/empress.jpg",
        "card_type": "major",
        "astrological_significance": "Venus - Love and beauty",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "The Emperor",
        "name_vi": "Hoàng Đế",
        "suit": "major_arcana",
        "number": 4,
        "meaning_upright": "Authority, structure, control, fatherhood, power",
        "meaning_reversed": "Domination, excessive control, rigidity, inflexibility",
        "description": "The Emperor represents authority, structure, control and fatherhood. He embodies masculine energy and the power to create order from chaos.",
        "keywords": ["authority", "structure", "control", "fatherhood", "power", "leadership"],
        "element": "fire",
        "planet": "mars",
        "zodiac": "aries",
        "image_url": "https://example.com/emperor.jpg",
        "card_type": "major",
        "astrological_significance": "Mars - Action and energy",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

async def seed_database():
    """
    Seed the database with initial tarot cards data
    """
    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db.tarot_cards
        
        # Check if data already exists
        existing_count = await collection.count_documents({})
        if existing_count > 0:
            print(f" Database already contains {existing_count} tarot cards")
            return
        
        # Insert tarot cards data
        result = await collection.insert_many(TAROT_CARDS_DATA)
        print(f" Successfully inserted {len(result.inserted_ids)} tarot cards")
        
        # Create indexes for better performance
        await collection.create_index("name")
        await collection.create_index("suit")
        await collection.create_index("number")
        await collection.create_index("card_type")
        print(" Database indexes created")
        
    except Exception as e:
        print(f" Error seeding database: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
