from environ import Env
from pathlib import Path
import stripe
import os
from django.core.management.utils import get_random_secret_key

print("💥 settings.py loaded from latest build")

# Cloudinary Configuration
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Initialize environment variables
env = Env()

# For build time, provide defaults for all required env vars
cloudinary_url = env('CLOUDINARY_URL', default='')
if cloudinary_url:
    # Parse the cloudinary://api_key:api_secret@cloud_name format
    import re
    match = re.match(r'cloudinary://(\d+):([^@]+)@(.+)', cloudinary_url)
    if match:
        api_key, api_secret, cloud_name = match.groups()
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': cloud_name,
            'API_KEY': api_key,
            'API_SECRET': api_secret,
        }
        print(f"✅ Cloudinary configured from CLOUDINARY_URL for cloud: {cloud_name}")
    else:
        print("⚠️  Invalid CLOUDINARY_URL format, using fallback")
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default='dddye9wli'),
            'API_KEY': env('CLOUDINARY_API_KEY', default='dummy'),
            'API_SECRET': env('CLOUDINARY_API_SECRET', default='dummy'),
        }
else:
    # Fallback to individual environment variables
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default='dddye9wli'),
        'API_KEY': env('CLOUDINARY_API_KEY', default='dummy'),
        'API_SECRET': env('CLOUDINARY_API_SECRET', default='dummy'),
    }
    print("⚠️  Using individual Cloudinary env vars")

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# Stripe
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='pk_test_dummy')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='sk_test_dummy')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='whsec_dummy')
stripe.api_key = STRIPE_SECRET_KEY

OPENAI_API_KEY = env("OPENAI_API_KEY", default="dummy")

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security - use Django's built-in secret key generator for build time
SECRET_KEY = env("DJANGO_SECRET_KEY", default=get_random_secret_key())
DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[
    "localhost", "127.0.0.1", "0.0.0.0", "web", "*.fly.dev"
])

# 🔥 SIMPLE CELERY FIX - detect if this is a Celery worker
import sys

# Check if this is a Celery worker process
IS_CELERY = (
    os.environ.get('IS_CELERY_WORKER') == 'true' or
    'celery' in sys.argv[0] or 
    'worker' in sys.argv or
    'beat' in sys.argv
)

# Disable CSRF for specific API endpoints
CSRF_EXEMPT_URLS = [
    r'^/api/imagegen/generate/$',
    r'^/api/imagegen/randomize/$',
    r'^/api/accounts/auth/google/$',      # 🔥 ADD THIS
    r'^/api/accounts/auth/facebook/$',   
]

class DisableCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import re
        # Check if this URL should be exempt from CSRF
        for pattern in CSRF_EXEMPT_URLS:
            if re.match(pattern, request.path_info):
                setattr(request, '_dont_enforce_csrf_checks', True)
                print(f"🔓 CSRF exempted for: {request.path_info}")  # Debug log
        
        return self.get_response(request)

if IS_CELERY:
    print("🔧 Celery worker detected - applying minimal configuration...")
    
    # Minimal apps for Celery workers
    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'cloudinary_storage',
        'cloudinary',
        
        # Custom apps (needed for tasks)
        'accounts.apps.AccountsConfig',
        'faceswap.apps.FaceswapConfig',
        'imagegen',
        
        # Celery apps
        'django_celery_beat',
        'django_celery_results',
        
        'rest_framework',
        'rest_framework.authtoken',
    ]
    
    # Minimal middleware for Celery workers
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
    
    # Use minimal URLs for Celery
    ROOT_URLCONF = 'django_project.celery_urls'
    
else:
    print("🌐 Standard Django configuration loaded")
    
    # Full apps for Django web server
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'cloudinary_storage',
        'cloudinary',

        # Custom apps
        'accounts.apps.AccountsConfig',
        'chat.apps.ChatConfig',
        'faceswap.apps.FaceswapConfig',

        # Third-party
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.facebook',  # 🔥 ADD THIS


        'imagegen',
        'corsheaders',

        'rest_framework',
        'rest_framework.authtoken',

        'django_celery_beat',
        'django_celery_results', 
    ]

    # Full middleware for Django web server
    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
        'django_project.settings.base.DisableCSRFMiddleware',  # 🔥 Add this BEFORE CsrfViewMiddleware
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'allauth.account.middleware.AccountMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'imagegen.middleware.UsageLimitMiddleware',
    ]
    ROOT_URLCONF = 'django_project.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'

