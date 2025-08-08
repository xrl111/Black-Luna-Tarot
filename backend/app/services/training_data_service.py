# 🎯 Tarot System - Training Data Service
"""
Service for collecting and processing training data for Llama3 fine-tuning
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
import structlog
from datetime import datetime

from app.database.models import (
    Reading, AITrainingData, ConversationSession, User,
    QuestionAnalysis, UserContext, CulturalContext, 
    AIResponseAnalysis, UserFeedbackAnalysis, BehavioralData,
    TrainingQualityMetrics
)
from app.core.exceptions import DatabaseException

logger = structlog.get_logger()

class TrainingDataService:
    """
    Service for managing training data collection and processing
    """
    
    def __init__(self, readings_collection: AsyncIOMotorCollection,
                 training_data_collection: AsyncIOMotorCollection,
                 users_collection: AsyncIOMotorCollection,
                 conversation_collection: AsyncIOMotorCollection):
        self.readings_collection = readings_collection
        self.training_data_collection = training_data_collection
        self.users_collection = users_collection
        self.conversation_collection = conversation_collection
    
    async def collect_training_data_from_reading(self, reading_id: str) -> Optional[AITrainingData]:
        """
        Collect comprehensive training data from a reading
        """
        try:
            # Get the reading
            reading_doc = await self.readings_collection.find_one({"_id": ObjectId(reading_id)})
            if not reading_doc:
                logger.warning("Reading not found for training data collection", reading_id=reading_id)
                return None
            
            reading = Reading(**reading_doc)
            
            # Get user context if available
            user_context = {}
            cultural_context = {}
            if reading.user_id:
                user_doc = await self.users_collection.find_one({"_id": reading.user_id})
                if user_doc:
                    user = User(**user_doc)
                    user_context = self._build_user_context(user)
                    cultural_context = self._build_cultural_context(user)
            
            # Build question analysis
            question_analysis = self._analyze_question(reading.question)
            
            # Build AI response analysis
            ai_response_analysis = self._analyze_ai_response(reading)
            
            # Build user feedback analysis
            user_feedback_analysis = self._analyze_user_feedback(reading)
            
            # Build behavioral data
            behavioral_data = self._analyze_behavioral_data(reading)
            
            # Build quality metrics
            quality_metrics = self._calculate_quality_metrics(reading, user_context)
            
            # Create training data
            training_data = AITrainingData(
                reading_id=reading.id,
                user_id=reading.user_id,
                session_id=reading.session_id,
                
                # Question analysis
                question=reading.question,
                question_category=reading.question_category,
                question_complexity=reading.question_complexity,
                question_emotion=reading.question_emotion,
                question_context=reading.question_context,
                question_urgency=reading.question_urgency,
                
                # Context data
                user_context=user_context,
                cultural_context=cultural_context,
                cards_context=self._build_cards_context(reading.cards_drawn),
                cards_combination=[card.card_name for card in reading.cards_drawn],
                spread_type=reading.reading_spread,
                spread_positions=[card.position_meaning for card in reading.cards_drawn],
                
                # AI response analysis
                ai_response=reading.ai_response,
                ai_response_sections=reading.ai_response_sections,
                ai_response_length=len(reading.ai_response),
                ai_response_tone=reading.ai_response_tone,
                ai_response_complexity=reading.ai_response_complexity,
                ai_actionable_advice=reading.ai_actionable_advice,
                ai_emotional_support=reading.ai_emotional_support,
                
                # User feedback
                user_rating=reading.user_rating,
                user_feedback=reading.user_feedback,
                user_satisfaction=reading.user_satisfaction,
                user_action_taken=reading.user_action_taken,
                user_accuracy_perception=reading.user_accuracy_perception,
                user_usefulness_score=reading.user_usefulness_score,
                user_clarity_score=reading.user_clarity_score,
                
                # Behavioral data
                user_engagement=behavioral_data.dict(),
                reading_duration=reading.reading_duration,
                interaction_pattern=reading.user_interaction_pattern,
                
                # Training metadata
                model_version=reading.ai_model_used,
                training_priority=quality_metrics.training_priority,
                quality_score=quality_metrics.quality_score,
                minimum_rating_threshold=quality_metrics.minimum_rating_threshold,
                minimum_engagement_threshold=quality_metrics.minimum_engagement_threshold,
                verified_user=quality_metrics.verified_user,
                return_visitor=quality_metrics.return_visitor
            )
            
            # Save to database
            result = await self.training_data_collection.insert_one(training_data.dict(by_alias=True))
            training_data.id = result.inserted_id
            
            logger.info("Training data collected successfully", 
                       reading_id=reading_id, 
                       training_data_id=str(training_data.id))
            
            return training_data
            
        except Exception as e:
            logger.error("Failed to collect training data", reading_id=reading_id, error=str(e))
            raise DatabaseException("Failed to collect training data")
    
    def _build_user_context(self, user: User) -> Dict[str, Any]:
        """Build comprehensive user context"""
        return {
            "user_id": str(user.id),
            "experience_level": user.preferences.experience_level,
            "belief_system": user.preferences.belief_system,
            "cultural_background": user.preferences.cultural_background,
            "reading_frequency": user.preferences.reading_frequency,
            "preferred_style": user.preferences.reading_style,
            "language_preference": user.preferences.language,
            "total_readings": user.statistics.total_readings,
            "average_rating": user.statistics.average_rating,
            "engagement_score": user.statistics.engagement_score,
            "return_visitor_count": user.statistics.return_visitor_count
        }
    
    def _build_cultural_context(self, user: User) -> Dict[str, Any]:
        """Build cultural context"""
        return {
            "user_culture": user.preferences.cultural_background,
            "belief_system": user.preferences.belief_system,
            "tarot_tradition": user.preferences.tarot_tradition,
            "language_preference": user.preferences.language,
            "cultural_sensitivity": "high",  # Default for Vietnamese context
            "spiritual_background": "vietnamese_spiritual"
        }
    
    def _analyze_question(self, question: str) -> QuestionAnalysis:
        """Analyze question for training data"""
        # Simple analysis - in production, use NLP/ML
        question_lower = question.lower()
        
        # Determine category
        categories = {
            "career": ["việc", "công việc", "sự nghiệp", "thăng tiến", "chuyển việc"],
            "love": ["tình yêu", "tình cảm", "mối quan hệ", "hôn nhân", "người yêu"],
            "health": ["sức khỏe", "bệnh", "thể chất", "tinh thần", "healing"],
            "finance": ["tiền bạc", "tài chính", "đầu tư", "kinh doanh", "tiết kiệm"],
            "spiritual": ["linh hồn", "tâm linh", "mục đích", "định mệnh", "thiền"]
        }
        
        category = "general"
        for cat, keywords in categories.items():
            if any(keyword in question_lower for keyword in keywords):
                category = cat
                break
        
        # Determine complexity
        complexity = "medium"
        if len(question.split()) < 5:
            complexity = "simple"
        elif len(question.split()) > 15:
            complexity = "complex"
        
        # Determine emotion
        emotions = {
            "uncertain": ["có nên", "có thể", "không biết", "lo lắng"],
            "anxious": ["lo", "sợ", "hoảng", "stress"],
            "hopeful": ["hy vọng", "mong muốn", "ước mơ", "tương lai"],
            "confused": ["bối rối", "không hiểu", "mâu thuẫn", "lẫn lộn"]
        }
        
        emotion = "neutral"
        for emo, keywords in emotions.items():
            if any(keyword in question_lower for keyword in keywords):
                emotion = emo
                break
        
        return QuestionAnalysis(
            original_question=question,
            question_category=category,
            question_complexity=complexity,
            question_emotion=emotion,
            question_context=None,
            question_urgency="medium",
            question_keywords=question.split(),
            question_sentiment="neutral"
        )
    
    def _analyze_ai_response(self, reading: Reading) -> AIResponseAnalysis:
        """Analyze AI response for training data"""
        response = reading.ai_response
        
        # Determine tone
        tone_keywords = {
            "supportive": ["hỗ trợ", "đồng hành", "khuyến khích", "tích cực"],
            "analytical": ["phân tích", "xem xét", "đánh giá", "logic"],
            "spiritual": ["tâm linh", "năng lượng", "vũ trụ", "thiền"]
        }
        
        tone = "supportive"
        response_lower = response.lower()
        for t, keywords in tone_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                tone = t
                break
        
        # Determine complexity
        complexity = "medium"
        if len(response.split()) < 100:
            complexity = "simple"
        elif len(response.split()) > 300:
            complexity = "complex"
        
        # Check for actionable advice
        actionable_keywords = ["nên", "cần", "hãy", "thử", "bắt đầu", "thay đổi"]
        actionable_advice = any(keyword in response_lower for keyword in actionable_keywords)
        
        # Check for emotional support
        emotional_keywords = ["hiểu", "đồng cảm", "hỗ trợ", "khuyến khích", "an ủi"]
        emotional_support = any(keyword in response_lower for keyword in emotional_keywords)
        
        return AIResponseAnalysis(
            full_response=response,
            response_sections=reading.ai_response_sections,
            response_tone=tone,
            response_complexity=complexity,
            actionable_advice=actionable_advice,
            emotional_support=emotional_support,
            response_length=len(response),
            response_quality_metrics={
                "readability": 0.8,
                "coherence": 0.9,
                "relevance": 0.85
            }
        )
    
    def _analyze_user_feedback(self, reading: Reading) -> UserFeedbackAnalysis:
        """Analyze user feedback for training data"""
        return UserFeedbackAnalysis(
            rating=reading.user_rating,
            feedback_text=reading.user_feedback,
            satisfaction_level=reading.user_satisfaction,
            action_taken=reading.user_action_taken,
            emotional_response=reading.user_emotion,
            accuracy_perception=reading.user_accuracy_perception,
            usefulness_score=reading.user_usefulness_score,
            clarity_score=reading.user_clarity_score,
            engagement_metrics={
                "reading_duration": reading.reading_duration,
                "cards_explored": reading.cards_explored,
                "shared_reading": reading.shared_reading,
                "saved_reading": reading.saved_reading,
                "revisited_reading": reading.revisited_reading
            }
        )
    
    def _analyze_behavioral_data(self, reading: Reading) -> BehavioralData:
        """Analyze behavioral data for training"""
        engagement_score = 0.5  # Default
        
        # Calculate engagement score based on interactions
        interactions = 0
        if reading.cards_explored:
            interactions += 1
        if reading.shared_reading:
            interactions += 1
        if reading.saved_reading:
            interactions += 1
        if reading.revisited_reading:
            interactions += 1
        
        engagement_score = min(1.0, interactions / 4.0)
        
        return BehavioralData(
            reading_duration=reading.reading_duration,
            interaction_pattern=reading.user_interaction_pattern,
            cards_explored=reading.cards_explored,
            shared_reading=reading.shared_reading,
            saved_reading=reading.saved_reading,
            revisited_reading=reading.revisited_reading,
            session_metrics={
                "session_id": reading.session_id,
                "reading_type": reading.reading_type,
                "cards_count": len(reading.cards_drawn)
            },
            engagement_score=engagement_score
        )
    
    def _calculate_quality_metrics(self, reading: Reading, user_context: Dict[str, Any]) -> TrainingQualityMetrics:
        """Calculate quality metrics for training data"""
        quality_score = 0.5  # Default
        
        # Factors that increase quality
        if reading.user_rating and reading.user_rating >= 4:
            quality_score += 0.2
        if reading.reading_duration > 120:  # More than 2 minutes
            quality_score += 0.1
        if reading.user_feedback and len(reading.user_feedback) > 10:
            quality_score += 0.1
        if reading.cards_explored:
            quality_score += 0.05
        if reading.saved_reading:
            quality_score += 0.05
        
        # User factors
        if user_context.get("return_visitor_count", 0) > 0:
            quality_score += 0.1
        if user_context.get("total_readings", 0) > 5:
            quality_score += 0.05
        
        quality_score = min(1.0, quality_score)
        
        # Determine training priority
        training_priority = 5  # Default
        if quality_score > 0.8:
            training_priority = 8
        elif quality_score > 0.6:
            training_priority = 6
        elif quality_score < 0.4:
            training_priority = 3
        
        return TrainingQualityMetrics(
            quality_score=quality_score,
            training_priority=training_priority,
            minimum_rating_threshold=3,
            minimum_engagement_threshold=60.0,
            verified_user=user_context.get("total_readings", 0) > 0,
            return_visitor=user_context.get("return_visitor_count", 0) > 0,
            data_quality_indicators={
                "has_rating": reading.user_rating is not None,
                "has_feedback": reading.user_feedback is not None,
                "has_engagement": reading.reading_duration > 60,
                "user_experience": user_context.get("total_readings", 0)
            }
        )
    
    def _build_cards_context(self, cards_drawn: List) -> str:
        """Build formatted cards context"""
        context_parts = []
        for card in cards_drawn:
            context_parts.append(
                f"{card.card_name} ({card.card_name_vi}) - {card.traditional_meaning} - {card.orientation}"
            )
        return " | ".join(context_parts)
    
    async def get_high_quality_training_data(self, limit: int = 100) -> List[AITrainingData]:
        """
        Get high-quality training data for fine-tuning
        """
        try:
            # Query for high-quality training data
            pipeline = [
                {
                    "$match": {
                        "quality_score": {"$gte": 0.7},
                        "user_rating": {"$gte": 4},
                        "reading_duration": {"$gte": 60},
                        "verified_user": True
                    }
                },
                {"$sort": {"quality_score": -1, "training_priority": -1}},
                {"$limit": limit}
            ]
            
            cursor = self.training_data_collection.aggregate(pipeline)
            documents = await cursor.to_list(length=limit)
            
            training_data = [AITrainingData(**doc) for doc in documents]
            
            logger.info("Retrieved high-quality training data", 
                       count=len(training_data),
                       limit=limit)
            
            return training_data
            
        except Exception as e:
            logger.error("Failed to get high-quality training data", error=str(e))
            raise DatabaseException("Failed to retrieve training data")
    
    async def export_training_data_for_llama3(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Export training data in Llama3 format
        """
        try:
            training_data = await self.get_high_quality_training_data(limit)
            
            llama3_format = []
            for data in training_data:
                # Build prompt
                prompt = self._build_llama3_prompt(data)
                
                # Build response
                response = self._build_llama3_response(data)
                
                llama3_format.append({
                    "input": prompt,
                    "output": response,
                    "quality_score": data.quality_score,
                    "user_rating": data.user_rating,
                    "training_priority": data.training_priority
                })
            
            logger.info("Exported training data for Llama3", 
                       count=len(llama3_format),
                       format="llama3")
            
            return llama3_format
            
        except Exception as e:
            logger.error("Failed to export training data for Llama3", error=str(e))
            raise DatabaseException("Failed to export training data")
    
    def _build_llama3_prompt(self, data: AITrainingData) -> str:
        """Build Llama3 prompt format"""
        prompt = f"""<|im_start|>system
You are a professional Vietnamese tarot reader using Llama 3. 
Provide insightful, compassionate, and practical tarot readings.
<|im_end|>

<|im_start|>user
Question: {data.question}
Context: {data.user_context}
Cards: {data.cards_context}
Reading Type: {data.spread_type}
<|im_end|>"""
        
        return prompt
    
    def _build_llama3_response(self, data: AITrainingData) -> str:
        """Build Llama3 response format"""
        return f"<|im_start|>assistant\n{data.ai_response}\n<|im_end|>"
