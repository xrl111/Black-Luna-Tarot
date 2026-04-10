import asyncio
import httpx

async def main():
    url = "http://localhost:8000/api/v1/ai/generate-reading/stream"
    payload = {
        "question": "Tôi nên tập trung điều gì trong 3 tháng tới?",
        "cards": [
            {"id": "689483ffac8d159543c982d4", "name": "King of Pentacles", "name_vi": "Vua Đồng Tiền"},
        ],
        "reading_type": "general",
        "reading_detail": "quick"
    }

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, timeout=60) as response:
                print(f"Status: {response.status_code}")
                async for line in response.aiter_lines():
                    print("Chunk:", line)
        print("Stream finished ✅")
    except Exception as e:
        print("Exception:", type(e), str(e))

if __name__ == "__main__":
    asyncio.run(main())
