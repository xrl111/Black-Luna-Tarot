import asyncio
import json
import os
import sys

# Add the backend dir to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import init_db, close_db, database

async def import_data():
    await init_db()
    
    # We use a global `database` variable from `app.core.database`
    # Import the actual database var exactly as it's defined
    from app.core.database import database as db
    
    if db is None:
        print("Database connection failed.")
        return
    
    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "tarot-images.json")
    print(f"Loading data from {dataset_path}")
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    cards = data.get("cards", [])
    print(f"Found {len(cards)} cards to import.")
    
    collection = db.tarot_cards
    
    # Clear existing data for a fresh import
    print("Clearing existing tarot cards from collection...")
    await collection.delete_many({})
    
    docs_to_insert = []
    for card in cards:
        doc = {
            "name": card.get("name"),
            # Ensure number is stored as int if possible, else string
            "number": int(card.get("number")) if card.get("number", "").isdigit() else card.get("number"),
            "arcana": card.get("arcana"),
            "suit": card.get("suit"),
            "img": card.get("img"),
            "fortune_telling": card.get("fortune_telling"),
            "keywords": card.get("keywords", []),
            "upright_meaning": " ".join(card.get("meanings", {}).get("light", [])),
            "reversed_meaning": " ".join(card.get("meanings", {}).get("shadow", [])),
            "element": card.get("Elemental"),
            "archetype": card.get("Archetype"),
            "numerology": card.get("Numerology"),
            "mythical": card.get("Mythical/Spiritual"),
            "questions": card.get("Questions to Ask")
        }
        docs_to_insert.append(doc)
        
    if docs_to_insert:
        await collection.insert_many(docs_to_insert)
        print("Successfully imported!")
        
    await close_db()

if __name__ == "__main__":
    asyncio.run(import_data())
