from .base import *
import os, sys
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

# ---------------- SECURITY ----------------
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

# ---------------- STATIC FILES ----------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------- DATABASE ----------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL is not set in environment variables.")

parsed = dj_database_url.parse(
    DATABASE_URL,
    conn_max_age=600,
    conn_health_checks=True,
)

# Add engine if missing
if "ENGINE" not in parsed:
    parsed["ENGINE"] = "django.db.backends.postgresql"

# Print to stderr (only visible in Fly logs)
print("✅ DEBUG: Parsed DATABASE_URL →", parsed, file=sys.stderr)

# Confirm required keys
for key in ("ENGINE", "NAME", "USER", "PASSWORD", "HOST", "PORT"):
    if key not in parsed:
        raise ImproperlyConfigured(f"Missing {key} in parsed DATABASE_URL")

DATABASES = {"default": parsed}

# ---------------- HOSTS ----------------
ALLOWED_HOSTS = [
    "ai-face-swap-app.fly.dev",
    "localhost",
    "127.0.0.1",
]

CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-app.netlify.app",
    "https://ai-face-swap-app.fly.dev",
]

# ---------------- HEALTH CHECK ----------------
from django.http import JsonResponse
def health_check(request):
    return JsonResponse({"status": "healthy"})

# ---------------- LOGGING ----------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
