# 🎯 Tarot System - Analytics Service
"""
Service layer for analytics and reporting
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()

class AnalyticsService:
    """
    Service for analytics and reporting
    """
    
    def __init__(self, readings_collection: AsyncIOMotorCollection, sessions_collection: AsyncIOMotorCollection):
        self.readings_collection = readings_collection
        self.sessions_collection = sessions_collection
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """
        Get system overview statistics
        """
        try:
            # Get basic counts
            total_readings = await self.readings_collection.count_documents({})
            total_sessions = await self.sessions_collection.count_documents({})
            active_sessions = await self.sessions_collection.count_documents({
                "is_active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            # Get recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_readings = await self.readings_collection.count_documents({
                "created_at": {"$gte": yesterday}
            })
            
            # Get average rating
            pipeline = [
                {"$match": {"user_rating": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": None, "avg_rating": {"$avg": "$user_rating"}}}
            ]
            
            rating_result = await self.readings_collection.aggregate(pipeline).to_list(1)
            avg_rating = rating_result[0]["avg_rating"] if rating_result else 0
            
            return {
                "total_readings": total_readings,
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "recent_readings_24h": recent_readings,
                "average_rating": round(avg_rating, 2),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get system overview", error=str(e))
            raise
    
    async def get_reading_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Get reading trends over time
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"},
                            "day": {"$dayOfMonth": "$created_at"}
                        },
                        "count": {"$sum": 1},
                        "avg_rating": {"$avg": "$user_rating"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await self.readings_collection.aggregate(pipeline).to_list(None)
            
            # Format results
            trends = []
            for result in results:
                date_info = result["_id"]
                date_str = f"{date_info['year']}-{date_info['month']:02d}-{date_info['day']:02d}"
                
                trends.append({
                    "date": date_str,
                    "readings_count": result["count"],
                    "average_rating": round(result.get("avg_rating", 0), 2)
                })
            
            return {
                "period_days": days,
                "trends": trends,
                "total_readings": sum(t["readings_count"] for t in trends)
            }
            
        except Exception as e:
            logger.error("Failed to get reading trends", error=str(e))
            raise
    
    async def get_popular_cards(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most frequently drawn cards
        """
        try:
            pipeline = [
                {"$unwind": "$cards_drawn"},
                {
                    "$group": {
                        "_id": "$cards_drawn.card_id",
                        "count": {"$sum": 1},
                        "avg_rating": {"$avg": "$user_rating"}
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            
            results = await self.readings_collection.aggregate(pipeline).to_list(None)
            
            # Note: In a real implementation, you'd join with tarot_cards collection
            # to get card names and details
            popular_cards = []
            for result in results:
                popular_cards.append({
                    "card_id": str(result["_id"]),
                    "drawn_count": result["count"],
                    "average_rating": round(result.get("avg_rating", 0), 2)
                })
            
            return popular_cards
            
        except Exception as e:
            logger.error("Failed to get popular cards", error=str(e))
            raise
    
    async def get_reading_types_stats(self) -> Dict[str, Any]:
        """
        Get statistics by reading type
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$reading_type",
                        "count": {"$sum": 1},
                        "avg_rating": {"$avg": "$user_rating"},
                        "avg_processing_time": {"$avg": "$processing_time"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            results = await self.readings_collection.aggregate(pipeline).to_list(None)
            
            stats = {}
            for result in results:
                reading_type = result["_id"]
                stats[reading_type] = {
                    "count": result["count"],
                    "average_rating": round(result.get("avg_rating", 0), 2),
                    "average_processing_time": round(result.get("avg_processing_time", 0), 2)
                }
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get reading types stats", error=str(e))
            raise
    
    async def get_user_engagement_metrics(self) -> Dict[str, Any]:
        """
        Get user engagement metrics
        """
        try:
            # Sessions with readings
            sessions_with_readings = await self.sessions_collection.count_documents({
                "readings_count": {"$gt": 0}
            })
            
            # Average readings per session
            pipeline = [
                {"$match": {"readings_count": {"$gt": 0}}},
                {"$group": {"_id": None, "avg_readings": {"$avg": "$readings_count"}}}
            ]
            
            avg_result = await self.sessions_collection.aggregate(pipeline).to_list(1)
            avg_readings_per_session = avg_result[0]["avg_readings"] if avg_result else 0
            
            # Return visitors (sessions with multiple readings)
            return_visitors = await self.sessions_collection.count_documents({
                "readings_count": {"$gt": 1}
            })
            
            return {
                "sessions_with_readings": sessions_with_readings,
                "average_readings_per_session": round(avg_readings_per_session, 2),
                "return_visitors": return_visitors,
                "engagement_rate": round((sessions_with_readings / max(1, await self.sessions_collection.count_documents({}))) * 100, 2)
            }
            
        except Exception as e:
            logger.error("Failed to get user engagement metrics", error=str(e))
            raise


