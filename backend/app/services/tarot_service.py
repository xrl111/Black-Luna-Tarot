#  Tarot System - Tarot Service Layer
"""
Business logic for tarot cards operations
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
import random
import structlog

from app.database.models import (
    TarotCard, TarotCardResponse, PaginationParams, PaginatedResponse
)
from app.core.exceptions import NotFoundException, DatabaseException

logger = structlog.get_logger()

class TarotCardService:
    """
    Service layer for tarot cards operations
    """
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def get_cards_paginated(
        self,
        pagination: PaginationParams,
        suit: Optional[str] = None,
        card_type: Optional[str] = None,
        element: Optional[str] = None,
        search: Optional[str] = None
    ) -> PaginatedResponse:
        """
        Get paginated tarot cards with filtering
        """
        try:
            # Build filter query
            filter_query = {}
            
            if suit:
                # Handle both suit filtering and major arcana
                if suit == "major":
                    filter_query["arcana"] = "Major Arcana"
                else:
                    filter_query["suit"] = {"$regex": f"^{suit}$", "$options": "i"}
            if card_type:
                # Map card_type to arcana field
                if card_type == "major":
                    filter_query["arcana"] = "Major Arcana"
                elif card_type == "minor":
                    filter_query["arcana"] = "Minor Arcana"
            if element:
                # Use elemental field for filtering
                filter_query["elemental"] = {"$regex": f"^{element}", "$options": "i"}
            if search:
                filter_query["$text"] = {"$search": search}
            
            # Get total count
            total = await self.collection.count_documents(filter_query)
            
            # Calculate pagination
            skip = (pagination.page - 1) * pagination.limit
            pages = (total + pagination.limit - 1) // pagination.limit
            
            # Get documents
            cursor = self.collection.find(filter_query)
            cursor = cursor.sort(pagination.sort_by, 1 if pagination.sort_order == "asc" else -1)
            cursor = cursor.skip(skip).limit(pagination.limit)
            
            documents = await cursor.to_list(length=pagination.limit)
            
            # Convert to response models
            items = []
            for doc in documents:
                # Map _id to id for response model
                doc_copy = doc.copy()
                if "_id" in doc_copy:
                    doc_copy["id"] = str(doc_copy["_id"])
                items.append(TarotCardResponse(**doc_copy))
            
            return PaginatedResponse(
                items=items,
                total=total,
                page=pagination.page,
                limit=pagination.limit,
                pages=pages,
                has_next=pagination.page < pages,
                has_prev=pagination.page > 1
            )
            
        except Exception as e:
            logger.error("Failed to get paginated cards", error=str(e))
            raise DatabaseException("Failed to retrieve tarot cards")
    
    async def get_card_by_id(self, card_id: str) -> Optional[TarotCardResponse]:
        """
        Get a specific tarot card by ID
        """
        try:
            if not card_id or not card_id.strip():
                return None
            
            # Check if it's a valid ObjectId format
            if not ObjectId.is_valid(card_id):
                logger.warning("Invalid ObjectId format", card_id=card_id)
                return None
            
            document = await self.collection.find_one({"_id": ObjectId(card_id)})
            
            if not document:
                return None
            
            # Map _id to id for response model
            document_copy = document.copy()
            if "_id" in document_copy:
                document_copy["id"] = str(document_copy["_id"])
            
            return TarotCardResponse(**document_copy)
            
        except Exception as e:
            logger.error("Failed to get card by ID", card_id=card_id, error=str(e))
            return None

    async def get_card_by_name(self, name: str) -> Optional[TarotCardResponse]:
        """
        Get a specific tarot card by name
        """
        try:
            if not name or not name.strip():
                return None
            
            document = await self.collection.find_one({"name": name.strip()})
            
            if not document:
                return None
            
            # Map _id to id for response model
            document_copy = document.copy()
            if "_id" in document_copy:
                document_copy["id"] = str(document_copy["_id"])
            
            return TarotCardResponse(**document_copy)
            
        except Exception as e:
            logger.error("Failed to get card by name", name=name, error=str(e))
            return None
    
    async def get_cards_by_suit(self, suit: str) -> List[TarotCardResponse]:
        """
        Get all cards from a specific suit
        """
        try:
            if not suit or not suit.strip():
                return []
            
            cursor = self.collection.find({"suit": suit.lower()}).sort("number", 1)
            documents = await cursor.to_list(length=None)
            
            items = []
            for doc in documents:
                # Map _id to id for response model
                doc_copy = doc.copy()
                if "_id" in doc_copy:
                    doc_copy["id"] = str(doc_copy["_id"])
                items.append(TarotCardResponse(**doc_copy))
            return items
            
        except Exception as e:
            logger.error("Failed to get cards by suit", suit=suit, error=str(e))
            return []  # Return empty list instead of raising exception
    
    async def get_random_cards(
        self, 
        count: int, 
        suit: Optional[str] = None
    ) -> List[TarotCardResponse]:
        """
        Get random tarot cards
        """
        try:
            # Build filter query
            filter_query = {}
            if suit and suit.strip():
                filter_query["suit"] = suit.lower()
            
            # Get all matching cards
            cursor = self.collection.find(filter_query)
            all_cards = await cursor.to_list(length=None)
            
            if not all_cards:
                return []
            
            # Select random cards
            selected_cards = random.sample(all_cards, min(count, len(all_cards)))
            
            items = []
            for card in selected_cards:
                # Map _id to id for response model
                card_copy = card.copy()
                if "_id" in card_copy:
                    card_copy["id"] = str(card_copy["_id"])
                items.append(TarotCardResponse(**card_copy))
            return items
            
        except Exception as e:
            logger.error("Failed to get random cards", error=str(e))
            return []  # Return empty list instead of raising exception
    
    async def search_cards(self, query: str) -> List[TarotCardResponse]:
        """
        Search cards by name, keywords, or description
        """
        try:
            if not query or query.strip() == "":
                return []
            
            # Create text search query if text index exists, otherwise use regex
            try:
                # Try text search first
                search_query = {"$text": {"$search": query}}
                cursor = self.collection.find(search_query).sort("name", 1)
                documents = await cursor.to_list(length=None)
                
                if documents:
                    return [TarotCardResponse(**doc) for doc in documents]
            except Exception:
                # Fallback to regex search if text index doesn't exist
                search_query = {
                    "$or": [
                        {"name": {"$regex": query, "$options": "i"}},
                        {"name_vi": {"$regex": query, "$options": "i"}},
                        {"keywords": {"$regex": query, "$options": "i"}},
                        {"description": {"$regex": query, "$options": "i"}}
                    ]
                }
                cursor = self.collection.find(search_query).sort("name", 1)
                documents = await cursor.to_list(length=None)
            
            return [TarotCardResponse(**doc) for doc in documents]
            
        except Exception as e:
            logger.error("Failed to search cards", query=query, error=str(e))
            return []  # Return empty list instead of raising exception
    
    async def get_cards_stats(self) -> Dict[str, Any]:
        """
        Get statistics about tarot cards
        """
        try:
            # Total cards
            total_cards = await self.collection.count_documents({})
            
            # Cards by suit
            pipeline = [
                {"$group": {"_id": "$suit", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            suit_stats = await self.collection.aggregate(pipeline).to_list(None)
            
            # Cards by type
            pipeline = [
                {"$group": {"_id": "$card_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            type_stats = await self.collection.aggregate(pipeline).to_list(None)
            
            # Cards by element
            pipeline = [
                {"$match": {"element": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$element", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            element_stats = await self.collection.aggregate(pipeline).to_list(None)
            
            return {
                "total_cards": total_cards,
                "by_suit": {stat["_id"]: stat["count"] for stat in suit_stats},
                "by_type": {stat["_id"]: stat["count"] for stat in type_stats},
                "by_element": {stat["_id"]: stat["count"] for stat in element_stats}
            }
            
        except Exception as e:
            logger.error("Failed to get cards statistics", error=str(e))
            return {
                "total_cards": 0,
                "by_suit": {},
                "by_type": {},
                "by_element": {}
            }  # Return empty stats instead of raising exception
    
    async def create_card(self, card_data: dict) -> TarotCardResponse:
        """
        Create a new tarot card
        """
        try:
            result = await self.collection.insert_one(card_data)
            
            # Get the created card
            created_card = await self.collection.find_one({"_id": result.inserted_id})
            
            return TarotCardResponse(**created_card)
            
        except Exception as e:
            logger.error("Failed to create card", error=str(e))
            raise DatabaseException("Failed to create tarot card")
    
    async def update_card(self, card_id: str, update_data: dict) -> TarotCardResponse:
        """
        Update a tarot card
        """
        try:
            if not ObjectId.is_valid(card_id):
                raise NotFoundException("Invalid card ID")
            
            result = await self.collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise NotFoundException("Tarot card not found")
            
            # Get the updated card
            updated_card = await self.collection.find_one({"_id": ObjectId(card_id)})
            
            return TarotCardResponse(**updated_card)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to update card", card_id=card_id, error=str(e))
            raise DatabaseException("Failed to update tarot card")
    
    async def delete_card(self, card_id: str) -> bool:
        """
        Delete a tarot card
        """
        try:
            if not ObjectId.is_valid(card_id):
                raise NotFoundException("Invalid card ID")
            
            result = await self.collection.delete_one({"_id": ObjectId(card_id)})
            
            if result.deleted_count == 0:
                raise NotFoundException("Tarot card not found")
            
            return True
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to delete card", card_id=card_id, error=str(e))
            raise DatabaseException("Failed to delete tarot card")
