from .base import *
import dj_database_url
import os

DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Database - use Fly.io Postgres
DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL'))
}

# Allowed hosts - update with your Fly.io app name
ALLOWED_HOSTS = [
    'ai-face-swap-app.fly.dev',
    'localhost',
    '127.0.0.1',
]

# CORS settings for your frontend
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-app.netlify.app",  # Will update after frontend deployment
    "https://ai-face-swap-app.fly.dev",
]

# Add health check URL
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy"})

# Add to your main urls.py
# path('health/', health_check, name='health-check'),

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}