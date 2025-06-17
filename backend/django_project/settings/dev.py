# backend/django_project/settings/dev.py
from .base import *

DEBUG = True

# Database for local development
DATABASES = {
    "default": env.db_url("DATABASE_URL", default="postgresql://postgres:postgres_password@db:5432/faceswap_db")
}

# Add localhost to allowed hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[
    "localhost", "127.0.0.1", "0.0.0.0", "backend"
])

# CORS settings for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]