#  Tarot System - Pydantic Models for MongoDB
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, validator
from bson import ObjectId

# Custom ObjectId field for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    def __repr__(self):
        return f"PyObjectId('{super().__repr__()}')"

    def __str__(self):
        return str(super().__str__())

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, PyObjectId):
            return str(self) == str(other)
        return False

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        if field_schema is not None:
            field_schema.update(type="string")
        return field_schema

    def __getstate__(self):
        return str(self)

    def __setstate__(self, state):
        self.__init__(state)

# Base model with common fields
class BaseDocument(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# ============================================================================
# TAROT CARDS MODELS
# ============================================================================

class TarotCard(BaseDocument):
    name: str = Field(..., description="English card name")
    name_vi: str = Field(..., description="Vietnamese card name")
    suit: str = Field(..., description="Card suit")
    number: str = Field(..., description="Card number (as string to handle '0' for The Fool)")
    court_rank: Optional[str] = Field(None, description="Court card rank")
    arcana: str = Field(..., description="Major or Minor Arcana")
    
    # Meanings
    meaning_upright: str = Field(..., description="Upright interpretation")
    meaning_reversed: str = Field(..., description="Reversed interpretation")
    description: str = Field(..., description="Detailed description")
    
    # Rich meanings from dataset
    fortune_telling: List[str] = Field(default=[], description="Fortune telling interpretations")
    keywords: List[str] = Field(default=[], description="Card keywords")
    meanings_light: List[str] = Field(default=[], description="Light/upright meanings")
    meanings_shadow: List[str] = Field(default=[], description="Shadow/reversed meanings")
    
    # Esoteric associations
    archetype: Optional[str] = Field(None, description="Archetype")
    hebrew_alphabet: Optional[str] = Field(None, description="Hebrew alphabet association")
    numerology: Optional[str] = Field(None, description="Numerological meaning")
    elemental: Optional[str] = Field(None, description="Elemental association")
    mythical_spiritual: Optional[str] = Field(None, description="Mythical/spiritual associations")
    
    # Astrological associations
    element: Optional[str] = Field(None, description="Associated element")
    planet: Optional[str] = Field(None, description="Associated planet")
    zodiac: Optional[str] = Field(None, description="Associated zodiac sign")
    astrology: Optional[str] = Field(None, description="Astrological associations")
    
    # Interactive elements
    questions_to_ask: List[str] = Field(default=[], description="Questions to ask when this card appears")
    affirmation: Optional[str] = Field(None, description="Affirmation for this card")
    
    # Visual and metadata
    image_url: str = Field(..., description="Card image URL")
    image_filename: str = Field(..., description="Original image filename")
    card_type: str = Field(..., description="Major or minor arcana")
    astrological_significance: Optional[str] = Field(None, description="Astrological meaning")
    
    # Vietnamese translations
    name_vi_alt: Optional[str] = Field(None, description="Alternative Vietnamese name")
    meaning_upright_vi: Optional[str] = Field(None, description="Vietnamese upright meaning")
    meaning_reversed_vi: Optional[str] = Field(None, description="Vietnamese reversed meaning")
    keywords_vi: List[str] = Field(default=[], description="Vietnamese keywords")
    description_vi: Optional[str] = Field(None, description="Vietnamese description")

class TarotCardCreate(BaseModel):
    name: str
    name_vi: str
    suit: str
    number: str
    court_rank: Optional[str] = None
    arcana: str
    meaning_upright: str
    meaning_reversed: str
    description: str
    fortune_telling: List[str] = []
    keywords: List[str] = []
    meanings_light: List[str] = []
    meanings_shadow: List[str] = []
    archetype: Optional[str] = None
    hebrew_alphabet: Optional[str] = None
    numerology: Optional[str] = None
    elemental: Optional[str] = None
    mythical_spiritual: Optional[str] = None
    element: Optional[str] = None
    planet: Optional[str] = None
    zodiac: Optional[str] = None
    astrology: Optional[str] = None
    questions_to_ask: List[str] = []
    affirmation: Optional[str] = None
    image_url: str
    image_filename: str
    card_type: str
    astrological_significance: Optional[str] = None
    name_vi_alt: Optional[str] = None
    meaning_upright_vi: Optional[str] = None
    meaning_reversed_vi: Optional[str] = None
    keywords_vi: List[str] = []
    description_vi: Optional[str] = None

class TarotCardUpdate(BaseModel):
    name: Optional[str] = None
    name_vi: Optional[str] = None
    meaning_upright: Optional[str] = None
    meaning_reversed: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    image_url: Optional[str] = None

# ============================================================================
# USER MODELS
# ============================================================================

class UserPreferences(BaseModel):
    reading_style: str = Field(default="detailed", description="Reading style preference")
    language: str = Field(default="vi", description="Language preference")
    theme: str = Field(default="auto", description="Theme preference")
    notifications: Dict[str, bool] = Field(default_factory=dict, description="Notification settings")
    
    # Enhanced preferences for training data
    experience_level: str = Field(default="beginner", description="User's tarot experience level")
    belief_system: str = Field(default="spiritual_but_practical", description="User's belief system")
    tarot_tradition: str = Field(default="rider_waite", description="Preferred tarot tradition")
    cultural_background: str = Field(default="vietnamese", description="Cultural background")
    reading_frequency: str = Field(default="occasional", description="How often user does readings")

class UserStatistics(BaseModel):
    total_readings: int = Field(default=0, description="Total readings performed")
    favorite_cards: List[str] = Field(default=[], description="Most frequently drawn cards")
    average_rating: float = Field(default=0.0, description="Average rating given")
    last_reading_date: Optional[datetime] = None
    reading_streak: int = Field(default=0, description="Consecutive days with readings")
    
    # Enhanced statistics for training data
    total_reading_time: float = Field(default=0.0, description="Total time spent on readings in minutes")
    average_reading_duration: float = Field(default=0.0, description="Average time per reading")
    feedback_given_count: int = Field(default=0, description="Number of times user gave feedback")
    return_visitor_count: int = Field(default=0, description="Number of return visits")
    preferred_reading_types: List[str] = Field(default=[], description="Most used reading types")
    engagement_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall engagement score")

class User(BaseModel):
    id: Union[int, str] = Field(..., description="User ID (Integer for Postgres)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="Display name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    
    # Authentication
    password_hash: Optional[str] = Field(None, description="Hashed password")
    auth_provider: str = Field(default="email", description="Authentication provider")
    auth_provider_id: Optional[str] = Field(None, description="External provider ID")
    
    # User data
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    statistics: UserStatistics = Field(default_factory=UserStatistics)
    
    # Account status
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verification status")
    role: str = Field(default="user", description="User role")
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: Optional[str] = None
    auth_provider: str = "email"
    auth_provider_id: Optional[str] = None
    avatar_url: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

class GoogleAuthPayload(BaseModel):
    id_token: str = Field(..., description="Google ID Token from frontend")

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    is_active: Optional[bool] = None
    last_login: Optional[datetime] = None

# ============================================================================
# READING MODELS
# ============================================================================

class CardDrawn(BaseModel):
    card_id: str = Field(..., min_length=1, max_length=100, description="Reference to tarot card")
    position: int = Field(..., ge=1, le=78, description="Position in spread")
    orientation: str = Field(..., description="Upright or reversed")
    position_meaning: str = Field(..., min_length=1, max_length=500, description="What this position represents")
    interpretation: str = Field(..., min_length=1, max_length=2000, description="AI-generated interpretation")
    keywords: List[str] = Field(default=[], max_items=20, description="Key insights")
    
    # Enhanced card data for training
    card_name: str = Field(..., min_length=1, max_length=100, description="Card name for easy reference")
    card_name_vi: str = Field(..., min_length=1, max_length=100, description="Vietnamese card name")
    traditional_meaning: str = Field(..., min_length=1, max_length=1000, description="Traditional card meaning")
    element: Optional[str] = Field(None, description="Associated element")
    zodiac: Optional[str] = Field(None, description="Associated zodiac sign")
    planet: Optional[str] = Field(None, description="Associated planet")
    astrological_significance: Optional[str] = Field(None, max_length=500, description="Astrological meaning")
    card_type: str = Field(..., description="Major or minor arcana")
    suit: str = Field(..., description="Card suit")
    number: str = Field(..., description="Card number")
    
    @validator('orientation')
    def validate_orientation(cls, v):
        valid_orientations = ['upright', 'reversed']
        if v.lower() not in valid_orientations:
            raise ValueError(f'Orientation must be one of: {", ".join(valid_orientations)}')
        return v.lower()
    
    @validator('element')
    def validate_element(cls, v):
        if v is not None:
            valid_elements = ['fire', 'water', 'air', 'earth']
            if v.lower() not in valid_elements:
                raise ValueError(f'Element must be one of: {", ".join(valid_elements)}')
            return v.lower()
        return v
    
    @validator('zodiac')
    def validate_zodiac(cls, v):
        if v is not None:
            valid_zodiacs = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
            if v.lower() not in valid_zodiacs:
                raise ValueError(f'Zodiac must be one of: {", ".join(valid_zodiacs)}')
            return v.lower()
        return v
    
    @validator('planet')
    def validate_planet(cls, v):
        if v is not None:
            valid_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
            if v.lower() not in valid_planets:
                raise ValueError(f'Planet must be one of: {", ".join(valid_planets)}')
            return v.lower()
        return v
    
    @validator('card_type')
    def validate_card_type(cls, v):
        valid_types = ['major', 'minor']
        if v.lower() not in valid_types:
            raise ValueError(f'Card type must be one of: {", ".join(valid_types)}')
        return v.lower()
    
    @validator('suit')
    def validate_suit(cls, v):
        valid_suits = ['wands', 'cups', 'swords', 'pentacles', 'major', 'trump']
        if v.lower() not in valid_suits:
            raise ValueError(f'Suit must be one of: {", ".join(valid_suits)}')
        return v.lower()
    
    @validator('position_meaning')
    def validate_position_meaning(cls, v):
        if not v or not v.strip():
            raise ValueError('Position meaning cannot be empty')
        return v.strip()
    
    @validator('interpretation')
    def validate_interpretation(cls, v):
        if not v or not v.strip():
            raise ValueError('Interpretation cannot be empty')
        return v.strip()

class Reading(BaseDocument):
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User reference")
    
    # Reading details
    question: str = Field(..., description="User's question")
    reading_type: str = Field(..., description="Type of reading")
    reading_spread: str = Field(..., description="Spread used")
    
    # Enhanced question analysis for training
    question_category: str = Field(default="general", description="Question category (career, love, health, etc.)")
    question_complexity: str = Field(default="medium", description="Question complexity (simple, medium, complex)")
    question_emotion: Optional[str] = Field(None, description="Emotion detected in question")
    question_context: Optional[str] = Field(None, description="Additional context about the question")
    question_urgency: str = Field(default="medium", description="Question urgency level")
    
    # Cards drawn
    cards_drawn: List[CardDrawn] = Field(..., description="Cards drawn in reading")
    
    # AI response
    ai_response: str = Field(..., description="Full AI interpretation")
    ai_summary: Optional[str] = Field(None, description="Brief summary")
    ai_advice: Optional[str] = Field(None, description="Specific advice")
    
    # Enhanced AI response analysis
    ai_response_sections: Dict[str, str] = Field(default_factory=dict, description="Structured response sections")
    ai_response_tone: str = Field(default="neutral", description="Response tone (supportive, analytical, spiritual)")
    ai_response_complexity: str = Field(default="medium", description="Response complexity level")
    ai_actionable_advice: bool = Field(default=True, description="Whether advice is actionable")
    ai_emotional_support: bool = Field(default=True, description="Whether emotional support provided")
    
    # User feedback
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="User rating")
    user_feedback: Optional[str] = Field(None, description="User comments")
    user_emotion: Optional[str] = Field(None, description="User emotion")
    
    # Enhanced user feedback
    user_satisfaction: Optional[str] = Field(None, description="User satisfaction level")
    user_action_taken: Optional[str] = Field(None, description="Action user took after reading")
    user_accuracy_perception: Optional[str] = Field(None, description="User's perception of accuracy")
    user_usefulness_score: Optional[int] = Field(None, ge=1, le=5, description="Usefulness score")
    user_clarity_score: Optional[int] = Field(None, ge=1, le=5, description="Clarity score")
    
    # Technical details
    ai_model_used: str = Field(..., description="AI model used")
    tokens_used: int = Field(default=0, description="Tokens consumed")
    processing_time: float = Field(default=0.0, description="Processing time in seconds")
    reading_duration: float = Field(default=0.0, description="User reading time")
    
    # Enhanced behavioral data
    user_interaction_pattern: Dict[str, Any] = Field(default_factory=dict, description="User interaction details")
    cards_explored: bool = Field(default=False, description="Whether user explored card details")
    shared_reading: bool = Field(default=False, description="Whether reading was shared")
    saved_reading: bool = Field(default=False, description="Whether reading was saved")
    revisited_reading: bool = Field(default=False, description="Whether user revisited reading")
    
    # Metadata
    tags: List[str] = Field(default=[], description="Reading tags")
    is_public: bool = Field(default=False, description="Public sharing")
    share_url: Optional[str] = Field(None, description="Public share URL")

class ReadingCreate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    question: str = Field(..., min_length=1, max_length=2000, description="User's question")
    reading_type: str = Field(..., description="Type of reading")
    reading_spread: str = Field(..., description="Spread used")
    cards_drawn: List[CardDrawn] = Field(..., min_items=1, max_items=78, description="Cards drawn in reading")
    ai_response: str = Field(..., min_length=1, max_length=10000, description="Full AI interpretation")
    ai_model_used: str = Field(..., min_length=1, max_length=100, description="AI model used")
    tokens_used: int = Field(default=0, ge=0, le=100000, description="Tokens consumed")
    processing_time: float = Field(default=0.0, ge=0.0, le=3600.0, description="Processing time in seconds")
    tags: List[str] = Field(default=[], max_items=20, description="Reading tags")
    
    @validator('reading_type')
    def validate_reading_type(cls, v):
        valid_types = ['love', 'career', 'health', 'spiritual', 'general', 'relationship', 'money', 'travel']
        if v.lower() not in valid_types:
            raise ValueError(f'Reading type must be one of: {", ".join(valid_types)}')
        return v.lower()
    
    @validator('reading_spread')
    def validate_reading_spread(cls, v):
        valid_spreads = ['single_card', 'three_card', 'celtic_cross', 'horseshoe', 'tree_of_life', 'custom']
        if v.lower() not in valid_spreads:
            raise ValueError(f'Reading spread must be one of: {", ".join(valid_spreads)}')
        return v.lower()
    
    @validator('question')
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    @validator('ai_response')
    def validate_ai_response(cls, v):
        if not v or not v.strip():
            raise ValueError('AI response cannot be empty')
        return v.strip()
    
    @validator('cards_drawn')
    def validate_cards_drawn(cls, v):
        if not v:
            raise ValueError('At least one card must be drawn')
        return v

class ReadingUpdate(BaseModel):
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="User rating (1-5)")
    user_feedback: Optional[str] = Field(None, max_length=1000, description="User feedback")
    user_emotion: Optional[str] = Field(None, max_length=100, description="User emotion")
    ai_summary: Optional[str] = Field(None, max_length=2000, description="AI summary")
    ai_advice: Optional[str] = Field(None, max_length=2000, description="AI advice")
    is_public: Optional[bool] = Field(None, description="Public sharing status")
    share_url: Optional[str] = Field(None, max_length=500, description="Share URL")
    
    @validator('user_rating')
    def validate_user_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('User rating must be between 1 and 5')
        return v
    
    @validator('user_feedback')
    def validate_user_feedback(cls, v):
        if v is not None and not v.strip():
            return None
        return v
    
    @validator('ai_summary')
    def validate_ai_summary(cls, v):
        if v is not None and not v.strip():
            return None
        return v
    
    @validator('ai_advice')
    def validate_ai_advice(cls, v):
        if v is not None and not v.strip():
            return None
        return v