# Database - provide default for build time
DATABASES = {
    "default": env.db_url("DATABASE_URL", default="sqlite:///tmp/build.db")
}

# Auth
AUTH_USER_MODEL = 'accounts.CustomUser'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth - FIXED: Updated to new settings format
SITE_ID = env.int("DJANGO_SITE_ID", default=1)

# ✅ NEW: Updated allauth settings (no more deprecation warnings)
ACCOUNT_LOGIN_METHODS = {'email'}  # Replaces ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_SIGNUP_FIELDS = ['email', 'password1', 'password2']  # Replaces EMAIL_REQUIRED and USERNAME_REQUIRED
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_SIGNUP_REDIRECT_URL = '/dashboard/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID', default='test-client-id'),
            'secret': env('GOOGLE_CLIENT_SECRET', default='test-secret'),
            'key': ''
        }
    },
    # 🔥 ADD FACEBOOK
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
        'APP': {
            'client_id': env('FACEBOOK_CLIENT_ID', default='test-client-id'),
            'secret': env('FACEBOOK_CLIENT_SECRET', default='test-secret'),
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files - properly configured for collectstatic
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR.parent / "static"] if (BASE_DIR.parent / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Staticfiles finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Email
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.locmem.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.test.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="test@test.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="testpassword")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@test.com")

# Security
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
    SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=2592000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
    SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
    SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
    CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
else:
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Other
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

# HuggingFace Configuration - FIXED
HUGGINGFACE_SPACE_NAME = env('HUGGINGFACE_SPACE_NAME', default='mnraynor90/facefusionfastapi-private')
HUGGINGFACE_API_TOKEN = env("HUGGINGFACE_API_TOKEN", default="dummy")

print(f"🔧 HuggingFace Space: {HUGGINGFACE_SPACE_NAME}")
print(f"🔑 HuggingFace Token: {'***configured***' if HUGGINGFACE_API_TOKEN != 'dummy' else 'NOT SET'}")

# CORS Configuration (only for non-Celery)
if not IS_CELERY:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://ai-convert.netlify.app",
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_PREFLIGHT_MAX_AGE = 86400

    CORS_ALLOW_HEADERS = [
        'accept', 'accept-encoding', 'authorization', 'content-type', 'dnt', 'origin',
        'user-agent', 'x-csrftoken', 'x-requested-with', 'cache-control', 'pragma',
        'expires', 'content-length', 'host', 'referer', 'sec-ch-ua', 'sec-ch-ua-mobile',
        'sec-ch-ua-platform', 'sec-fetch-dest', 'sec-fetch-mode', 'sec-fetch-site',
    ]

    CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'HEAD']

# Conditional Logging
if IS_CELERY:
    # Simplified logging for Celery workers
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
            'celery': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
    
    # Disable problematic system checks for Celery
    SILENCED_SYSTEM_CHECKS = [
        'admin.E404',
        'urls.E007',
        'urls.W005',
        'security.W004',
        'security.W008',
    ]
    
    print("✅ Celery worker configuration applied")
else:
    # Full logging for Django
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'corsheaders': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_EXPIRES = 7 * 24 * 60 * 60  # 7 days
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Periodic Tasks Configuration
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-images': {
        'task': 'imagegen.tasks.cleanup_expired_images_task',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'options': {'expires': 60 * 60}  # Task expires in 1 hour if not picked up
    },
}

# Fix session cookies for frontend - IMPROVED
SESSION_COOKIE_SAMESITE = 'Lax'  # Try Lax instead of None
SESSION_COOKIE_SECURE = False    # For development (HTTP)
SESSION_COOKIE_HTTPONLY = True   # Security
SESSION_COOKIE_AGE = 1209600     # 2 weeks
CSRF_COOKIE_SAMESITE = 'Lax'     # Also fix CSRF cookies
CSRF_COOKIE_SECURE = False       # For development

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

print(f"✅ Settings loaded - IS_CELERY: {IS_CELERY}")