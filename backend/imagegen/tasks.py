from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
from .models import GeneratedImage
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def cleanup_expired_images_task(self):
    """
    Celery task to clean up expired images from Cloudinary
    Runs every 6 hours automatically
    """
    try:
        logger.info("🧹 Starting scheduled cleanup of expired images")
        
        # Find expired images
        now = timezone.now()
        expired_images = GeneratedImage.objects.filter(
            expires_at__lt=now,
            is_expired=False,
            cleanup_attempted=False
        )
        
        count = expired_images.count()
        logger.info(f"📊 Found {count} expired images to clean up")
        
        if count == 0:
            logger.info("✅ No expired images found")
            return "No images to clean up"
        
        # Process cleanup
        deleted_count = 0
        failed_count = 0
        
        for img in expired_images:
            try:
                deleted_files = img.expire_and_cleanup()
                logger.info(f"✅ Cleaned up image {img.id}: {deleted_files}")
                deleted_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to cleanup image {img.id}: {e}")
                failed_count += 1
        
        result = f"Cleanup complete: {deleted_count} deleted, {failed_count} failed"
        logger.info(f"🎉 {result}")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Cleanup task failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def manual_cleanup_task(force=False):
    """
    Manual cleanup task for testing/admin use
    """
    if force:
        # Force cleanup all images (for testing)
        call_command('cleanup_expired_images', '--force')
        return "Force cleanup completed"
    else:
        # Normal cleanup
        call_command('cleanup_expired_images')
        return "Manual cleanup completed"