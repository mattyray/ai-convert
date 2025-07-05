# HistoryFace - AI Historical Transformation

Transform yourself into historical figures using cutting-edge AI face swap technology! Upload a selfie and discover which historical personality you resemble most, then see yourself transformed into iconic figures like Napoleon, Cleopatra, Leonardo da Vinci, and more.

## ✨ Features

- **🎭 AI Face Matching**: Advanced facial recognition matches you with historical figures
- **🎲 Random Transformations**: Get surprised with random historical figure transformations  
- **⚡ Real-time Processing**: Live progress tracking with detailed status updates
- **🔐 Google Authentication**: Secure login with Google OAuth
- **📱 Responsive Design**: Works seamlessly on desktop and mobile
- **☁️ Cloud Storage**: Images stored securely with Cloudinary
- **🚀 Background Processing**: Celery-powered async image processing
- **📊 Processing Analytics**: Detailed logging and monitoring

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  React Frontend │    │  Django Backend │    │  External APIs  │
│                 │    │                 │    │                 │
│  ┌─────────────┐│    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│  │   Upload    ││────│ │    API      │ │────│ │ HuggingFace │ │
│  │   Component ││    │ │  Endpoints  │ │    │ │   Spaces    │ │
│  └─────────────┘│    │ └─────────────┘ │    │ └─────────────┘ │
│  ┌─────────────┐│    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│  │ Auth Modal  ││────│ │ User Models │ │────│ │   Google    │ │
│  └─────────────┘│    │ └─────────────┘ │    │ │   OAuth     │ │
│  ┌─────────────┐│    │ ┌─────────────┐ │    │ └─────────────┘ │
│  │   Results   ││────│ │   Celery    │ │    │ ┌─────────────┐ │
│  │   Display   ││    │ │   Workers   │ │────│ │ Cloudinary  │ │
│  └─────────────┘│    │ └─────────────┘ │    │ │   Storage   │ │
└─────────────────┘    └─────────────────┘    │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                       ┌─────────────────┐    │ │   Stripe    │ │
                       │   Data Storage  │    │ │  Payments   │ │
                       │                 │    │ └─────────────┘ │
                       │ ┌─────────────┐ │    └─────────────────┘
                       │ │ PostgreSQL  │ │
                       │ │  Database   │ │
                       │ └─────────────┘ │
                       │ ┌─────────────┐ │
                       │ │    Redis    │ │
                       │ │   Cache     │ │
                       │ └─────────────┘ │
                       └─────────────────┘
```

## 📋 API Flow Diagram

```
Frontend Upload → Django API → Face Recognition → HuggingFace → Result Storage
     │              │              │                 │              │
     │              │              │                 │              │
     ▼              ▼              ▼                 ▼              ▼
┌─────────┐   ┌─────────────┐  ┌──────────┐    ┌──────────┐   ┌──────────┐
│ User    │   │ Image       │  │ Facial   │    │ AI Face  │   │ Result   │
│ Uploads │──▶│ Validation  │─▶│ Analysis │───▶│ Swapping │──▶│ Storage  │
│ Selfie  │   │ & Storage   │  │ & Match  │    │ Process  │   │ & Return │
└─────────┘   └─────────────┘  └──────────┘    └──────────┘   └──────────┘
                    │              │                 │              │
                    ▼              ▼                 ▼              ▼
              ┌─────────────┐  ┌──────────┐    ┌──────────┐   ┌──────────┐
              │ Cloudinary  │  │ Database │    │ Celery   │   │ Frontend │
              │ Image CDN   │  │ Logging  │    │ Queue    │   │ Display  │
              └─────────────┘  └──────────┘    └──────────┘   └──────────┘