# ============================================================================
# AI TRAINING DATA MODELS
# ============================================================================

class AITrainingData(BaseDocument):
    reading_id: str = Field(..., description="Reference to reading")
    user_id: Optional[str] = Field(None, description="User reference")
    session_id: str = Field(..., description="Session identifier")
    
    # Enhanced training data
    question: str = Field(..., description="Original question")
    question_category: str = Field(..., description="Question category")
    question_complexity: str = Field(..., description="Question complexity")
    question_emotion: Optional[str] = Field(None, description="Emotion detected in question")
    question_context: Optional[str] = Field(None, description="Additional context")
    question_urgency: str = Field(..., description="Question urgency level")
    
    # Enhanced context data
    user_context: Dict[str, Any] = Field(..., description="Complete user context")
    cultural_context: Dict[str, Any] = Field(..., description="Cultural and belief context")
    cards_context: str = Field(..., description="Formatted card information")
    cards_combination: List[str] = Field(..., description="Card names drawn")
    spread_type: str = Field(..., description="Spread type used")
    spread_positions: List[str] = Field(..., description="Spread position meanings")
    
    # Enhanced AI response data
    ai_response: str = Field(..., description="Original AI response")
    ai_response_sections: Dict[str, str] = Field(..., description="Structured response sections")
    ai_response_length: int = Field(..., description="Response character count")
    ai_response_tone: str = Field(..., description="Response tone")
    ai_response_complexity: str = Field(..., description="Response complexity")
    ai_actionable_advice: bool = Field(..., description="Whether advice is actionable")
    ai_emotional_support: bool = Field(..., description="Whether emotional support provided")
    
    # Enhanced user feedback
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = None
    user_satisfaction: Optional[str] = None
    user_action_taken: Optional[str] = None
    user_accuracy_perception: Optional[str] = Field(None, description="User's accuracy perception")
    user_usefulness_score: Optional[int] = Field(None, ge=1, le=5)
    user_clarity_score: Optional[int] = Field(None, ge=1, le=5)
    
    # Behavioral data
    user_engagement: Dict[str, Any] = Field(..., description="User engagement metrics")
    reading_duration: float = Field(..., description="Time spent on reading")
    interaction_pattern: Dict[str, Any] = Field(..., description="User interaction details")
    
    # Training metadata
    training_status: str = Field(default="pending", description="Training status")
    model_version: str = Field(..., description="Model version")
    training_priority: int = Field(default=5, ge=1, le=10, description="Training priority")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Quality score")
    
    # Quality control
    minimum_rating_threshold: int = Field(default=3, description="Minimum rating for training")
    minimum_engagement_threshold: float = Field(default=60.0, description="Minimum engagement time")
    verified_user: bool = Field(default=False, description="Whether user is verified")
    return_visitor: bool = Field(default=False, description="Whether user is return visitor")
    
    # Timestamps
    processed_at: Optional[datetime] = None
    trained_at: Optional[datetime] = None

