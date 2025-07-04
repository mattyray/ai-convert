from django.db import models
from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils import timezone
from datetime import timedelta
import cloudinary.uploader
import re
import logging

logger = logging.getLogger(__name__)

def get_expiration_time():
    """Get expiration time 48 hours from now"""
    return timezone.now() + timedelta(hours=48)

class GeneratedImage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_images"
    )
    prompt = models.TextField()
    match_name = models.CharField(max_length=100)
    selfie = models.ImageField(
        upload_to="uploads/selfies/",
        storage=MediaCloudinaryStorage()
    )
    output_image = models.ImageField(
        upload_to="uploads/fused/", 
        null=True, 
        blank=True,
        storage=MediaCloudinaryStorage()
    )
    output_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_time)
    is_expired = models.BooleanField(default=False)
    cleanup_attempted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.match_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def extract_public_id_from_url(self, image_url):
        """
        Extract Cloudinary public_id from URL using official recommendation
        
        Examples:
        - https://res.cloudinary.com/dddye9wli/image/upload/v1/uploads/selfies/compressed_selfie_heskpo
        - https://res.cloudinary.com/cloud/image/upload/v1647610701/uploads/fused/image.jpg
        
        Returns: uploads/selfies/compressed_selfie_heskpo
        """
        if not image_url:
            return None
            
        try:
            # Split URL by '/'
            url_parts = image_url.split('/')
            
            # Find the 'upload' part
            upload_index = -1
            for i, part in enumerate(url_parts):
                if part == 'upload':
                    upload_index = i
                    break
            
            if upload_index == -1:
                logger.error(f"❌ 'upload' not found in URL: {image_url}")
                return None
            
            # Skip the version part (next after 'upload')
            # URL structure: .../upload/v1/public_id or .../upload/v1647610701/public_id
            if upload_index + 1 >= len(url_parts):
                logger.error(f"❌ No version part after 'upload': {image_url}")
                return None
            
            # Start from 2 positions after 'upload' (skip version)
            public_id_parts = url_parts[upload_index + 2:]
            
            if not public_id_parts:
                logger.error(f"❌ No public_id parts found: {image_url}")
                return None
            
            # Join the remaining parts
            public_id = '/'.join(public_id_parts)
            
            # Remove file extension if present (for URLs with extensions)
            if '.' in public_id:
                # Only remove extension if it's at the very end
                last_part = public_id.split('/')[-1]
                if '.' in last_part:
                    # Remove extension from last part only
                    last_part_no_ext = '.'.join(last_part.split('.')[:-1])
                    public_id_parts = public_id.split('/')[:-1] + [last_part_no_ext]
                    public_id = '/'.join(public_id_parts)
            
            logger.info(f"✅ Extracted public_id: {public_id} from URL: {image_url}")
            return public_id
                
        except Exception as e:
            logger.error(f"❌ Error extracting public_id from {image_url}: {e}")
            return None
    
    def get_image_public_id(self, image_field):
        """Get public_id for an image field"""
        try:
            # Method 1: Try to get public_id directly (if available)
            if hasattr(image_field, 'public_id') and image_field.public_id:
                return image_field.public_id
            
            # Method 2: Extract from URL
            if hasattr(image_field, 'url') and image_field.url:
                return self.extract_public_id_from_url(image_field.url)
            
            # Method 3: Extract from name/path
            if hasattr(image_field, 'name') and image_field.name:
                # Remove file extension
                name_without_ext = image_field.name.rsplit('.', 1)[0]
                return name_without_ext
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting public_id: {e}")
            return None
    
    def delete_from_cloudinary(self):
        """Delete associated images from Cloudinary"""
        deleted_files = []
        
        # Delete selfie
        if self.selfie:
            try:
                public_id = self.get_image_public_id(self.selfie)
                if public_id:
                    result = cloudinary.uploader.destroy(public_id)
                    logger.info(f"🗑️ Cloudinary delete selfie result: {result}")
                    deleted_files.append(f"selfie:{public_id}")
                else:
                    logger.warning(f"⚠️ Could not get public_id for selfie: {self.selfie}")
            except Exception as e:
                logger.error(f"❌ Error deleting selfie {self.id}: {e}")
        
        # Delete output image
        if self.output_image:
            try:
                public_id = self.get_image_public_id(self.output_image)
                if public_id:
                    result = cloudinary.uploader.destroy(public_id)
                    logger.info(f"🗑️ Cloudinary delete output result: {result}")
                    deleted_files.append(f"output:{public_id}")
                else:
                    logger.warning(f"⚠️ Could not get public_id for output_image: {self.output_image}")
            except Exception as e:
                logger.error(f"❌ Error deleting output_image {self.id}: {e}")
        
        return deleted_files
    
    def expire_and_cleanup(self):
        """Mark as expired and delete from Cloudinary"""
        logger.info(f"🧹 Starting cleanup for GeneratedImage {self.id}")
        
        deleted_files = self.delete_from_cloudinary()
        self.is_expired = True
        self.cleanup_attempted = True
        self.save()
        
        logger.info(f"✅ Cleanup completed for GeneratedImage {self.id}: {deleted_files}")
        return deleted_files
    
    @property
    def is_expired_now(self):
        """Check if image should be expired"""
        return timezone.now() > self.expires_at
    
    class Meta:
        ordering = ['-created_at']


class UsageSession(models.Model):
    """Track usage limits for anonymous users"""
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    matches_used = models.IntegerField(default=0)
    randomizes_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    MAX_MATCHES = 1
    MAX_RANDOMIZES = 1
    
    def __str__(self):
        return f"Session {self.session_key} - M:{self.matches_used}/{self.MAX_MATCHES} R:{self.randomizes_used}/{self.MAX_RANDOMIZES}"
    
    @property
    def can_match(self):
        return self.matches_used < self.MAX_MATCHES
    
    @property
    def can_randomize(self):
        return self.randomizes_used < self.MAX_RANDOMIZES
    
    @property
    def is_limited(self):
        return not self.can_match and not self.can_randomize
    
    def use_match(self):
        if self.can_match:
            self.matches_used += 1
            self.save()
            return True
        return False
    
    def use_randomize(self):
        if self.can_randomize:
            self.randomizes_used += 1
            self.save()
            return True
        return False
    
    @classmethod
    def get_or_create_for_session(cls, session_key):
        usage_session, created = cls.objects.get_or_create(
            session_key=session_key,
            defaults={'matches_used': 0, 'randomizes_used': 0}
        )
        return usage_session