```

## 🛠️ Tech Stack

### Backend
- **Django 5.1.6** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database
- **Redis** - Caching and Celery broker
- **Celery** - Background task processing
- **HuggingFace Spaces** - AI face swap processing
- **Cloudinary** - Image storage and CDN
- **face-recognition** - Facial analysis library

### Frontend  
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **Axios** - HTTP client
- **Lucide React** - Icon library

### Infrastructure
- **Docker** - Containerization
- **Fly.io** - Backend deployment
- **Netlify** - Frontend deployment
- **GitHub Actions** - CI/CD (planned)

## 📁 Project Structure & Apps

### Django Applications

#### **🔐 accounts/**
Custom user authentication and profile management
```
accounts/
├── models.py          # CustomUser model with email-based auth
├── views.py           # User registration, login, profile APIs
├── serializers.py     # User data serialization
├── social_auth.py     # Google/Facebook OAuth integration
├── admin.py           # Django admin customization
└── urls.py            # Authentication API endpoints
```
**Purpose**: Handles all user-related functionality including custom email-based authentication, social login (Google/Facebook), and user profile management.

#### **🎭 faceswap/**
Core face swapping functionality
```
faceswap/
├── models.py          # FaceSwapJob model for tracking operations
├── views.py           # Face swap API endpoints
├── serializers.py     # Face swap request/response serialization
├── huggingface_utils.py # HuggingFace Spaces integration
├── admin.py           # Admin interface for job monitoring
└── urls.py            # Face swap API routes
```
**Purpose**: Manages the core face swapping operations, integrating with HuggingFace Spaces for AI processing and tracking job status.

#### **🖼️ imagegen/**
Image generation and processing pipeline
```
imagegen/
├── models.py          # GeneratedImage model and usage tracking
├── views/
│   ├── generation_views.py   # Main image processing endpoints
│   └── management_views.py   # Image management and status
├── serializers.py     # Image data serialization
├── face_match.py      # Facial recognition and historical matching
├── utils.py           # Image compression and optimization
├── middleware.py      # Usage limit enforcement
├── admin.py           # Admin interface for image management
└── urls.py            # Image processing API routes
```
**Purpose**: Handles the complete image processing workflow from upload to historical figure matching to final result generation.

#### **💬 chat/** *(Optional/Future)*
Chat and communication features
```
chat/
├── models.py          # Chat models (planned feature)
├── views.py           # Chat API endpoints
└── urls.py            # Chat routes
```
**Purpose**: Placeholder for future chat functionality, customer support, or AI chat features.

### **🏢 django_project/**
Main project configuration
```
django_project/
├── settings/
│   ├── base.py        # Base configuration
│   ├── dev.py         # Development settings
│   └── prod.py        # Production settings
├── celery.py          # Celery configuration
├── urls.py            # Main URL routing
├── wsgi.py            # WSGI application
└── asgi.py            # ASGI application (for future websockets)
```

## 📦 Third-Party Packages

### **Core Django Packages**
```python
Django==5.1.6                    # Main web framework
djangorestframework==3.16.0      # REST API framework
django-environ==0.12.0           # Environment variable management
django-extensions==4.1           # Useful Django extensions
django-cors-headers==4.6.0       # CORS handling for frontend
whitenoise==6.9.0                # Static file serving
gunicorn==23.0.0                 # WSGI HTTP server
```

### **Authentication & Security**
```python
django-allauth==65.6.0           # Social authentication (Google/Facebook)
django-crispy-forms==2.3         # Better form rendering
crispy-bootstrap5==2024.10       # Bootstrap 5 support for forms
cryptography==44.0.3             # Cryptographic functions
PyJWT==2.10.1                    # JSON Web Token handling
```

### **Database & Caching**
```python
psycopg2-binary==2.9.10          # PostgreSQL adapter
dj-database-url==2.1.0           # Database URL parsing
redis==5.2.0                     # Redis client for caching
```

### **Background Tasks**
```python
celery==5.5.3                    # Distributed task queue
django-celery-beat==2.8.1        # Periodic task scheduling
django-celery-results==2.6.0     # Task result storage
```

### **Cloud Services & APIs**
```python
cloudinary==1.44.0               # Cloud image storage
django-cloudinary-storage==0.3.0 # Django integration for Cloudinary
openai==1.78.1                   # OpenAI API client
stripe==12.0.1                   # Payment processing
httpx==0.28.1                    # Modern HTTP client
requests==2.32.3                 # HTTP library
gradio-client==1.10.3            # HuggingFace Spaces client
```

### **Image Processing & AI**
```python
face-recognition==1.3.0          # Facial recognition library
dlib==20.0.0                     # Machine learning toolkit
Pillow==10.0.0                   # Python Imaging Library
opencv-python==4.8.1.78          # Computer vision library
numpy==2.2.4                     # Numerical computing
```

### **Authentication Services**
```python
google-auth==2.40.3              # Google authentication
google-auth-oauthlib==1.2.2      # Google OAuth2 client
google-auth-httplib2==0.2.0      # Google HTTP transport
```

### **Data Processing**
```python
pandas==2.2.3                    # Data manipulation (for analytics)
openpyxl==3.1.5                  # Excel file handling
tablib==3.8.0                    # Dataset manipulation
python-dateutil==2.9.0.post0     # Date/time utilities
```

### **Development & Testing**
```python
# In requirements-dev.txt
flake8==7.2.0                    # Code linting
mypy==1.15.0                     # Static type checking
pytest==8.3.5                    # Testing framework
pytest-django==4.11.1            # Django integration for pytest
safety==3.5.0                    # Security vulnerability scanner
```

### **System Monitoring**
```python
psutil==5.9.0                    # System and process utilities
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Git**

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/historyface.git
cd historyface
```

### 2. Environment Setup
```bash
# Backend environment
cp .env.example .env
# Edit .env with your configuration (see Environment Variables section)

# Frontend environment  
cd frontend
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 3. Start with Docker (Recommended)
```bash
# From project root
docker-compose up --build

# Services will be available at:
# - Backend: http://localhost:8002
# - Frontend: http://localhost:5173
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### 4. Manual Setup (Development)

#### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Start services
python manage.py runserver 8002
celery -A django_project worker --loglevel=info
celery -A django_project beat --loglevel=info
```

