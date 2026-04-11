from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Dict, Any

from app.core.config import settings
from app.core.database import get_database
from app.core.security import create_access_token
from app.database.models import GoogleAuthPayload, User, UserPreferences

router = APIRouter()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.postgres import get_pg_db
from app.database.pg_models import PGUser

router = APIRouter()

@router.post("/google", response_model=Dict[str, Any])
async def google_auth(
    payload: GoogleAuthPayload,
    session: AsyncSession = Depends(get_pg_db)
):
    """
    Authenticate a user using Google OAuth2 ID Token.
    Returns a JWT access token for our application.
    """
    if not settings.GOOGLE_CLIENT_ID:
        # Fallback for local testing if Client ID is not setup
        # NEVER DO THIS IN PRODUCTION
        if settings.ENVIRONMENT != "production" and payload.id_token == "test-bypass-token":
            user_info = {
                "email": "test@example.com",
                "name": "Test User",
                "picture": "https://example.com/avatar.png",
                "sub": "test-google-id-123"
            }
        else:
            raise HTTPException(
                status_code=501, 
                detail="Google Client ID is not configured on the server."
            )
    else:
        try:
            # Verify the token with Google
            user_info = id_token.verify_oauth2_token(
                payload.id_token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )

    email = user_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
        
    # Check if user exists in Postgres
    result = await session.execute(select(PGUser).where(PGUser.email == email))
    user_doc = result.scalar_one_or_none()
    
    if user_doc:
        # User exists, update auth info (in case avatar changed etc)
        user_doc.name = user_info.get("name", user_doc.name)
        user_doc.avatar_url = user_info.get("picture", user_doc.avatar_url)
        user_doc.auth_provider_id = user_info.get("sub")
        await session.commit()
    else:
        # New User in Postgres
        new_user = PGUser(
            email=email,
            name=user_info.get("name", email.split("@")[0]),
            avatar_url=user_info.get("picture"),
            auth_provider="google",
            auth_provider_id=user_info.get("sub")
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    
    # Create our own JWT access token
    # We use email as the subject for simplicity
    access_token = create_access_token(subject=email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": email,
            "name": user_info.get("name")
        }
    }
