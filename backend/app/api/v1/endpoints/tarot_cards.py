# 🎯 Tarot System - Tarot Cards API Endpoints
"""
API endpoints for tarot cards management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
import os
from pathlib import Path as PathLib

from app.core.database import get_tarot_cards_collection, get_users_collection
from app.database.models import TarotCard, TarotCardResponse, PaginationParams, PaginatedResponse
from app.services.tarot_service import TarotCardService
from app.core.exceptions import NotFoundException

logger = structlog.get_logger()
router = APIRouter()

# ============================================================================
# TAROT CARD CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=TarotCardResponse, status_code=201)
async def create_tarot_card(
    card_data: TarotCard,
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Create a new tarot card
    
    Creates a new tarot card with all the provided data.
    The image should be uploaded separately using the upload endpoint.
    
    **Request Body:**
    - All tarot card fields as defined in TarotCard model
    
    **Response:**
    - Created tarot card with ID
    
    **Error Responses:**
    - 400: Invalid data
    - 409: Card already exists
    """
    try:
        service = TarotCardService(collection)
        
        # Check if card with same name already exists
        existing_card = await service.get_card_by_name(card_data.name)
        if existing_card:
            raise HTTPException(status_code=409, detail="Card with this name already exists")
        
        # Create the card
        created_card = await service.create_card(card_data)
        
        logger.info("Created new tarot card", 
                   card_id=str(created_card.id),
                   name=created_card.name)
        
        return created_card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create tarot card", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create tarot card")

@router.post("/with-image", response_model=TarotCardResponse, status_code=201)
async def create_tarot_card_with_image(
    card_data: TarotCard = Form(...),
    image: UploadFile = File(...),
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    """
    Create a new tarot card with image upload
    
    Creates a new tarot card and uploads its image in one operation.
    
    **Request:**
    - `card_data`: Tarot card data (JSON string)
    - `image`: Image file (multipart/form-data)
    
    **Response:**
    - Created tarot card with image URL
    
    **Error Responses:**
    - 400: Invalid data or image
    - 409: Card already exists
    """
    try:
        # Validate image file
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        if image.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image size must be less than 10MB")
        
        service = TarotCardService(collection)
        
        # Check if card with same name already exists
        existing_card = await service.get_card_by_name(card_data.name)
        if existing_card:
            raise HTTPException(status_code=409, detail="Card with this name already exists")
        
        # Upload image first
        from app.services.upload_service import UploadService
        upload_service = UploadService(users_collection)
        
        # Generate filename based on card name
        file_extension = PathLib(image.filename).suffix if image.filename else ".jpg"
        safe_filename = f"{card_data.name.lower().replace(' ', '_')}{file_extension}"
        
        # Upload image to tarot-cards directory
        upload_result = await upload_service.upload_tarot_card_image(
            image, card_data.name, card_data.name_vi
        )
        
        # Update card data with image URL
        card_data.image_url = upload_result.file_path
        
        # Create the card
        created_card = await service.create_card(card_data)
        
        logger.info("Created new tarot card with image", 
                   card_id=str(created_card.id),
                   name=created_card.name,
                   image_url=upload_result.file_path)
        
        return created_card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create tarot card with image", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create tarot card with image")

