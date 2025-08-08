#!/usr/bin/env python3
"""
Simple script to import tarot cards to MongoDB
"""

import json
import pymongo
from pathlib import Path
from datetime import datetime, timezone

def import_to_mongodb():
    """Import tarot cards to MongoDB"""
    
    # MongoDB connection
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["tarot_system"]
    collection = db["tarot_cards"]
    
    # Load JSON file
    json_file = Path(__file__).parent / "tarot-cards.json"
    
    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return
    
    # Check if it's an array or has cards key
    if isinstance(data, list):
        cards = data
        print(f"✅ Found {len(cards)} cards in array")
    elif "cards" in data:
        cards = data["cards"]
        print(f"✅ Found {len(cards)} cards in data.cards")
    else:
        print("❌ No cards found in JSON")
        return
    
    # Clear existing data (optional)
    print("🗑️ Clearing existing data...")
    collection.delete_many({})
    
    # Import each card
    imported = 0
    errors = 0
    
    for i, card in enumerate(cards, 1):
        try:
            # Add MongoDB ObjectId if not present
            if "_id" not in card:
                from bson import ObjectId
                card["_id"] = ObjectId()
            
            # Insert into MongoDB
            result = collection.insert_one(card)
            print(f"✅ [{i:3d}] Imported: {card.get('name', 'Unknown')} -> {result.inserted_id}")
            imported += 1
            
        except Exception as e:
            print(f"❌ [{i:3d}] Error importing {card.get('name', 'Unknown')}: {e}")
            errors += 1
    
    # Print summary
    print(f"\n📊 Import Summary:")
    print(f"   Total cards: {len(cards)}")
    print(f"   Imported: {imported}")
    print(f"   Errors: {errors}")
    
    # Verify import
    count = collection.count_documents({})
    print(f"   In database: {count}")
    
    # Show sample
    sample = collection.find_one()
    if sample:
        print(f"\n🔍 Sample card in database:")
        print(f"   Name: {sample.get('name')}")
        print(f"   ID: {sample.get('_id')}")
        print(f"   Suit: {sample.get('suit')}")
    
    client.close()

if __name__ == "__main__":
    print("🚀 Starting MongoDB import...")
    import_to_mongodb()
    print("✅ Import completed!")
