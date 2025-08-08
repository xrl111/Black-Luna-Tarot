# 🎯 Tarot System - Notification Service
"""
Service layer for notification management
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
from datetime import datetime
from bson import ObjectId

from app.database.models import Notification, NotificationCreate, NotificationResponse
from app.core.exceptions import NotFoundException, DatabaseException

logger = structlog.get_logger()

class NotificationService:
    def __init__(self, users_collection: AsyncIOMotorCollection):
        self.users_collection = users_collection
    
    async def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        """Create a new notification"""
        try:
            notification = Notification(
                user_id=notification_data.user_id,
                title=notification_data.title,
                message=notification_data.message,
                notification_type=notification_data.notification_type,
                data=notification_data.data,
                created_at=datetime.utcnow(),
                is_read=False
            )
            
            result = await self.users_collection.update_one(
                {"_id": ObjectId(notification_data.user_id)},
                {"$push": {"notifications": notification.dict()}}
            )
            
            if result.modified_count == 0:
                raise DatabaseException("Failed to create notification")
            
            logger.info("Created notification", 
                       user_id=notification_data.user_id,
                       notification_type=notification_data.notification_type)
            
            return NotificationResponse(**notification.dict())
            
        except Exception as e:
            logger.error("Failed to create notification", error=str(e))
            raise DatabaseException(f"Failed to create notification: {str(e)}")
    
    async def get_user_notifications(
        self, 
        user_id: str, 
        unread_only: bool = False, 
        limit: int = 50
    ) -> List[NotificationResponse]:
        """Get user notifications"""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise NotFoundException("User not found")
            
            notifications = user.get("notifications", [])
            
            if unread_only:
                notifications = [n for n in notifications if not n.get("is_read", False)]
            
            # Sort by created_at descending and limit
            notifications.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
            notifications = notifications[:limit]
            
            return [NotificationResponse(**notification) for notification in notifications]
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to get user notifications", error=str(e))
            raise DatabaseException(f"Failed to get user notifications: {str(e)}")
    
    async def mark_notification_read(self, notification_id: str) -> None:
        """Mark notification as read"""
        try:
            result = await self.users_collection.update_one(
                {"notifications._id": ObjectId(notification_id)},
                {"$set": {"notifications.$.is_read": True, "notifications.$.read_at": datetime.utcnow()}}
            )
            
            if result.modified_count == 0:
                raise NotFoundException("Notification not found")
            
            logger.info("Marked notification as read", notification_id=notification_id)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to mark notification as read", error=str(e))
            raise DatabaseException(f"Failed to mark notification as read: {str(e)}")
    
    async def mark_all_notifications_read(self, user_id: str) -> None:
        """Mark all user notifications as read"""
        try:
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "notifications.$[].is_read": True,
                        "notifications.$[].read_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                logger.warning("No notifications found to mark as read", user_id=user_id)
            
            logger.info("Marked all notifications as read", user_id=user_id)
            
        except Exception as e:
            logger.error("Failed to mark all notifications as read", error=str(e))
            raise DatabaseException(f"Failed to mark all notifications as read: {str(e)}")
    
    async def delete_notification(self, notification_id: str) -> None:
        """Delete a notification"""
        try:
            result = await self.users_collection.update_one(
                {"notifications._id": ObjectId(notification_id)},
                {"$pull": {"notifications": {"_id": ObjectId(notification_id)}}}
            )
            
            if result.modified_count == 0:
                raise NotFoundException("Notification not found")
            
            logger.info("Deleted notification", notification_id=notification_id)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to delete notification", error=str(e))
            raise DatabaseException(f"Failed to delete notification: {str(e)}")
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise NotFoundException("User not found")
            
            notifications = user.get("notifications", [])
            unread_count = sum(1 for n in notifications if not n.get("is_read", False))
            
            return unread_count
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to get unread count", error=str(e))
            raise DatabaseException(f"Failed to get unread count: {str(e)}")
    
    async def subscribe_push_notifications(
        self, 
        user_id: str, 
        device_token: str, 
        platform: str
    ) -> None:
        """Subscribe user to push notifications"""
        try:
            subscription = {
                "device_token": device_token,
                "platform": platform,
                "subscribed_at": datetime.utcnow(),
                "is_active": True
            }
            
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$addToSet": {"push_subscriptions": subscription}
                }
            )
            
            if result.modified_count == 0:
                logger.warning("User not found or subscription already exists", user_id=user_id)
            
            logger.info("Subscribed to push notifications", 
                       user_id=user_id, 
                       platform=platform)
            
        except Exception as e:
            logger.error("Failed to subscribe to push notifications", error=str(e))
            raise DatabaseException(f"Failed to subscribe to push notifications: {str(e)}")
    
    async def unsubscribe_push_notifications(self, user_id: str, device_token: str) -> None:
        """Unsubscribe user from push notifications"""
        try:
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$pull": {"push_subscriptions": {"device_token": device_token}}
                }
            )
            
            if result.modified_count == 0:
                logger.warning("No subscription found to remove", user_id=user_id)
            
            logger.info("Unsubscribed from push notifications", user_id=user_id)
            
        except Exception as e:
            logger.error("Failed to unsubscribe from push notifications", error=str(e))
            raise DatabaseException(f"Failed to unsubscribe from push notifications: {str(e)}")
    
    async def send_push_notification(
        self, 
        user_ids: List[str], 
        title: str, 
        body: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send push notification to multiple users"""
        try:
            # Get all users with push subscriptions
            users = await self.users_collection.find({
                "_id": {"$in": [ObjectId(uid) for uid in user_ids]},
                "push_subscriptions": {"$exists": True, "$ne": []}
            }).to_list(None)
            
            sent_count = 0
            failed_count = 0
            
            for user in users:
                subscriptions = user.get("push_subscriptions", [])
                for subscription in subscriptions:
                    if subscription.get("is_active", True):
                        try:
                            # Here you would integrate with actual push notification service
                            # (Firebase, Apple Push Notification Service, etc.)
                            logger.info("Sending push notification", 
                                       user_id=str(user["_id"]),
                                       device_token=subscription["device_token"])
                            sent_count += 1
                        except Exception as e:
                            logger.error("Failed to send push notification", 
                                        user_id=str(user["_id"]),
                                        error=str(e))
                            failed_count += 1
            
            return {
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_users": len(users)
            }
            
        except Exception as e:
            logger.error("Failed to send push notifications", error=str(e))
            raise DatabaseException(f"Failed to send push notifications: {str(e)}")
    
    async def send_email_notification(
        self, 
        user_ids: List[str], 
        subject: str, 
        template: str, 
        template_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send email notification to multiple users"""
        try:
            # Get all users
            users = await self.users_collection.find({
                "_id": {"$in": [ObjectId(uid) for uid in user_ids]}
            }).to_list(None)
            
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    # Here you would integrate with actual email service
                    # (SendGrid, AWS SES, etc.)
                    logger.info("Sending email notification", 
                               user_id=str(user["_id"]),
                               email=user.get("email"),
                               subject=subject)
                    sent_count += 1
                except Exception as e:
                    logger.error("Failed to send email notification", 
                                user_id=str(user["_id"]),
                                error=str(e))
                    failed_count += 1
            
            return {
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_users": len(users)
            }
            
        except Exception as e:
            logger.error("Failed to send email notifications", error=str(e))
            raise DatabaseException(f"Failed to send email notifications: {str(e)}")
    
    async def create_email_template(
        self, 
        template_name: str, 
        subject: str, 
        html_content: str, 
        text_content: str
    ) -> Dict[str, Any]:
        """Create email template"""
        try:
            template = {
                "name": template_name,
                "subject": subject,
                "html_content": html_content,
                "text_content": text_content,
                "created_at": datetime.utcnow()
            }
            
            # Store template in database or file system
            logger.info("Created email template", template_name=template_name)
            
            return template
            
        except Exception as e:
            logger.error("Failed to create email template", error=str(e))
            raise DatabaseException(f"Failed to create email template: {str(e)}")
    
    async def get_notification_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user notification settings"""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise NotFoundException("User not found")
            
            settings = user.get("notification_settings", {})
            return settings
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to get notification settings", error=str(e))
            raise DatabaseException(f"Failed to get notification settings: {str(e)}")
    
    async def update_notification_settings(self, user_id: str, settings: Dict[str, Any]) -> None:
        """Update user notification settings"""
        try:
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"notification_settings": settings}}
            )
            
            if result.modified_count == 0:
                raise NotFoundException("User not found")
            
            logger.info("Updated notification settings", user_id=user_id)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to update notification settings", error=str(e))
            raise DatabaseException(f"Failed to update notification settings: {str(e)}")