#### Frontend Setup  
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Environment Variables

### Backend (.env)
```bash
# Django Settings
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgresql://postgres:postgres_password@db:5432/faceswap_db

# Redis & Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Cloud Storage
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# AI Services
HUGGINGFACE_SPACE_NAME=your-space-name
HUGGINGFACE_API_TOKEN=hf_your_token_here

# Authentication
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional: Payment & Social
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
FACEBOOK_CLIENT_ID=your-facebook-app-id
FACEBOOK_CLIENT_SECRET=your-facebook-secret
```

### Frontend (.env.local)
```bash
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8002

# Authentication
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_FACEBOOK_APP_ID=your-facebook-app-id
```

## 📖 Usage

### 1. Upload Your Selfie
- Drag and drop or click to select an image
- Supports JPG, PNG, WebP formats
- Maximum file size: 10MB

### 2. Choose Processing Mode
- **🔮 Find My Historical Twin**: AI analyzes your features to find the best match
- **🎲 Surprise Me**: Get randomly matched with any historical figure

### 3. Watch the Magic
- Real-time progress tracking through 4 stages:
  - 📤 Uploading your image securely
  - 🔍 AI analyzing facial features  
  - 👥 Matching with historical figures
  - ✨ Creating your transformation

### 4. Share Your Results
- Download high-quality result images
- Share directly to social media
- Copy image links for posting

## 🔌 API Documentation

### Authentication
```bash
# Google OAuth
POST /api/accounts/auth/google/
Content-Type: application/json
{
  "credential": "google_jwt_token",
  "user_info": { "email": "user@example.com", ... }
}

# Get user profile
GET /api/accounts/me/
Authorization: Token your_auth_token
```

### Image Processing
```bash
# Generate face swap
POST /api/imagegen/generate/
Authorization: Token your_auth_token
Content-Type: multipart/form-data
selfie: [image_file]

# Random transformation
POST /api/imagegen/randomize/
Authorization: Token your_auth_token  
Content-Type: multipart/form-data
selfie: [image_file]

# Check processing status
GET /api/imagegen/status/{job_id}/
Authorization: Token your_auth_token
```

### Response Format
```json
{
  "id": 123,
  "match_name": "Napoleon Bonaparte",
  "match_score": 0.87,
  "message": "Successfully transformed you into Napoleon Bonaparte!",
  "output_image_url": "https://cloudinary.com/...",
  "original_selfie_url": "https://cloudinary.com/...",
  "historical_figure_url": "https://cloudinary.com/...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## 🚀 Deployment

### Backend (Fly.io)
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly deploy

# Set environment variables
fly secrets set DJANGO_SECRET_KEY=your-secret
fly secrets set DATABASE_URL=your-db-url
fly secrets set CLOUDINARY_URL=your-cloudinary-url
```

### Frontend (Netlify)
```bash
# Build for production
npm run build

# Deploy to Netlify (via CLI or drag-and-drop)
npx netlify deploy --prod --dir=dist
```

## 🧪 Development

### Running Tests
```bash
# Backend tests
python manage.py test

# Frontend tests  
npm run test

# End-to-end tests
npm run test:e2e
```

### Code Quality
```bash
# Backend formatting
black .
isort .
flake8 .

# Frontend formatting
npm run lint
npm run format
```

### Database Migrations
```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush
```

## 📊 Monitoring & Logging

### Application Logs
```bash
# View Django logs
docker-compose logs backend

# View Celery worker logs
docker-compose logs celery_worker

# View frontend logs
docker-compose logs frontend
```

### Performance Monitoring
- Backend: Django Debug Toolbar (development)
- Frontend: Vite bundle analyzer
- Database: PostgreSQL query logging
- Celery: Flower monitoring (planned)

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`  
5. **Open Pull Request**

### Development Guidelines
- Follow existing code style (use Black/Prettier)
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **HuggingFace** - AI model hosting and inference
- **Cloudinary** - Image storage and optimization
- **Historical Figure Images** - Various public domain sources
- **Open Source Libraries** - All the amazing tools that make this possible

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/historyface/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/historyface/wiki)
- **Email**: support@historyface.com

## 🗺️ Roadmap

- [ ] **Enhanced AI Models**: More accurate face matching
- [ ] **Historical Figure Expansion**: Add more personalities 
- [ ] **Video Processing**: Transform videos, not just images
- [ ] **Mobile App**: Native iOS/Android applications
- [ ] **Social Features**: Share galleries, user profiles
- [ ] **API Rate Limiting**: Advanced usage controls
- [ ] **Analytics Dashboard**: Processing statistics
- [ ] **Multi-language Support**: Internationalization

---

**Built with ❤️ using Django, React, and AI**

Transform into history. Discover your past. Share your story.