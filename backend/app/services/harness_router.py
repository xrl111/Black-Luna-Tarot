import json
import httpx
import structlog
from typing import Dict, Any
from app.core.config import settings

logger = structlog.get_logger(__name__)

class HarnessRouterService:
    """
    AutoHarness Router Layer:
    Sử dụng mô hình nhỏ (Qwen 1.5B) đọc JSON để phân loại Intent, 
    sau đó trả về một Spread / Harness cố định để hướng dẫn người dùng rút bài.
    """
    def __init__(self):
        self.ollama_url = settings.OLLAMA_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.timeout = 15.0

    async def classify_intent(self, question: str) -> str:
        """
        Dùng LLM siêu nhỏ để phân loại câu hỏi ra 1 trong các hòm cố định.
        Ép trả về JSON.
        """
        system_prompt = '''
Bạn là hệ thống phân loại Tarot. 
Hãy đọc câu hỏi và phân loại vào MỘT trong các nhóm: "love" (tình cảm), "career" (công việc, tiền bạc), "yes_no" (câu hỏi có/không), "spiritual" (tâm linh, tổng quan lớn), "general" (chung chung).
Chỉ trả về JSON có định dạng: {"intent": "danh mục"}
'''
        prompt = f"Câu hỏi: {question}"
        
        payload = {
            "model": self.ollama_model,
            "prompt": f"{system_prompt}\n{prompt}",
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "num_predict": 50
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.ollama_url}/api/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "{}")
                    try:
                        parsed = json.loads(response_text)
                        intent = parsed.get("intent", "general").lower()
                        if intent not in ["love", "career", "yes_no", "spiritual", "general"]:
                            intent = "general"
                        return intent
                    except json.JSONDecodeError:
                        return "general"
                return "general"
        except Exception as e:
            logger.error("Failed to classify intent", error=str(e))
            return "general"

    def get_spread_harness(self, intent: str) -> Dict[str, Any]:
        """
        AutoHarness: Định nghĩa các rule cứng về số bài, loại trải bài dựa trên Intent
        """
        rules = {
            "love": {
                "reading_type": "3",
                "spread_name": "Quan Hệ Tình Cảm (3 lá)",
                "card_count": 3,
                "positions": ["Bản thân", "Đối phương", "Động lực giữa hai người"]
            },
            "career": {
                "reading_type": "5",
                "spread_name": "Sự Nghiệp & Tài Chính (5 lá)",
                "card_count": 5,
                "positions": ["Tình trạng hiện tại", "Khó khăn", "Kỹ năng cần có", "Sự hỗ trợ", "Đích đến"]
            },
            "yes_no": {
                "reading_type": "1",
                "spread_name": "Trả Lời Trực Diện (1 lá)",
                "card_count": 1,
                "positions": ["Kết quả bốc thăm"]
            },
            "spiritual": {
                "reading_type": "10",
                "spread_name": "Celtic Cross Truyền Thống (10 lá)",
                "card_count": 10,
                "positions": ["Hiện tại", "Thách thức", "Quá khứ gần", "Tương lai gần", "Ý thức", "Vô thức", "Bản thân", "Môi trường", "Hy vọng & Nỗi sợ", "Kết quả tiềm năng"]
            },
            "general": {
                "reading_type": "3",
                "spread_name": "Quá Khứ - Hiện Tại - Tương Lai (3 lá)",
                "card_count": 3,
                "positions": ["Quá khứ", "Hiện tại", "Tương lai"]
            }
        }
        return rules.get(intent, rules["general"])

    async def get_intake_recommendation(self, question: str) -> Dict[str, Any]:
        """
        Lấy cấu hình thu thập dữ liệu đầu vào (Intake Configuration)
        """
        intent = await self.classify_intent(question)
        harness = self.get_spread_harness(intent)
        return {
            "question": question,
            "detected_intent": intent,
            "recommended_spread": harness
        }