class AITrainingDataCreate(BaseModel):
    reading_id: str
    user_id: Optional[str] = None
    session_id: str
    question: str
    question_category: str
    question_complexity: str
    question_emotion: Optional[str] = None
    question_context: Optional[str] = None
    question_urgency: str = "medium"
    user_context: Dict[str, Any]
    cultural_context: Dict[str, Any]
    cards_context: str
    cards_combination: List[str]
    spread_type: str
    spread_positions: List[str]
    ai_response: str
    ai_response_sections: Dict[str, str]
    ai_response_length: int
    ai_response_tone: str
    ai_response_complexity: str
    ai_actionable_advice: bool
    ai_emotional_support: bool
    model_version: str
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    user_satisfaction: Optional[str] = None
    user_action_taken: Optional[str] = None
    user_accuracy_perception: Optional[str] = None
    user_usefulness_score: Optional[int] = None
    user_clarity_score: Optional[int] = None
    user_engagement: Dict[str, Any]
    reading_duration: float
    interaction_pattern: Dict[str, Any]

# ============================================================================
# TRAINING DATA ENHANCEMENT MODELS
# ============================================================================

class QuestionAnalysis(BaseModel):
    """Enhanced question analysis for training data"""
    original_question: str = Field(..., description="Original user question")
    question_category: str = Field(..., description="Question category")
    question_complexity: str = Field(..., description="Question complexity")
    question_emotion: Optional[str] = Field(None, description="Detected emotion")
    question_context: Optional[str] = Field(None, description="Additional context")
    question_urgency: str = Field(default="medium", description="Urgency level")
    question_keywords: List[str] = Field(default=[], description="Extracted keywords")
    question_sentiment: Optional[str] = Field(None, description="Sentiment analysis")

