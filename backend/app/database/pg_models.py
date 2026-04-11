from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, func
from app.core.postgres import Base

class PGUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    # Auth
    auth_provider = Column(String(50), default='email')
    auth_provider_id = Column(String(255), nullable=True)

    # Preferences
    experience_level = Column(String(50), default='beginner')
    belief_system = Column(String(100), default='spiritual_but_practical')
    cultural_background = Column(String(100), default='vietnamese')
    reading_frequency = Column(String(50), default='occasional')
    preferred_style = Column(String(50), default='detailed')
    language_preference = Column(String(10), default='vi')
    tarot_tradition = Column(String(50), default='rider_waite')

    # Statistics
    total_readings = Column(Integer, default=0)
    average_rating = Column(Float, default=0.00)
    engagement_score = Column(Float, default=0.00)
    last_reading_date = Column(DateTime(timezone=True), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(20), default='user')

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    def to_pydantic_dict(self):
        """Map the flattened Postgres schema to the nested Pydantic User schema so the Frontend doesn't break"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "auth_provider": self.auth_provider,
            "auth_provider_id": self.auth_provider_id,
            "preferences": {
                "experience_level": self.experience_level,
                "belief_system": self.belief_system,
                "cultural_background": self.cultural_background,
                "reading_frequency": self.reading_frequency,
                "reading_style": self.preferred_style, # mapped from preferred_style
                "language": self.language_preference, # mapped from language_preference
                "theme": "auto", 
                "tarot_tradition": self.tarot_tradition
            },
            "statistics": {
                "total_readings": self.total_readings,
                "average_rating": self.average_rating,
                "engagement_score": self.engagement_score,
                "last_reading_date": self.last_reading_date
            },
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
