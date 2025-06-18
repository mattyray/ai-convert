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

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # ✅ This is required for collectstatic
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

    'imagegen',
    'corsheaders',

    'rest_framework',
    'rest_framework.authtoken', 
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# Allauth
SITE_ID = env.int("DJANGO_SITE_ID", default=1)
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = "email"
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

HUGGINGFACE_FACESWAP_URL = env('HUGGINGFACE_FACESWAP_URL', 
    default='https://mnraynor90-facefusionfastapi-private.hf.space')

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "https://*.netlify.app",  # Will be updated with actual Netlify URL
    "https://*.fly.dev",      # Allow all fly.dev subdomains
]

CORS_ALLOW_CREDENTIALS = True