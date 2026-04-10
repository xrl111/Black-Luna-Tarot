import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from aiokafka import AIOKafkaConsumer

async def main():
    print("1. Clearing Rate Limits in MongoDB...")
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["tarot_system"]
    await db["rate_limits"].delete_many({})
    print("   -> Cleared.")

    print("\n2. Sending valid Payload to FastAPI...")
    payload = {
        "session_id": "test_session_999",
        "question": "Testing auto-save and big data ingest pipeline.",
        "cards_drawn": [{
            "card_id": "sword_queen",
            "position": 1,
            "orientation": "upright",
            "position_meaning": "General",
            "interpretation": "AI text",
            "card_name": "Queen of Swords",
            "card_name_vi": "Hoang Hau Kiem",
            "traditional_meaning": "Clear thinking",
            "card_type": "minor",
            "suit": "swords",
            "number": "13"
        }],
        "ai_response": "Hay suy nghi logic va thong suot.",
        "reading_type": "general",
        "reading_spread": "single_card",
        "ai_model_used": "qwen"
    }
    
    async with httpx.AsyncClient() as http_client:
        resp = await http_client.post("http://localhost:8000/api/v1/readings/", json=payload)
        print(f"   -> FastAPI Response: {resp.status_code}")
        if resp.status_code != 200:
            print(f"   -> Response Body: {resp.text}")
            return

    print("\n3. Waiting 2 seconds for Kafka processing...")
    await asyncio.sleep(2)

    print("\n4. Pinging Kafka to read from tarot-events...")
    consumer = AIOKafkaConsumer(
        "tarot-events",
        bootstrap_servers="localhost:9094",
        auto_offset_reset="earliest",
        group_id="test_verificator"
    )
    await consumer.start()
    try:
        data = await consumer.getmany(timeout_ms=3000)
        topic_partition = list(data.keys())[0] if data else None
        messages = data.get(topic_partition, []) if topic_partition else []
        
        found = False
        for msg in messages:
            msg_str = msg.value.decode("utf-8")
            if "test_session_999" in msg_str:
                found = True
                print("   -> ✅ SUCCESS! FOUND THE MESSAGE IN KAFKA:")
                print(f"       {msg_str[:300]}...")
                break
        
        if not found:
            print("   -> ❌ FAILED! Message not found in Kafka topic!")
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
