import sys
import threading
import time
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class BackgroundCleanupThread(threading.Thread):
    """Background thread that periodically cleans up expired images"""
    
    def __init__(self):
        super().__init__(daemon=True)  # Daemon thread dies when main program exits
        self.stop_event = threading.Event()
        self.cleanup_interval = 6 * 60 * 60  # 6 hours in seconds
        
    def run(self):
        logger.info("🧹 Background cleanup thread started")
        
        while not self.stop_event.is_set():
            try:
                # Wait for the interval or until stop is requested
                if self.stop_event.wait(self.cleanup_interval):
                    break  # Stop event was set
                
                # Perform cleanup
                self.cleanup_expired_images()
                
            except Exception as e:
                logger.error(f"❌ Background cleanup error: {e}")
                # Continue running even if there's an error
    
    def cleanup_expired_images(self):
        """Clean up expired images"""
        try:
            from .models import GeneratedImage
            
            logger.info("🧹 Starting background cleanup of expired images")
            
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
                return
            
            deleted_count = 0
            failed_count = 0
            
            for img in expired_images:
                try:
                    deleted_files = img.expire_and_cleanup()
                    deleted_count += 1
                    logger.info(f"✅ Cleaned up image {img.id}: {deleted_files}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ Failed to cleanup image {img.id}: {e}")
            
            logger.info(f"🎉 Background cleanup completed: {deleted_count} deleted, {failed_count} failed")
            
        except Exception as e:
            logger.error(f"❌ Background cleanup failed: {e}")
    
    def stop(self):
        """Stop the cleanup thread"""
        logger.info("🛑 Stopping background cleanup thread")
        self.stop_event.set()

# Global cleanup thread instance
_cleanup_thread = None

def start_background_cleanup():
    """Start the background cleanup thread (call once at startup)"""
    global _cleanup_thread
    
    # Skip only for migrations and celery workers (allow DEBUG mode)
    if ('migrate' in sys.argv or 
        'makemigrations' in sys.argv or
        getattr(settings, 'IS_CELERY_WORKER', False)):
        logger.info("⏭️ Skipping background cleanup (migration/celery mode)")
        return
    
    if _cleanup_thread is None or not _cleanup_thread.is_alive():
        _cleanup_thread = BackgroundCleanupThread()
        _cleanup_thread.start()
        logger.info("✅ Background cleanup thread started")
    else:
        logger.info("ℹ️ Background cleanup thread already running")

def stop_background_cleanup():
    """Stop the background cleanup thread"""
    global _cleanup_thread
    if _cleanup_thread and _cleanup_thread.is_alive():
        _cleanup_thread.stop()
        _cleanup_thread = None