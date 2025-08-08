# 🎯 Tarot System - Upload Service
"""
Service layer for file upload and management
"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
import structlog
import aiofiles
import os
from datetime import datetime
import uuid
from PIL import Image
import io
from fastapi import UploadFile

from app.database.models import FileUpload, FileUploadResponse
from app.core.exceptions import ValidationException, DatabaseException, NotFoundException
from app.core.config import settings

logger = structlog.get_logger()

class UploadService:
    def __init__(self, users_collection: AsyncIOMotorCollection):
        self.users_collection = users_collection
        self.upload_dir = "uploads"
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
        
        # Create subdirectories
        for subdir in ["images", "documents", "avatars", "tarot-cards"]:
            subdir_path = os.path.join(self.upload_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
    
    async def upload_image(
        self, 
        file: UploadFile, 
        user_id: Optional[str], 
        category: str, 
        description: Optional[str]
    ) -> FileUploadResponse:
        """Upload and process an image file"""
        try:
            # Read file content
            content = await file.read()
            
            # Validate image
            try:
                image = Image.open(io.BytesIO(content))
                image.verify()
            except Exception:
                raise ValidationException("Invalid image file")
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
            filename = f"{file_id}{extension}"
            
            # Determine subdirectory
            subdir = "images"
            if category == "avatar":
                subdir = "avatars"
            elif category == "tarot-card":
                subdir = "tarot-cards"
            
            file_path = os.path.join(self.upload_dir, subdir, filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Create file upload record
            file_upload = FileUpload(
                id=file_id,
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                content_type=file.content_type,
                category=category,
                description=description,
                user_id=user_id,
                uploaded_at=datetime.utcnow(),
                file_type="image"
            )
            
            # Save to database
            await self._save_file_record(file_upload)
            
            logger.info("Image uploaded successfully", 
                       file_id=file_id,
                       user_id=user_id,
                       category=category)
            
            return FileUploadResponse(**file_upload.dict())
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error("Failed to upload image", error=str(e))
            raise DatabaseException(f"Failed to upload image: {str(e)}")
    
    async def upload_document(
        self, 
        file: UploadFile, 
        user_id: Optional[str], 
        category: str, 
        description: Optional[str]
    ) -> FileUploadResponse:
        """Upload a document file"""
        try:
            # Read file content
            content = await file.read()
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            extension = os.path.splitext(file.filename)[1] if file.filename else ""
            filename = f"{file_id}{extension}"
            
            file_path = os.path.join(self.upload_dir, "documents", filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Create file upload record
            file_upload = FileUpload(
                id=file_id,
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                content_type=file.content_type,
                category=category,
                description=description,
                user_id=user_id,
                uploaded_at=datetime.utcnow(),
                file_type="document"
            )
            
            # Save to database
            await self._save_file_record(file_upload)
            
            logger.info("Document uploaded successfully", 
                       file_id=file_id,
                       user_id=user_id,
                       category=category)
            
            return FileUploadResponse(**file_upload.dict())
            
        except Exception as e:
            logger.error("Failed to upload document", error=str(e))
            raise DatabaseException(f"Failed to upload document: {str(e)}")
    
    async def upload_avatar(
        self, 
        file: UploadFile, 
        user_id: str
    ) -> FileUploadResponse:
        """Upload user avatar"""
        try:
            # Validate image
            content = await file.read()
            try:
                image = Image.open(io.BytesIO(content))
                image.verify()
            except Exception:
                raise ValidationException("Invalid image file")
            
            # Generate filename
            file_id = str(uuid.uuid4())
            extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
            filename = f"avatar_{user_id}_{file_id}{extension}"
            
            file_path = os.path.join(self.upload_dir, "avatars", filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Create file upload record
            file_upload = FileUpload(
                id=file_id,
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                content_type=file.content_type,
                category="avatar",
                description="User avatar",
                user_id=user_id,
                uploaded_at=datetime.utcnow(),
                file_type="image"
            )
            
            # Save to database
            await self._save_file_record(file_upload)
            
            # Update user avatar URL
            await self._update_user_avatar(user_id, file_path)
            
            logger.info("Avatar uploaded successfully", 
                       file_id=file_id,
                       user_id=user_id)
            
            return FileUploadResponse(**file_upload.dict())
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error("Failed to upload avatar", error=str(e))
            raise DatabaseException(f"Failed to upload avatar: {str(e)}")
    
    async def upload_tarot_card_image(
        self, 
        file: UploadFile, 
        card_name: str, 
        card_name_vi: str
    ) -> FileUploadResponse:
        """Upload tarot card image"""
        try:
            # Validate image
            content = await file.read()
            try:
                image = Image.open(io.BytesIO(content))
                image.verify()
            except Exception:
                raise ValidationException("Invalid image file")
            
            # Generate filename
            file_id = str(uuid.uuid4())
            extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
            filename = f"tarot_{card_name.replace(' ', '_')}_{file_id}{extension}"
            
            file_path = os.path.join(self.upload_dir, "tarot-cards", filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Create file upload record
            file_upload = FileUpload(
                id=file_id,
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                content_type=file.content_type,
                category="tarot-card",
                description=f"Tarot card: {card_name} ({card_name_vi})",
                user_id=None,  # System upload
                uploaded_at=datetime.utcnow(),
                file_type="image"
            )
            
            # Save to database
            await self._save_file_record(file_upload)
            
            logger.info("Tarot card image uploaded successfully", 
                       file_id=file_id,
                       card_name=card_name)
            
            return FileUploadResponse(**file_upload.dict())
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error("Failed to upload tarot card image", error=str(e))
            raise DatabaseException(f"Failed to upload tarot card image: {str(e)}")
    
    async def get_user_files(
        self, 
        user_id: str, 
        category: Optional[str] = None, 
        limit: int = 50
    ) -> List[FileUploadResponse]:
        """Get user files"""
        try:
            # This would typically query a separate files collection
            # For now, we'll return an empty list as placeholder
            logger.info("Getting user files", user_id=user_id, category=category)
            return []
            
        except Exception as e:
            logger.error("Failed to get user files", error=str(e))
            raise DatabaseException(f"Failed to get user files: {str(e)}")
    
    async def get_file_info(self, file_id: str) -> FileUploadResponse:
        """Get file information"""
        try:
            # This would typically query a separate files collection
            # For now, we'll raise an exception as placeholder
            logger.info("Getting file info", file_id=file_id)
            raise NotFoundException("File not found")
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error("Failed to get file info", error=str(e))
            raise DatabaseException(f"Failed to get file info: {str(e)}")
    
    async def delete_file(self, file_id: str, user_id: str) -> None:
        """Delete a file"""
        try:
            # This would typically delete from files collection and file system
            # For now, we'll log as placeholder
            logger.info("Deleting file", file_id=file_id, user_id=user_id)
            
        except Exception as e:
            logger.error("Failed to delete file", error=str(e))
            raise DatabaseException(f"Failed to delete file: {str(e)}")
    
    async def resize_image(
        self, 
        file_id: str, 
        width: int, 
        height: int, 
        quality: int = 85
    ) -> Dict[str, Any]:
        """Resize an image"""
        try:
            # This would typically load the image, resize it, and save
            # For now, we'll return a placeholder response
            logger.info("Resizing image", file_id=file_id, width=width, height=height)
            
            return {
                "file_id": file_id,
                "new_width": width,
                "new_height": height,
                "quality": quality,
                "status": "resized"
            }
            
        except Exception as e:
            logger.error("Failed to resize image", error=str(e))
            raise DatabaseException(f"Failed to resize image: {str(e)}")
    
    async def crop_image(
        self, 
        file_id: str, 
        x: int, 
        y: int, 
        width: int, 
        height: int
    ) -> Dict[str, Any]:
        """Crop an image"""
        try:
            # This would typically load the image, crop it, and save
            # For now, we'll return a placeholder response
            logger.info("Cropping image", file_id=file_id, x=x, y=y, width=width, height=height)
            
            return {
                "file_id": file_id,
                "crop_x": x,
                "crop_y": y,
                "crop_width": width,
                "crop_height": height,
                "status": "cropped"
            }
            
        except Exception as e:
            logger.error("Failed to crop image", error=str(e))
            raise DatabaseException(f"Failed to crop image: {str(e)}")
    
    async def compress_image(self, file_id: str, quality: int = 85) -> Dict[str, Any]:
        """Compress an image"""
        try:
            # This would typically load the image, compress it, and save
            # For now, we'll return a placeholder response
            logger.info("Compressing image", file_id=file_id, quality=quality)
            
            return {
                "file_id": file_id,
                "quality": quality,
                "status": "compressed"
            }
            
        except Exception as e:
            logger.error("Failed to compress image", error=str(e))
            raise DatabaseException(f"Failed to compress image: {str(e)}")
    
    async def bulk_upload_images(
        self, 
        files: List[UploadFile], 
        user_id: Optional[str], 
        category: str
    ) -> List[FileUploadResponse]:
        """Bulk upload multiple images"""
        try:
            results = []
            
            for file in files:
                try:
                    result = await self.upload_image(file, user_id, category, None)
                    results.append(result)
                except Exception as e:
                    logger.error("Failed to upload file in bulk", 
                                filename=file.filename,
                                error=str(e))
                    # Continue with other files
            
            logger.info("Bulk upload completed", 
                       total_files=len(files),
                       successful_uploads=len(results))
            
            return results
            
        except Exception as e:
            logger.error("Failed to bulk upload images", error=str(e))
            raise DatabaseException(f"Failed to bulk upload images: {str(e)}")
    
    async def get_storage_usage(self, user_id: str) -> Dict[str, Any]:
        """Get user storage usage"""
        try:
            # This would typically calculate total file sizes for the user
            # For now, we'll return a placeholder response
            logger.info("Getting storage usage", user_id=user_id)
            
            return {
                "user_id": user_id,
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "file_count": 0,
                "usage_by_category": {}
            }
            
        except Exception as e:
            logger.error("Failed to get storage usage", error=str(e))
            raise DatabaseException(f"Failed to get storage usage: {str(e)}")
    
    async def cleanup_storage(self, user_id: str) -> Dict[str, Any]:
        """Clean up user storage (remove old/unused files)"""
        try:
            # This would typically identify and remove old files
            # For now, we'll return a placeholder response
            logger.info("Cleaning up storage", user_id=user_id)
            
            return {
                "user_id": user_id,
                "files_removed": 0,
                "space_freed_bytes": 0,
                "space_freed_mb": 0
            }
            
        except Exception as e:
            logger.error("Failed to cleanup storage", error=str(e))
            raise DatabaseException(f"Failed to cleanup storage: {str(e)}")
    
    async def _save_file_record(self, file_upload: FileUpload) -> None:
        """Save file record to database"""
        try:
            # This would typically save to a separate files collection
            # For now, we'll just log the action
            logger.info("Saving file record", file_id=file_upload.id)
            
        except Exception as e:
            logger.error("Failed to save file record", error=str(e))
            raise DatabaseException(f"Failed to save file record: {str(e)}")
    
    async def _update_user_avatar(self, user_id: str, avatar_path: str) -> None:
        """Update user avatar URL in user record"""
        try:
            # This would typically update the user's avatar_url field
            logger.info("Updating user avatar", user_id=user_id, avatar_path=avatar_path)
            
        except Exception as e:
            logger.error("Failed to update user avatar", error=str(e))
            raise DatabaseException(f"Failed to update user avatar: {str(e)}")
