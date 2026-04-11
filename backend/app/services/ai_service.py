#  Tarot System - AI Service
"""
Service layer for AI integration and tarot reading generation
"""

from typing import List, Optional, Dict, Any
import json
import httpx
import structlog
from datetime import datetime
import asyncio

from app.core.config import settings
from app.core.exceptions import AIServiceException
from app.database.models import CardDrawn

logger = structlog.get_logger()

class AIService:
    """
    Service for AI-powered tarot reading generation
    """
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.ollama_timeout = settings.OLLAMA_TIMEOUT
    
    async def generate_tarot_reading(
        self,
        question: str,
        cards_drawn: List[Dict[str, Any]],
        reading_type: str = "general",
        detail: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a tarot reading using AI
        """
        try:
            # Prepare the prompt
            prompt = self._build_tarot_prompt(
                question, cards_drawn, reading_type, detail=detail or "quick"
            )
            
            used_model = self.ollama_model
            if llm_config and llm_config.get("api_key"):
                response = await self._call_external_llm(prompt, llm_config)
                used_model = llm_config.get("model", "external-llm")
            else:
                response = await self._call_ollama(prompt)
            
            # Process and structure the response
            structured_response = self._process_ai_response(response, cards_drawn, used_model)
            
            logger.info("Generated tarot reading", 
                       question=question, 
                       cards_count=len(cards_drawn),
                       reading_type=reading_type)
            
            return structured_response
            
        except Exception as e:
            logger.error("Failed to generate tarot reading", error=str(e))
            raise AIServiceException("Failed to generate reading", details={"error": str(e)})
    
    def _build_tarot_prompt(
        self,
        question: str,
        cards: List[Dict[str, Any]],
        reading_type: str,
        detail: str | None = None,
    ) -> str:
        """
        Build a comprehensive prompt for tarot reading
        """
        # Map reading type to spread positions (VI)
        rt = (reading_type or "").lower()
        spread_positions = []
        spread_name = "Tổng quát"
        if rt in ("1", "one", "single"):
            spread_name = "1 lá - Tổng quan"
            spread_positions = [
                "Tổng quan tình huống & lời khuyên trọng tâm",
            ]
        elif rt in ("3", "three"):
            spread_name = "3 lá - Quá khứ/Hiện tại/Tương lai"
            spread_positions = [
                "Quá khứ",
                "Hiện tại",
                "Tương lai",
            ]
        elif rt in ("5", "five"):
            spread_name = "5 lá - Phân tích nhanh"
            spread_positions = [
                "Tình huống hiện tại",
                "Thách thức chính",
                "Lời khuyên trọng tâm",
                "Yếu tố/ảnh hưởng bên ngoài",
                "Kết quả khả dĩ",
            ]
        elif rt in ("7", "seven"):
            spread_name = "7 lá - Horseshoe"
            spread_positions = [
                "Quá khứ",
                "Hiện tại",
                "Ảnh hưởng ẩn/tiềm thức",
                "Trở ngại",
                "Ảnh hưởng bên ngoài",
                "Hướng đi tốt nhất",
                "Kết quả",
            ]
        elif rt in ("10", "ten"):
            spread_name = "10 lá - Celtic Cross (đầy đủ)"
            spread_positions = [
                "(1) Hiện tại/Tình huống",
                "(2) Thách thức/Cản trở",
                "(3) Nền tảng/Quá khứ gần",
                "(4) Tương lai gần",
                "(5) Ý thức/Mục tiêu",
                "(6) Vô thức/Nền sâu",
                "(7) Bản thân/Thái độ",
                "(8) Môi trường/Người khác",
                "(9) Hy vọng & Nỗi sợ",
                "(10) Kết quả tiềm năng",
            ]

        # Build a JSON block of cards; quick mode keeps only essential fields to improve latency
        import json as _json
        compact_cards = []
        is_quick = (detail or "quick").lower() == "quick"
        # Each card may include 'is_reversed' and 'order_index' from frontend
        # Sort by order_index if provided to preserve draw order
        def _order_key(c: Dict[str, Any]):
            try:
                return int(c.get("order_index", 0))
            except Exception:
                return 0
        sorted_cards = sorted(cards, key=_order_key)

        from app.services.tarot_engine import TarotLogicEngine
        engine = TarotLogicEngine()
        processed_cards = engine.process_reversals_and_context(sorted_cards)
        occult_context = engine.build_system_context(processed_cards)

        for i, card in enumerate(processed_cards, 1):
            position_vi = spread_positions[i - 1] if i - 1 < len(spread_positions) else None
            if is_quick:
                compact_cards.append({
                    "index": i,
                    "position_vi": position_vi,
                    "id": card.get("id") or card.get("_id"),
                    "name": card.get("name"),
                    "name_vi": card.get("name_vi"),
                    "is_reversed": bool(card.get("is_reversed", False)),
                    "order_index": card.get("order_index", i),
                    "energy_state": card.get("energy_state"),
                    "active_meaning": card.get("active_meaning"),
                    "keywords": card.get("keywords_vi") or card.get("keywords"),
                })
            else:
                compact_cards.append({
                    "index": i,
                    "position_vi": position_vi,
                    "id": card.get("id") or card.get("_id"),
                    "name": card.get("name"),
                    "name_vi": card.get("name_vi"),
                    "suit": card.get("suit"),
                    "arcana": card.get("arcana") or card.get("card_type"),
                    "number": card.get("number"),
                    "keywords": card.get("keywords_vi") or card.get("keywords"),
                    "meanings_light": card.get("meanings_light"),
                    "meanings_shadow": card.get("meanings_shadow"),
                    "questions_to_ask": card.get("questions_to_ask"),
                    "energy_state": card.get("energy_state"),
                    "active_meaning": card.get("active_meaning"),
                    "order_index": card.get("order_index", i),
                })
        cards_text = _json.dumps(compact_cards, ensure_ascii=False, indent=2)
        
        # Spread guide text
        spread_guide = "\n".join([f"{idx+1}. {name}" for idx, name in enumerate(spread_positions)]) if spread_positions else "Không cố định vị trí; hãy diễn giải theo mạch logic."

        prompt = f"""
Bạn là một tarot reader chuyên nghiệp. Hãy trả lời HOÀN TOÀN BẰNG TIẾNG VIỆT, văn phong rõ ràng, ấm áp, giàu thấu cảm, và có tính thực tiễn.

CÂU HỎI: {question}

KIỂU TRẢI BÀI: {spread_name}

CÁC LÁ BÀI ĐÃ RÚT (JSON):
{cards_text}

SƠ ĐỒ VỊ TRÍ (nếu áp dụng):
{spread_guide}

{occult_context}
YÊU CẦU:
- Diễn giải từng lá (ý nghĩa chính, ánh sáng/bóng tối, liên hệ với câu hỏi)
- Với trải bài có vị trí: nêu rõ ý nghĩa từng lá theo đúng vị trí đã gán (position_vi)
- Tổng quan mối liên hệ giữa các lá
- Lời khuyên cụ thể, dễ áp dụng (liên hệ trực tiếp tới các vị trí trọng yếu của trải bài)
- Nếu là Celtic Cross 10 lá: tập trung phân tích (2,7,8,9) để hình thành lời khuyên hành động
- Gợi ý về năng lượng/thời điểm nếu phù hợp

LƯU Ý:
- Chỉ dùng TIẾNG VIỆT
- Tôn trọng hành trình cá nhân của người hỏi
- Cân bằng giữa truyền thống tarot và góc nhìn tâm lý hiện đại
- Độ dài khoảng 400–600 từ
"""
        return prompt.strip()
    
    async def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API to generate response
        """
        try:
            # Increase robustness with a proper timeout object and simple retries
            timeout = httpx.Timeout(
                connect=10.0,
                read=float(self.ollama_timeout) if self.ollama_timeout else 60.0,
                write=10.0,
                pool=10.0,
            )

            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": settings.OLLAMA_NUM_PREDICT,
                    "top_k": settings.OLLAMA_TOP_K,
                    "top_p": settings.OLLAMA_TOP_P,
                    "temperature": settings.OLLAMA_TEMPERATURE,
                    "num_ctx": settings.OLLAMA_NUM_CTX,
                    "keep_alive": settings.OLLAMA_KEEP_ALIVE,
                    **({"num_thread": settings.OLLAMA_NUM_THREAD} if settings.OLLAMA_NUM_THREAD else {}),
                },
            }

            async with httpx.AsyncClient(timeout=timeout) as client:
                last_exc: Optional[Exception] = None
                for attempt in range(1, 4):
                    try:
                        response = await client.post(url, json=payload)
                        if response.status_code == 200:
                            result = response.json()
                            return result.get("response", "")
                        else:
                            text = None
                            try:
                                text = response.text
                            except Exception:
                                text = None
                            logger.error(
                                "Ollama API non-200",
                                status_code=response.status_code,
                                url=url,
                                model=self.ollama_model,
                                response_preview=(text[:200] + "...") if text and len(text) > 200 else text,
                                attempt=attempt,
                            )
                            last_exc = AIServiceException(
                                "Ollama API error",
                                details={
                                    "status_code": response.status_code,
                                    "url": url,
                                    "model": self.ollama_model,
                                    "response": text,
                                },
                            )
                    except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                        last_exc = e
                        logger.error(
                            "Ollama call failed",
                            error=str(e),
                            url=url,
                            model=self.ollama_model,
                            attempt=attempt,
                        )
                        # Fallback: if localhost fails, retry with 127.0.0.1 immediately once
                        if "localhost" in url and attempt == 1:
                            alt_url = url.replace("localhost", "127.0.0.1")
                            try:
                                response = await client.post(alt_url, json=payload)
                                if response.status_code == 200:
                                    result = response.json()
                                    return result.get("response", "")
                                else:
                                    text = None
                                    try:
                                        text = response.text
                                    except Exception:
                                        text = None
                                    logger.error(
                                        "Ollama API non-200 (alt URL)",
                                        status_code=response.status_code,
                                        url=alt_url,
                                        model=self.ollama_model,
                                        response_preview=(text[:200] + "...") if text and len(text) > 200 else text,
                                    )
                            except Exception as e2:
                                logger.error("Alt URL also failed", url=alt_url, error=str(e2))
                    # simple backoff
                    await asyncio.sleep(0.5 * attempt)

                # After retries
                if isinstance(last_exc, AIServiceException):
                    raise last_exc
                else:
                    raise AIServiceException(
                        "AI service unavailable",
                        details={"url": url, "model": self.ollama_model, "error": str(last_exc) if last_exc else None},
                    )

        except AIServiceException:
            raise
        except Exception as e:
            logger.error("Failed to call Ollama API", error=str(e))
            raise AIServiceException(
                "Failed to call AI service",
                details={"url": self.ollama_url, "model": self.ollama_model, "error": str(e)},
            )

    async def stream_tarot_reading(
        self,
        question: str,
        cards_drawn: List[Dict[str, Any]],
        reading_type: str = "general",
        detail: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
    ):
        """Stream AI reading text chunks from Ollama or External LLM."""
        prompt = self._build_tarot_prompt(
            question, cards_drawn, reading_type, detail=detail or "quick"
        )

        if llm_config and llm_config.get("api_key"):
            async for chunk in self._stream_external_llm(prompt, llm_config):
                yield chunk
            return

        url = f"{self.ollama_url}/api/generate"
        
        request_model = self.ollama_model
        if llm_config and llm_config.get("provider", "").lower() == "ollama" and llm_config.get("model"):
            request_model = llm_config.get("model")
            
        # Tính toán linh hoạt token limit dựa trên số lượng lá bài
        num_cards = len(cards_drawn) if cards_drawn else 1
        # Mỗi lá bài cần khoảng 450 tokens để phân tích chi tiết. Cơ bản cần 400 tokens cho mở/kết.
        dynamic_predict = max(settings.OLLAMA_NUM_PREDICT, 400 + (num_cards * 450))
        # Context window cần lớn hơn Predict để chứa được cả câu hỏi, lịch sử và prompt (thêm ~800 tokens/lá)
        dynamic_ctx = max(settings.OLLAMA_NUM_CTX, 1500 + (num_cards * 800))

        payload = {
            "model": request_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": dynamic_predict,
                "top_k": settings.OLLAMA_TOP_K,
                "top_p": settings.OLLAMA_TOP_P,
                "temperature": settings.OLLAMA_TEMPERATURE,
                "num_ctx": dynamic_ctx,
                "keep_alive": settings.OLLAMA_KEEP_ALIVE,
                **({"num_thread": settings.OLLAMA_NUM_THREAD} if settings.OLLAMA_NUM_THREAD else {}),
            },
        }

        timeout = httpx.Timeout(
            connect=10.0,
            read=float(self.ollama_timeout) if self.ollama_timeout else 120.0,
            write=10.0,
            pool=10.0,
        )

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        text = None
                        try:
                            body_bytes = await response.aread()
                            text = body_bytes.decode("utf-8", errors="ignore")
                        except Exception:
                            text = None
                        logger.error(
                            "Ollama stream non-200",
                            status_code=response.status_code,
                            url=url,
                            model=self.ollama_model,
                            response_preview=(text[:200] + "...") if text and len(text) > 200 else text,
                        )
                        raise AIServiceException(
                            "Ollama API error",
                            details={"status_code": response.status_code, "url": url, "model": self.ollama_model, "response": text},
                        )

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            if isinstance(data, dict):
                                chunk = data.get("response")
                                if chunk:
                                    yield chunk
                                if data.get("done") is True:
                                    break
                            else:
                                # not a dict, just pass raw
                                yield line
                        except Exception:
                            # not json line, pass raw
                            yield line

        except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            logger.error("Ollama stream connection error", error=str(e), url=url, model=self.ollama_model)
            yield f"\n\n\n*(Cảnh báo: Kết nối tới máy chủ AI đang bị quá tải hoặc gián đoạn. Xin vui lòng chờ một lát rồi thử lại!)*"
            return
        except AIServiceException as e:
            yield f"\n\n\n*(Cảnh báo: Lỗi hệ thống AI - {e.message})*"
            return
        except Exception as e:
            logger.error("Failed streaming from Ollama", error=str(e))
            yield f"\n\n\n*(Cảnh báo: Có lỗi xảy ra trong quá trình nhận dữ liệu từ AI. Xin vui lòng thử lại!)*"
            return

    async def _call_external_llm(self, prompt: str, llm_config: Dict[str, Any]) -> str:
        provider = llm_config.get("provider", "").lower()
        api_key = llm_config.get("api_key")
        model = llm_config.get("model")

        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
        elif provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
        elif provider == "gemini":
            url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        else:
            raise AIServiceException("Unsupported LLM provider", details={"provider": provider})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Bạn là một Tarot Reader chuyên nghiệp. Hãy trả lời BẰNG TIẾNG VIỆT, văn phong ấm áp, thấu cảm và sâu sắc. Trả lời trực tiếp vào vấn đề."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": 0.7
        }
        
        timeout = httpx.Timeout(60.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    logger.error("External LLM API error", status=response.status_code, body=response.text)
                    raise AIServiceException("External LLM API error")
        except Exception as e:
            logger.error("Failed to call External LLM", error=str(e))
            raise AIServiceException("Failed to call external AI service")
        return ""

    async def _stream_external_llm(self, prompt: str, llm_config: Dict[str, Any]):
        provider = llm_config.get("provider", "").lower()
        api_key = llm_config.get("api_key")
        model = llm_config.get("model")

        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
        elif provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
        elif provider == "gemini":
            url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        else:
            raise AIServiceException("Unsupported LLM provider", details={"provider": provider})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Bạn là một Tarot Reader chuyên nghiệp. Hãy trả lời BẰNG TIẾNG VIỆT, văn phong ấm áp, thấu cảm và sâu sắc. Trả lời trực tiếp vào vấn đề."},
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "temperature": 0.7
        }
        
        timeout = httpx.Timeout(120.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        text = await response.aread()
                        logger.error("External LLM stream error", body=text)
                        raise AIServiceException("External LLM API stream error")

                    async for line in response.aiter_lines():
                        if isinstance(line, bytes):
                            try:
                                line = line.decode("utf-8", errors="ignore")
                            except Exception:
                                pass
                        if isinstance(line, str) and line.startswith("data:"):
                            data_str = line[5:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                                if content:
                                    yield content
                            except Exception:
                                pass
        except Exception as e:
            logger.error("Failed external LLM stream", error=str(e))
            yield f"\n\n\n*(Cảnh báo: Kết nối tới API của {provider.upper()} bị gián đoạn. Xin vui lòng kiểm tra lại API Key hoặc mạng lưới của bạn!)*"
            return
    
    def _process_ai_response(self, response: str, cards: List[Dict[str, Any]], model_used: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and structure the AI response
        """
        # Simple processing - in a real implementation, you might use more sophisticated parsing
        return {
            "ai_response": response,
            "ai_summary": self._extract_summary(response),
            "ai_advice": self._extract_advice(response),
            "cards_interpreted": len(cards),
            "response_length": len(response),
            "model_used": model_used or self.ollama_model,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _extract_summary(self, response: str) -> str:
        """
        Extract a brief summary from the AI response
        """
        # Simple extraction - take first 100 characters
        return response[:100] + "..." if len(response) > 100 else response
    
    def _extract_advice(self, response: str) -> str:
        """
        Extract practical advice from the AI response
        """
        # Look for advice sections
        advice_keywords = ["advice", "guidance", "recommend", "suggest"]
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in advice_keywords):
                return line.strip()
        
        # Fallback: return last few sentences
        sentences = response.split('.')
        if len(sentences) >= 2:
            return '. '.join(sentences[-2:]).strip()
        
        return response[:150] + "..." if len(response) > 150 else response
    
    async def test_ai_connection(self) -> Dict[str, Any]:
        """
        Test the AI service connection
        """
        try:
            # Test with a simple prompt
            test_prompt = "Hello, can you tell me about tarot cards?"
            response = await self._call_ollama(test_prompt)
            
            return {
                "status": "success",
                "model": self.ollama_model,
                "response_length": len(response),
                "test_response": response[:100] + "..." if len(response) > 100 else response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model": self.ollama_model
            }
    
    async def get_available_models(self) -> List[str]:
        """
        Get list of available Ollama models
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                
                if response.status_code == 200:
                    data = response.json()
                    models = [model.get("name", "") for model in data.get("models", [])]
                    return models
                else:
                    return []
                    
        except Exception as e:
            logger.error("Failed to get available models", error=str(e))
            return []


