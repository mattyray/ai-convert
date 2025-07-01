from django.db import models
from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils import timezone
from datetime import timedelta
import cloudinary.uploader

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
    
    def delete_from_cloudinary(self):
        """Delete associated images from Cloudinary"""
        deleted_files = []
        try:
            if self.selfie and hasattr(self.selfie, 'public_id'):
                cloudinary.uploader.destroy(self.selfie.public_id)
                deleted_files.append(f"selfie:{self.selfie.public_id}")
        except Exception as e:
            print(f"⚠️ Error deleting selfie: {e}")
        try:
            if self.output_image and hasattr(self.output_image, 'public_id'):
                cloudinary.uploader.destroy(self.output_image.public_id)
                deleted_files.append(f"output:{self.output_image.public_id}")
        except Exception as e:
            print(f"⚠️ Error deleting output: {e}")
        return deleted_files
    
    def expire_and_cleanup(self):
        """Mark as expired and delete from Cloudinary"""
        deleted_files = self.delete_from_cloudinary()
        self.is_expired = True
        self.cleanup_attempted = True
        self.save()
        return deleted_files
    
    @property
    def is_expired_now(self):
        """Check if image should be expired"""
        return timezone.now() > self.expires_at


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