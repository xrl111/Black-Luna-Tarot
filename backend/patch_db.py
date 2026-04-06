import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.database import init_db, close_db
from app.core.database import database as db

async def patch_nulls():
    try:
        await init_db()
        if db is None:
            print("Database connection failed.")
            return

        collection = db.tarot_cards
        cards = await collection.find({}).to_list(100)
        
        updated_count = 0
        for card in cards:
            update_fields = {}
            for field in ["planet", "zodiac", "astrology", "affirmation", 
                          "astrological_significance", "name_vi_alt", "court_rank", "image_url"]:
                # If image_url is missing, construct it from img
                if field == "image_url":
                    if card.get("image_url") is None and card.get("img"):
                        update_fields["image_url"] = f"/uploads/tarot-cards/{card.get('img')}"
                else:
                    if card.get(field) is None:
                        update_fields[field] = "Chưa có dữ liệu"
                        
            if update_fields:
                await collection.update_one({"_id": card["_id"]}, {"$set": update_fields})
                updated_count += 1
                
        print(f"✅ Successfully patched {updated_count} cards out of {len(cards)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(patch_nulls())
