from .base import *  # Import all base settings
import dj_database_url

DEBUG = False

# -------------- SECURITY SETTINGS --------------
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# -------------- STATIC FILES --------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

# -------------- DATABASE CONFIGURATION --------------
db_config = dj_database_url.config(
    conn_max_age=600,
    conn_health_checks=True,
    ssl_require=True,
)

# Ensure ENGINE is explicitly set for psycopg2
if "ENGINE" not in db_config:
    db_config["ENGINE"] = "django.db.backends.postgresql"

DATABASES = {
    "default": db_config
}

# -------------- HOSTS & CORS --------------
ALLOWED_HOSTS = [
    "ai-face-swap-app.fly.dev",
    "localhost",
    "127.0.0.1",
]

CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-app.netlify.app",  # Replace when deployed
    "https://ai-face-swap-app.fly.dev",
]

# -------------- HEALTH CHECK ENDPOINT --------------
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy"})

# -------------- LOGGING CONFIG --------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