@router.put("/{card_id}", response_model=TarotCardResponse)
async def update_tarot_card(
    card_id: str,
    card_data: TarotCard,
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Update an existing tarot card
    
    Updates an existing tarot card with new data.
    
    **Parameters:**
    - `card_id`: The ID of the tarot card to update
    
    **Request Body:**
    - Updated tarot card data
    
    **Response:**
    - Updated tarot card
    
    **Error Responses:**
    - 404: Card not found
    - 400: Invalid data
    """
    try:
        service = TarotCardService(collection)
        
        # Check if card exists
        existing_card = await service.get_card_by_id(card_id)
        if not existing_card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Update the card
        updated_card = await service.update_card(card_id, card_data)
        
        logger.info("Updated tarot card", 
                   card_id=card_id,
                   name=updated_card.name)
        
        return updated_card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update tarot card", card_id=card_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update tarot card")

@router.delete("/{card_id}")
async def delete_tarot_card(
    card_id: str,
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Delete a tarot card
    
    Deletes a tarot card and optionally its associated image.
    
    **Parameters:**
    - `card_id`: The ID of the tarot card to delete
    
    **Response:**
    - Success message
    
    **Error Responses:**
    - 404: Card not found
    """
    try:
        service = TarotCardService(collection)
        
        # Check if card exists
        existing_card = await service.get_card_by_id(card_id)
        if not existing_card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Delete the card
        await service.delete_card(card_id)
        
        logger.info("Deleted tarot card", 
                   card_id=card_id,
                   name=existing_card.name)
        
        return {"message": "Tarot card deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete tarot card", card_id=card_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete tarot card")

# ============================================================================
# TAROT CARD IMAGE ENDPOINTS
# ============================================================================

@router.get("/image/{card_id}")
async def get_tarot_card_image(
    card_id: str,
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Get tarot card image by card ID
    
    Returns the image file for a specific tarot card.
    The image is served from the uploads/tarot-cards directory.
    
    **Parameters:**
    - `card_id`: The ID of the tarot card
    
    **Response:**
    - Image file (JPEG/PNG)
    
    **Error Responses:**
    - 404: Card not found
    - 404: Image file not found
    """
    try:
        # Get card information to find the image filename
        service = TarotCardService(collection)
        card = await service.get_card_by_id(card_id)
        
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Get image filename from card data
        image_url = card.image_url
        if not image_url:
            raise HTTPException(status_code=404, detail="Card image not available")
        
        # Extract filename from image_url (e.g., "/uploads/tarot-cards/p07.jpg" -> "p07.jpg")
        image_filename = image_url.split("/")[-1] if "/" in image_url else image_url
        
        # Construct path to image file in uploads/tarot-cards directory
        uploads_path = PathLib(__file__).parent.parent.parent.parent.parent / "uploads" / "tarot-cards"
        image_path = uploads_path / image_filename
        
        # Check if image file exists
        if not image_path.exists():
            logger.warning("Image file not found", 
                          card_id=card_id, 
                          image_filename=image_filename,
                          image_path=str(image_path))
            raise HTTPException(status_code=404, detail="Image file not found")
        
        # Determine content type based on file extension
        content_type = "image/jpeg"  # Default
        if image_path.suffix.lower() in [".png", ".gif", ".webp"]:
            content_type = f"image/{image_path.suffix.lower()[1:]}"
        
        logger.info("Serving tarot card image", 
                   card_id=card_id, 
                   image_filename=image_filename)
        
        return FileResponse(
            path=str(image_path),
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to serve tarot card image", 
                    card_id=card_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to serve card image")

@router.get("/image/filename/{image_filename}")
async def get_tarot_card_image_by_filename(
    image_filename: str
):
    """
    Get tarot card image by filename
    
    Returns the image file directly by filename.
    This is useful for cases where you know the exact filename.
    
    **Parameters:**
    - `image_filename`: The filename of the image (e.g., "m00.jpg", "c01.jpg")
    
    **Response:**
    - Image file (JPEG/PNG)
    
    **Error Responses:**
    - 404: Image file not found
    """
    try:
        # Construct path to image file in uploads/tarot-cards directory
        uploads_path = PathLib(__file__).parent.parent.parent.parent.parent / "uploads" / "tarot-cards"
        image_path = uploads_path / image_filename
        
        # Check if image file exists
        if not image_path.exists():
            logger.warning("Image file not found by filename", 
                          image_filename=image_filename,
                          image_path=str(image_path))
            raise HTTPException(status_code=404, detail="Image file not found")
        
        # Determine content type based on file extension
        content_type = "image/jpeg"  # Default
        if image_path.suffix.lower() in [".png", ".gif", ".webp"]:
            content_type = f"image/{image_path.suffix.lower()[1:]}"
        
        logger.info("Serving tarot card image by filename", 
                   image_filename=image_filename)
        
        return FileResponse(
            path=str(image_path),
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to serve tarot card image by filename", 
                    image_filename=image_filename, 
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to serve card image")

@router.get("/images/list")
async def list_available_images():
    """
    List all available tarot card images
    
    Returns a list of all available image files in the uploads/tarot-cards directory.
    This is useful for frontend to know what images are available.
    
    **Response:**
    - List of image filenames
    """
    try:
        # Construct path to uploads/tarot-cards directory
        uploads_path = PathLib(__file__).parent.parent.parent.parent.parent / "uploads" / "tarot-cards"
        
        # Get all image files
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(uploads_path.glob(f"*{ext}"))
            image_files.extend(uploads_path.glob(f"*{ext.upper()}"))
        
        # Convert to filenames and sort
        filenames = [f.name for f in image_files]
        filenames.sort()
        
        logger.info("Listed available tarot card images", 
                   count=len(filenames))
        
        return {
            "total_images": len(filenames),
            "images": filenames
        }
        
    except Exception as e:
        logger.error("Failed to list available images", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list available images")

# ============================================================================
# TAROT CARD DATA ENDPOINTS
# ============================================================================

@router.get("/", response_model=PaginatedResponse)
async def get_tarot_cards(
    pagination: PaginationParams = Depends(),
    suit: Optional[str] = Query(None, description="Filter by suit"),
    card_type: Optional[str] = Query(None, description="Filter by card type (major/minor)"),
    element: Optional[str] = Query(None, description="Filter by element"),
    search: Optional[str] = Query(None, description="Search in name and keywords"),
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Get paginated list of tarot cards with optional filtering
    """
    try:
        # Validate suit parameter
        if suit:
            valid_suits = ["wands", "cups", "swords", "pentacles", "major"]
            if suit.lower() not in valid_suits:
                raise HTTPException(status_code=400, detail=f"Invalid suit. Must be one of: {', '.join(valid_suits)}")
        
        # Validate card_type parameter
        if card_type:
            valid_types = ["major", "minor"]
            if card_type.lower() not in valid_types:
                raise HTTPException(status_code=400, detail=f"Invalid card_type. Must be one of: {', '.join(valid_types)}")
        
        # Validate element parameter
        if element:
            valid_elements = ["fire", "water", "air", "earth"]
            if element.lower() not in valid_elements:
                raise HTTPException(status_code=400, detail=f"Invalid element. Must be one of: {', '.join(valid_elements)}")
        
        service = TarotCardService(collection)
        result = await service.get_cards_paginated(
            pagination=pagination,
            suit=suit.lower() if suit else None,
            card_type=card_type.lower() if card_type else None,
            element=element.lower() if element else None,
            search=search
        )
        
        logger.info(
            "Retrieved tarot cards",
            total=result.total,
            page=pagination.page,
            limit=pagination.limit
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve tarot cards", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve tarot cards")

@router.get("/search/{query}", response_model=List[TarotCardResponse])
async def search_cards(
    query: str,
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Search tarot cards by name, keywords, or description
    """
    try:
        if not query or not query.strip():
            return []
        
        # Validate query length
        if len(query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters long")
            
        service = TarotCardService(collection)
        cards = await service.search_cards(query.strip())
        
        logger.info("Searched cards", query=query, count=len(cards))
        return cards
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to search cards", query=query, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to search cards")

@router.get("/search", response_model=List[TarotCardResponse])
async def search_cards_empty(
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Handle empty search query
    """
    return []

@router.get("/suit/{suit}", response_model=List[TarotCardResponse])
async def get_cards_by_suit(
    suit: str,
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Get tarot cards by suit
    """
    try:
        # Validate suit parameter
        valid_suits = ["wands", "cups", "swords", "pentacles", "major"]
        if suit.lower() not in valid_suits:
            raise HTTPException(status_code=400, detail=f"Invalid suit. Must be one of: {', '.join(valid_suits)}")
        
        service = TarotCardService(collection)
        cards = await service.get_cards_by_suit(suit.lower())
        
        logger.info("Retrieved cards by suit", suit=suit, count=len(cards))
        return cards
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get cards by suit", suit=suit, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get cards by suit")

@router.get("/random/{count}", response_model=List[TarotCardResponse])
async def get_random_cards(
    count: int = Path(..., ge=1, le=78, description="Number of random cards to get"),
    suit: Optional[str] = Query(None, description="Filter by suit"),
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Get random tarot cards
    """
    try:
        # Validate suit parameter if provided
        if suit:
            valid_suits = ["wands", "cups", "swords", "pentacles", "major"]
            if suit.lower() not in valid_suits:
                raise HTTPException(status_code=400, detail=f"Invalid suit. Must be one of: {', '.join(valid_suits)}")
        
        service = TarotCardService(collection)
        cards = await service.get_random_cards(count, suit.lower() if suit else None)
        
        logger.info("Retrieved random cards", count=count, suit=suit, actual_count=len(cards))
        return cards
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get random cards", count=count, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get random cards")

@router.get("/stats/overview")
async def get_cards_stats(
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Get tarot cards statistics overview
    """
    try:
        service = TarotCardService(collection)
        stats = await service.get_cards_stats()
        
        logger.info("Retrieved cards stats", stats=stats)
        return stats
        
    except Exception as e:
        logger.error("Failed to get cards stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get cards stats")

@router.get("/{card_id}", response_model=TarotCardResponse)
async def get_tarot_card(
    card_id: str,
    collection: AsyncIOMotorCollection = Depends(get_tarot_cards_collection)
):
    """
    Get a specific tarot card by ID
    """
    try:
        service = TarotCardService(collection)
        card = await service.get_card_by_id(card_id)
        
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        logger.info("Retrieved tarot card", card_id=card_id)
        return card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get tarot card", card_id=card_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get tarot card")