class UserContext(BaseModel):
    """Complete user context for training"""
    user_id: Optional[str] = Field(None, description="User identifier")
    experience_level: str = Field(..., description="Tarot experience level")
    belief_system: str = Field(..., description="Belief system")
    cultural_background: str = Field(..., description="Cultural background")
    reading_frequency: str = Field(..., description="Reading frequency")
    preferred_style: str = Field(..., description="Preferred reading style")
    language_preference: str = Field(..., description="Language preference")
    device_info: Dict[str, Any] = Field(..., description="Device information")
    session_data: Dict[str, Any] = Field(..., description="Session information")

class CulturalContext(BaseModel):
    """Cultural and belief context"""
    user_culture: str = Field(..., description="User's culture")
    belief_system: str = Field(..., description="Belief system")
    tarot_tradition: str = Field(..., description="Tarot tradition")
    language_preference: str = Field(..., description="Language preference")
    cultural_sensitivity: str = Field(..., description="Cultural sensitivity level")
    spiritual_background: Optional[str] = Field(None, description="Spiritual background")

class AIResponseAnalysis(BaseModel):
    """Detailed AI response analysis"""
    full_response: str = Field(..., description="Complete AI response")
    response_sections: Dict[str, str] = Field(..., description="Structured sections")
    response_tone: str = Field(..., description="Response tone")
    response_complexity: str = Field(..., description="Complexity level")
    actionable_advice: bool = Field(..., description="Has actionable advice")
    emotional_support: bool = Field(..., description="Provides emotional support")
    response_length: int = Field(..., description="Character count")
    response_quality_metrics: Dict[str, Any] = Field(..., description="Quality metrics")

