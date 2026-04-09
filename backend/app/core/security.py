from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.requests import Request
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.config import settings
from app.core.database import get_database
from app.database.models import User

# OAuth2 scheme for dependency injection
# We define tokenUrl as empty since we use Google OAuth primarily, but FastAPI needs it for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token for the user"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Payload format
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Generate token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_users_collection() -> AsyncIOMotorCollection:
    """Get the users collection"""
    db = get_database()
    return db["users"]

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    collection: AsyncIOMotorCollection = Depends(get_users_collection)
) -> User:
    """
    Dependency to get the current authenticated user.
    Throws 401 Unauthorized if token is missing or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    # Fetch user from database using the PyObjectId or string
    # We store the email or object id in sub. If it's email, we query by email. 
    # Let's assume sub is email for simplicity of Google Auth.
    from bson.errors import InvalidId
    from bson.objectid import ObjectId
    
    user_doc = None
    if "@" in user_id:
        user_doc = await collection.find_one({"email": user_id})
    else:
        try:
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
        except InvalidId:
            pass
            
    if user_doc is None:
        raise credentials_exception
        
    # Convert dict to Pydantic Model
    user = User(**user_doc)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    collection: AsyncIOMotorCollection = Depends(get_users_collection)
) -> Optional[User]:
    """
    Dependency to get the current authenticated user if exists.
    If no token is provided, returns None (Anonymous/Guest user).
    """
    if not token:
        return None
        
    try:
        return await get_current_user(token, collection)
    except HTTPException:
        # If token is invalid for some reason, we could either reject or treat as guest.
        # It's safer to treat as Guest if we just want optional auth.
        return None
