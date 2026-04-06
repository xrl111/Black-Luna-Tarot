import pymongo

def patch_nulls():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["tarot_system"]
    collection = db["tarot_cards"]
    
    cards = list(collection.find({}))
    
    updated_count = 0
    for card in cards:
        update_fields = {}
        for field in ["planet", "zodiac", "astrology", "affirmation", 
                      "astrological_significance", "name_vi_alt", "court_rank", "image_url"]:
            # If image_url is missing, construct it from img
            if field == "image_url" and (card.get("image_url") is None or card.get("image_url") == ""):
                if card.get("img"):
                    update_fields["image_url"] = f"/uploads/tarot-cards/{card.get('img')}"
                elif card.get("image_filename"):
                    update_fields["image_url"] = f"/uploads/tarot-cards/{card.get('image_filename')}"
            else:
                if card.get(field) is None:
                    update_fields[field] = "Chưa có dữ liệu"
                    
        if update_fields:
            collection.update_one({"_id": card["_id"]}, {"$set": update_fields})
            updated_count += 1
            
    print(f"✅ Successfully patched {updated_count} cards out of {len(cards)}")
    client.close()

if __name__ == "__main__":
    patch_nulls()