class UserFeedbackAnalysis(BaseModel):
    """Enhanced user feedback analysis"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="User rating")
    feedback_text: Optional[str] = Field(None, description="Feedback text")
    satisfaction_level: Optional[str] = Field(None, description="Satisfaction level")
    action_taken: Optional[str] = Field(None, description="Action taken")
    emotional_response: Optional[str] = Field(None, description="Emotional response")
    accuracy_perception: Optional[str] = Field(None, description="Accuracy perception")
    usefulness_score: Optional[int] = Field(None, ge=1, le=5, description="Usefulness score")
    clarity_score: Optional[int] = Field(None, ge=1, le=5, description="Clarity score")
    engagement_metrics: Dict[str, Any] = Field(..., description="Engagement metrics")

class BehavioralData(BaseModel):
    """User behavioral data for training"""
    reading_duration: float = Field(..., description="Time spent on reading")
    interaction_pattern: Dict[str, Any] = Field(..., description="Interaction details")
    cards_explored: bool = Field(..., description="Explored card details")
    shared_reading: bool = Field(..., description="Shared reading")
    saved_reading: bool = Field(..., description="Saved reading")
    revisited_reading: bool = Field(..., description="Revisited reading")
    session_metrics: Dict[str, Any] = Field(..., description="Session metrics")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="Engagement score")

class TrainingQualityMetrics(BaseModel):
    """Quality metrics for training data"""
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    training_priority: int = Field(..., ge=1, le=10, description="Training priority")
    minimum_rating_threshold: int = Field(default=3, description="Minimum rating")
    minimum_engagement_threshold: float = Field(default=60.0, description="Minimum engagement")
    verified_user: bool = Field(..., description="User verification status")
    return_visitor: bool = Field(..., description="Return visitor status")
    data_quality_indicators: Dict[str, Any] = Field(..., description="Quality indicators")

class ConversationTurn(BaseModel):
    """Single turn in a conversation"""
    turn_number: int = Field(..., ge=1, description="Turn number in conversation")
    user_input: str = Field(..., min_length=1, max_length=2000, description="User's input")
    ai_response: str = Field(..., min_length=1, max_length=5000, description="AI's response")
    user_followup: Optional[str] = Field(None, max_length=2000, description="User's follow-up")
    ai_clarification: Optional[str] = Field(None, max_length=5000, description="AI's clarification")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Turn timestamp")
    context_changes: Dict[str, Any] = Field(default_factory=dict, description="Context changes")
    
    @validator('user_input')
    def validate_user_input(cls, v):
        if not v or not v.strip():
            raise ValueError('User input cannot be empty')
        return v.strip()
    
    @validator('ai_response')
    def validate_ai_response(cls, v):
        if not v or not v.strip():
            raise ValueError('AI response cannot be empty')
        return v.strip()
    
    @validator('user_followup')
    def validate_user_followup(cls, v):
        if v is not None and not v.strip():
            return None
        return v
    
    @validator('ai_clarification')
    def validate_ai_clarification(cls, v):
        if v is not None and not v.strip():
            return None
        return v

class ConversationSession(BaseDocument):
    """Multi-turn conversation session"""
    session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User reference")
    reading_id: str = Field(..., min_length=1, max_length=100, description="Associated reading")
    
    # Conversation data
    conversation_turns: List[ConversationTurn] = Field(..., min_items=1, max_items=100, description="Conversation turns")
    conversation_flow: str = Field(..., description="Conversation flow type")
    user_engagement_level: str = Field(..., description="User engagement level")
    
    # Context tracking
    initial_context: Dict[str, Any] = Field(..., description="Initial context")
    context_evolution: List[Dict[str, Any]] = Field(..., description="Context evolution")
    
    # Quality metrics
    conversation_quality_score: float = Field(..., ge=0.0, le=1.0, description="Conversation quality")
    user_satisfaction: Optional[str] = Field(None, description="User satisfaction")
    conversation_outcome: Optional[str] = Field(None, description="Conversation outcome")
    
    # Metadata
    total_duration: float = Field(..., ge=0.0, description="Total conversation duration")
    turns_count: int = Field(..., ge=1, description="Number of turns")
    is_completed: bool = Field(default=False, description="Conversation completed")

class ConversationSessionCreate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User reference")
    reading_id: str = Field(..., min_length=1, max_length=100, description="Associated reading")
    conversation_turns: List[ConversationTurn] = Field(..., min_items=1, max_items=100, description="Conversation turns")
    conversation_flow: str = Field(..., description="Conversation flow type")
    user_engagement_level: str = Field(..., description="User engagement level")
    initial_context: Dict[str, Any] = Field(..., description="Initial context")
    context_evolution: List[Dict[str, Any]] = Field(..., description="Context evolution")
    conversation_quality_score: float = Field(..., ge=0.0, le=1.0, description="Conversation quality")
    user_satisfaction: Optional[str] = Field(None, description="User satisfaction")
    conversation_outcome: Optional[str] = Field(None, description="Conversation outcome")
    total_duration: float = Field(..., ge=0.0, description="Total conversation duration")
    turns_count: int = Field(..., ge=1, description="Number of turns")
    is_completed: bool = Field(default=False, description="Conversation completed")
    
    @validator('conversation_flow')
    def validate_conversation_flow(cls, v):
        valid_flows = ['question_answer', 'clarification', 'followup', 'multi_turn', 'guided']
        if v.lower() not in valid_flows:
            raise ValueError(f'Conversation flow must be one of: {", ".join(valid_flows)}')
        return v.lower()
    
    @validator('user_engagement_level')
    def validate_user_engagement_level(cls, v):
        valid_levels = ['low', 'medium', 'high', 'very_high']
        if v.lower() not in valid_levels:
            raise ValueError(f'User engagement level must be one of: {", ".join(valid_levels)}')
        return v.lower()
    
    @validator('user_satisfaction')
    def validate_user_satisfaction(cls, v):
        if v is not None:
            valid_satisfactions = ['very_satisfied', 'satisfied', 'neutral', 'dissatisfied', 'very_dissatisfied']
            if v.lower() not in valid_satisfactions:
                raise ValueError(f'User satisfaction must be one of: {", ".join(valid_satisfactions)}')
            return v.lower()
        return v
    
    @validator('conversation_outcome')
    def validate_conversation_outcome(cls, v):
        if v is not None:
            valid_outcomes = ['clarification_provided', 'question_answered', 'guidance_given', 'incomplete', 'abandoned']
            if v.lower() not in valid_outcomes:
                raise ValueError(f'Conversation outcome must be one of: {", ".join(valid_outcomes)}')
            return v.lower()
        return v
    
    @validator('turns_count')
    def validate_turns_count(cls, v):
        if v <= 0:
            raise ValueError('Turns count must be greater than 0')
        return v
    
    @validator('total_duration')
    def validate_total_duration(cls, v):
        if v < 0:
            raise ValueError('Total duration cannot be negative')
        return v

# ============================================================================
# SESSION MODELS
# ============================================================================

class DeviceInfo(BaseModel):
    user_agent: str = Field(..., min_length=1, max_length=500, description="Browser user agent")
    ip_address: str = Field(..., min_length=1, max_length=45, description="Anonymized IP address")
    country: Optional[str] = Field(None, max_length=3, description="Country")
    city: Optional[str] = Field(None, max_length=100, description="City")
    timezone: Optional[str] = Field(None, max_length=50, description="Timezone")
    language: Optional[str] = Field(None, max_length=10, description="Browser language")
    screen_resolution: Optional[str] = Field(None, max_length=20, description="Screen resolution")
    device_type: Optional[str] = Field(None, max_length=20, description="Device type")
    
    @validator('user_agent')
    def validate_user_agent(cls, v):
        if not v or not v.strip():
            raise ValueError('User agent cannot be empty')
        return v.strip()
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        if not v or not v.strip():
            raise ValueError('IP address cannot be empty')
        return v.strip()
    
    @validator('country')
    def validate_country(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('Country code must be 2 characters')
        return v
    
    @validator('device_type')
    def validate_device_type(cls, v):
        if v is not None:
            valid_types = ['desktop', 'mobile', 'tablet', 'unknown']
            if v.lower() not in valid_types:
                raise ValueError(f'Device type must be one of: {", ".join(valid_types)}')
            return v.lower()
        return v

class UserBehavior(BaseModel):
    reading_types_used: List[str] = Field(default=[], description="Reading types used")
    average_rating: float = Field(default=0.0, description="Average rating given")
    engagement_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Engagement score")
    return_visitor: bool = Field(default=False, description="Return visitor flag")

class Session(BaseDocument):
    session_id: str = Field(..., description="Unique session identifier")
    session_token: str = Field(..., description="Secure session token")
    
    # Session data
    readings_count: int = Field(default=0, description="Number of readings")
    total_duration: float = Field(default=0.0, description="Total duration in minutes")
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Device and behavior
    device_info: DeviceInfo = Field(..., description="Device information")
    behavior: UserBehavior = Field(default_factory=UserBehavior, description="User behavior")
    
    # Session status
    is_active: bool = Field(default=True, description="Active session")
    expires_at: datetime = Field(..., description="Session expiration")

class SessionCreate(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier")
    session_token: str = Field(..., min_length=1, max_length=200, description="Secure session token")
    device_info: DeviceInfo = Field(..., description="Device information")
    expires_at: datetime = Field(..., description="Session expiration")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Session ID cannot be empty')
        return v.strip()
    
    @validator('session_token')
    def validate_session_token(cls, v):
        if not v or not v.strip():
            raise ValueError('Session token cannot be empty')
        return v.strip()
    
    @validator('expires_at')
    def validate_expires_at(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError('Session expiration must be in the future')
        return v

class SessionUpdate(BaseModel):
    readings_count: Optional[int] = Field(None, ge=0, description="Number of readings")
    total_duration: Optional[float] = Field(None, ge=0.0, description="Total duration in minutes")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    behavior: Optional[UserBehavior] = Field(None, description="User behavior")
    is_active: Optional[bool] = Field(None, description="Active status")
    
    @validator('readings_count')
    def validate_readings_count(cls, v):
        if v is not None and v < 0:
            raise ValueError('Readings count cannot be negative')
        return v
    
    @validator('total_duration')
    def validate_total_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError('Total duration cannot be negative')
        return v

# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class ReadingResponse(BaseModel):
    id: str
    question: str
    reading_type: str
    cards_drawn: List[CardDrawn]
    ai_response: str
    ai_summary: Optional[str]
    ai_advice: Optional[str]
    created_at: datetime
    tags: List[str]

    class Config:
        populate_by_name = True

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str]
    preferences: UserPreferences
    statistics: UserStatistics
    is_active: bool
    created_at: datetime

    class Config:
        populate_by_name = True

class TarotCardResponse(BaseModel):
    id: str
    name: str
    name_vi: str
    suit: str
    number: str
    arcana: str
    meaning_upright: str
    meaning_reversed: str
    keywords: List[str]
    image_url: str
    card_type: str
    fortune_telling: List[str]
    meanings_light: List[str]
    meanings_shadow: List[str]
    archetype: Optional[str]
    hebrew_alphabet: Optional[str]
    numerology: Optional[str]
    elemental: Optional[str]
    mythical_spiritual: Optional[str]
    questions_to_ask: List[str]
    affirmation: Optional[str]
    meaning_upright_vi: Optional[str]
    meaning_reversed_vi: Optional[str]
    keywords_vi: List[str]

    class Config:
        populate_by_name = True

# ============================================================================
# UTILITY MODELS
# ============================================================================

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order")

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool

    class Config:
        populate_by_name = True

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

    class Config:
        populate_by_name = True

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

# ============================================================================
# NOTIFICATION MODELS
# ============================================================================

class Notification(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), description="Notification ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: str = Field(..., description="Notification type")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    is_read: bool = Field(default=False, description="Read status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation time")
    read_at: Optional[datetime] = Field(None, description="Read time")

class NotificationCreate(BaseModel):
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: str = Field(..., description="Notification type")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")

class NotificationResponse(BaseModel):
    id: str = Field(..., description="Notification ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: str = Field(..., description="Notification type")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    is_read: bool = Field(..., description="Read status")
    created_at: datetime = Field(..., description="Creation time")
    read_at: Optional[datetime] = Field(None, description="Read time")

class PushSubscription(BaseModel):
    device_token: str = Field(..., description="Device token")
    platform: str = Field(..., description="Platform (ios, android, web)")
    subscribed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Subscription time")
    is_active: bool = Field(default=True, description="Active status")

class EmailTemplate(BaseModel):
    name: str = Field(..., description="Template name")
    subject: str = Field(..., description="Email subject")
    html_content: str = Field(..., description="HTML content")
    text_content: str = Field(..., description="Text content")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation time")

# ============================================================================
# FILE UPLOAD MODELS
# ============================================================================

class FileUpload(BaseModel):
    id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Generated filename")
    original_filename: Optional[str] = Field(None, description="Original filename")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="Content type")
    category: str = Field(..., description="File category")
    description: Optional[str] = Field(None, description="File description")
    user_id: Optional[str] = Field(None, description="User ID")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Upload time")
    file_type: str = Field(..., description="File type (image, document, etc.)")

class FileUploadResponse(BaseModel):
    id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Generated filename")
    original_filename: Optional[str] = Field(None, description="Original filename")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="Content type")
    category: str = Field(..., description="File category")
    description: Optional[str] = Field(None, description="File description")
    user_id: Optional[str] = Field(None, description="User ID")
    uploaded_at: datetime = Field(..., description="Upload time")
    file_type: str = Field(..., description="File type")
