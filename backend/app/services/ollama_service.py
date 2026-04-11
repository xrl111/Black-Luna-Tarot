#  Tarot System - Ollama AI Service
"""
Ollama integration service for AI-powered tarot readings
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
import httpx
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaRequest(BaseModel):
    """Ollama API request model"""
    model: str
    prompt: str
    stream: bool = False
    options: Optional[Dict[str, Any]] = None

class OllamaResponse(BaseModel):
    """Ollama API response model"""
    model: str
    created_at: str
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

class TarotReadingRequest(BaseModel):
    """Tarot reading request model"""
    cards: List[str]
    question: str
    spread_type: str = "three_card"
    user_context: Optional[str] = None

class TarotReadingResponse(BaseModel):
    """Tarot reading response model"""
    reading: str
    interpretation: str
    advice: str
    confidence: float
    model_used: str
    processing_time: float

class OllamaService:
    """
    Service for interacting with Ollama local LLM
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.default_model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Generate response from Ollama"""
        
        model = model or self.default_model
        
        request_data = OllamaRequest(
            model=model,
            prompt=prompt,
            stream=False,
            options=options or {}
        )
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=request_data.dict(exclude_none=True)
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return None
    
    def _create_tarot_prompt(self, request: TarotReadingRequest) -> str:
        """Create a specialized prompt for tarot reading"""
        
        prompt = f"""
You are a professional tarot reader with deep knowledge of tarot symbolism and interpretation. 
You are using the latest Llama 3 model, which provides enhanced understanding and more nuanced responses.
Please provide a detailed, insightful, and compassionate tarot reading.

SPREAD TYPE: {request.spread_type.upper()}
CARDS DRAWN: {', '.join(request.cards)}
QUESTION: {request.question}

{f"USER CONTEXT: {request.user_context}" if request.user_context else ""}

Please provide your reading in the following format:

**CARD INTERPRETATIONS:**
[Interpret each card individually and its position meaning, considering both traditional symbolism and modern psychological insights]

**OVERALL READING:**
[Provide a comprehensive interpretation of how the cards work together, highlighting patterns and themes]

**GUIDANCE & ADVICE:**
[Offer practical advice and guidance based on the reading, focusing on actionable steps]

**ENERGY & TIMING:**
[Discuss the energy and timing aspects of the reading, including astrological and elemental influences]

Please be:
- Insightful and detailed with enhanced Llama 3 capabilities
- Compassionate and supportive
- Practical and actionable
- Respectful of the querent's journey
- Based on traditional tarot wisdom with modern psychological understanding
- Clear and accessible in your language

Your response should be approximately 400-600 words, taking advantage of Llama 3's improved reasoning capabilities.
"""
        return prompt.strip()
    
    async def generate_tarot_reading(
        self, 
        request: TarotReadingRequest
    ) -> Optional[TarotReadingResponse]:
        """Generate a tarot reading using Ollama"""
        
        import time
        start_time = time.time()
        
        # Create specialized prompt
        prompt = self._create_tarot_prompt(request)
        
        # Generate response
        response_text = await self.generate_response(prompt)
        
        if not response_text:
            return None
        
        processing_time = time.time() - start_time
        
        # Parse response into structured format
        try:
            # Try to extract sections from response
            sections = self._parse_tarot_response(response_text)
            
            return TarotReadingResponse(
                reading=response_text,
                interpretation=sections.get("interpretation", ""),
                advice=sections.get("advice", ""),
                confidence=0.85,  # Default confidence
                model_used=self.default_model,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Failed to parse tarot response: {e}")
            # Return basic response if parsing fails
            return TarotReadingResponse(
                reading=response_text,
                interpretation=response_text,
                advice="",
                confidence=0.7,
                model_used=self.default_model,
                processing_time=processing_time
            )
    
    def _parse_tarot_response(self, response: str) -> Dict[str, str]:
        """Parse tarot response into sections"""
        sections = {
            "interpretation": "",
            "advice": ""
        }
        
        # Simple parsing based on common patterns
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "overall reading" in line.lower() or "interpretation" in line.lower():
                current_section = "interpretation"
            elif "guidance" in line.lower() or "advice" in line.lower():
                current_section = "advice"
            elif current_section and line:
                sections[current_section] += line + " "
        
        return sections
    
    async def train_on_user_data(
        self, 
        user_readings: List[Dict[str, Any]]
    ) -> bool:
        """Train the model on user-specific data (future feature)"""
        # This is a placeholder for future fine-tuning capabilities
        logger.info("Training on user data - feature not yet implemented")
        return True
    
    async def get_model_info(self, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        model = model or self.default_model
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json={"name": model}
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None

# Global service instance
ollama_service = OllamaService()

# Convenience functions
async def get_tarot_reading(
    cards: List[str], 
    question: str, 
    spread_type: str = "three_card",
    user_context: Optional[str] = None
) -> Optional[TarotReadingResponse]:
    """Convenience function to get a tarot reading"""
    
    request = TarotReadingRequest(
        cards=cards,
        question=question,
        spread_type=spread_type,
        user_context=user_context
    )
    
    async with OllamaService() as service:
        return await service.generate_tarot_reading(request)

async def check_ollama_health() -> bool:
    """Convenience function to check Ollama health"""
    async with OllamaService() as service:
        return await service.health_check()

