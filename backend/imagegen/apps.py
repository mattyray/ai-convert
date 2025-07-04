from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ImagegenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'imagegen'

    def ready(self):
        """Called when Django starts up"""
        try:
            from .background_cleanup import start_background_cleanup
            start_background_cleanup()
            logger.info("✅ ImageGen app ready - background cleanup initialized")
        except Exception as e:
            logger.error(f"❌ Failed to start background cleanup: {e}")