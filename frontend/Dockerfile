# backend/Dockerfile

FROM python:3.10.3-slim-bullseye

# Avoid prompts during install
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies only once
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    gfortran \
    git \
    libatlas-base-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libpq-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Pre-create working dir
WORKDIR /app

# 👇 Copy and install only requirements first (layer cache win)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir numpy && \
    pip install --no-cache-dir dlib && \
    pip install --no-cache-dir face-recognition && \
    pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . /app/

# Create necessary dirs for media/static
RUN mkdir -p /app/media/uploads/selfies /app/staticfiles

# Optional: run collectstatic here if needed
# RUN python manage.py collectstatic --noinput || echo "Skipping collectstatic"

# Non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "django_project.wsgi:application"]
