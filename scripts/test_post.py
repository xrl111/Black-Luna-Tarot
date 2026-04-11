import httpx

payload = {
    "session_id": "session_12345",
    "user_id": "1",
    "question": "Test question",
    "reading_type": "general",
    "reading_spread": "three_card",
    "cards_drawn": [
        {
            "card_id": "test",
            "position": 1,
            "orientation": "upright",
            "position_meaning": "General advice",
            "interpretation": "Interpreted by AI in full text",
            "card_name": "Test Card",
            "card_name_vi": "Test Vi",
            "traditional_meaning": "Test",
            "card_type": "major",
            "suit": "major",
            "number": "0"
        }
    ],
    "ai_response": "Test full response",
    "ai_model_used": "qwen2.5:1.5b"
}

import asyncio
async def main():
    async with httpx.AsyncClient() as client:
        res = await client.post("http://localhost:8000/api/v1/readings/", json=payload)
        print(res.status_code)
        print(res.json())

if __name__ == "__main__":
    asyncio.run(main())
