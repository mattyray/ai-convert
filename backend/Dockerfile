# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set Django settings module for build
ENV DJANGO_SETTINGS_MODULE=django_project.settings.base

# Set dummy environment variables for build time
ENV DJANGO_SECRET_KEY=build-time-secret-key
ENV DATABASE_URL=sqlite:///tmp/build.db
ENV CLOUDINARY_CLOUD_NAME=dummy
ENV CLOUDINARY_API_KEY=dummy
ENV CLOUDINARY_API_SECRET=dummy
ENV OPENAI_API_KEY=dummy

# Install system dependencies required for face-recognition and dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    python3-pip \
    git \
    wget \
    pkg-config \
    libpq-dev \
    gcc \
    g++ \
    libatlas-base-dev \
    gfortran \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel

# Install Python dependencies in stages for better debugging
# First install numpy (required for dlib)
RUN pip install --no-cache-dir numpy

# Install dlib separately with verbose output
RUN pip install --no-cache-dir dlib --verbose

# Install face recognition
RUN pip install --no-cache-dir face-recognition

# Install face recognition models (CRITICAL FIX)
RUN pip install --no-cache-dir git+https://github.com/ageitgey/face_recognition_models

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create media directories
RUN mkdir -p /app/media/uploads/selfies
RUN mkdir -p /app/staticfiles

# Try to collect static files (skip if it fails)
RUN python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "django_project.wsgi:application"]