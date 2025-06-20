# Based on official ageitgey/face_recognition Dockerfile
FROM python:3.10.3-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (based on official ageitgey Dockerfile)
RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    libpq-dev \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

# Build and install dlib from source (CRITICAL - this is the official way)
RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

# Set work directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip3 install --upgrade pip wheel

# Install face_recognition and other Python packages
RUN pip3 install face_recognition
RUN pip3 install -r requirements.txt

# Set dummy environment variables for build time (FIXED: Added HuggingFace vars)
ENV DJANGO_SETTINGS_MODULE=django_project.settings.base
ENV DJANGO_SECRET_KEY=build-time-secret-key
ENV DATABASE_URL=sqlite:///tmp/build.db
ENV CLOUDINARY_CLOUD_NAME=dummy
ENV CLOUDINARY_API_KEY=dummy
ENV CLOUDINARY_API_SECRET=dummy
ENV OPENAI_API_KEY=dummy
ENV HUGGINGFACE_SPACE_NAME=dummy/dummy-space
ENV HUGGINGFACE_API_TOKEN=dummy

# Copy project
COPY . /app/

# Create media directories
RUN mkdir -p /app/media/uploads/selfies
RUN mkdir -p /app/staticfiles

# Try to collect static files (skip if it fails)
RUN python3 manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python3 -c "import requests; requests.get('http://localhost:8000/health/', timeout=10)" || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "django_project.wsgi:application"]