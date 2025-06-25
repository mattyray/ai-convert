# 🔄 AI Face Swap App

A modern, full-stack AI face swap application that allows users to upload photos and generate AI-powered face swaps using advanced machine learning models.

**🔗 Repository:** https://github.com/mattyray/ai-convert

## 🌟 Features

- **🤖 AI Face Swap**: Advanced face swapping using Hugging Face Spaces
- **📱 Modern UI**: Responsive React frontend with Tailwind CSS
- **🔐 Authentication**: User accounts with Google OAuth integration
- **💳 Payments**: Stripe integration for premium features
- **☁️ Cloud Storage**: Cloudinary for image hosting and optimization
- **📊 Real-time Status**: Live updates on processing status
- **🚀 Auto-scaling**: Serverless architecture with automatic scaling
- **🐳 Containerized**: Full Docker development environment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  AI Processing  │
│                 │    │                 │    │                 │
│  React + Vite   │◄──►│     Django      │◄──►│ Hugging Face    │
│   (Netlify)     │    │    (Fly.io)     │    │    Spaces       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloudinary    │    │   PostgreSQL    │    │   Gradio API    │
│ (Image Storage) │    │   (Database)    │    │ (ML Pipeline)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling and HMR
- **Tailwind CSS** for utility-first styling
- **Axios** for HTTP client with interceptors
- **Lucide React** for consistent iconography

### Backend
- **Django 5.1** with Python 3.10+
- **Django REST Framework** for API endpoints
- **PostgreSQL** for relational data storage
- **Cloudinary** for media CDN and transformations
- **Stripe** for payment processing
- **Django Allauth** for social authentication

### AI/ML Pipeline
- **Hugging Face Spaces** for model hosting
- **Gradio Client** for API communication
- **Face Recognition** libraries (dlib + face_recognition)
- **OpenCV** for image preprocessing

### Infrastructure
- **Frontend**: Netlify (CDN + Static hosting)
- **Backend**: Fly.io (Auto-scaling containers)
- **Database**: Fly.io PostgreSQL (Managed database)
- **Storage**: Cloudinary CDN
- **Containerization**: Docker + Docker Compose

## 🚀 Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose
- Git
- Node.js 18+ (for local frontend development)

### 1. Clone Repository
```bash
git clone https://github.com/mattyray/ai-convert.git
cd ai-convert
```

### 2. Environment Setup
```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Configure your environment variables (see Environment Variables section)
```

### 3. Docker Development
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. Initialize Database
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser (optional)
docker-compose exec backend python manage.py createsuperuser
```

### 5. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8002
- **Admin Panel**: http://localhost:8002/admin

## 🔧 Environment Variables

### Backend (.env)
```bash
# Django Core
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web

# Database
DATABASE_URL=postgres://user:password@db:5432/ai_face_swap

# Cloudinary (Image Storage)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Stripe Payment Processing
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Hugging Face AI Models
HUGGINGFACE_SPACE_NAME=mnraynor90/facefusionfastapi-private
HUGGINGFACE_API_TOKEN=hf_...

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Frontend (.env.local)
```bash
VITE_API_BASE_URL=http://127.0.0.1:8002
VITE_API_TOKEN=your-api-token
```

## 🏢 Django Apps Architecture

Our Django backend is organized into focused, single-responsibility apps:

### 📁 **accounts** (`accounts/`)
**Purpose**: User management and authentication
- **Models**: `CustomUser` with email-based authentication
- **Features**: User registration, login, profile management
- **Integration**: Works with Django Allauth for social login

### 💬 **chat** (`chat/`)
**Purpose**: User interaction and messaging
- **Models**: Chat sessions, messages, conversation history
- **Features**: Real-time communication, chat history
- **Use Case**: User support and interaction logging

### 🔄 **faceswap** (`faceswap/`)
**Purpose**: Face swap job management and tracking
- **Models**: `FaceSwapJob` for tracking AI processing
- **Features**: Job creation, status tracking, result management
- **Integration**: Interfaces with Hugging Face Spaces API

### 🖼️ **imagegen** (`imagegen/`)
**Purpose**: Core image generation and processing
- **Models**: `GeneratedImage`, processing metadata
- **Features**: Image upload, AI processing pipeline, result storage
- **Integration**: Cloudinary for storage, HuggingFace for AI

### 🔧 **django_project** (`django_project/`)
**Purpose**: Main project configuration
- **Files**: `settings.py`, `urls.py`, `wsgi.py`
- **Features**: Global configuration, URL routing, WSGI application

## 📋 Third-Party Libraries Explained

### **Core Django Extensions**
```python
# Authentication & Social Login
'allauth',                    # Social authentication framework
'allauth.account',           # Account management
'allauth.socialaccount',     # Social providers (Google)
'allauth.socialaccount.providers.google',  # Google OAuth

# API Framework
'rest_framework',            # RESTful API development
'rest_framework.authtoken',  # Token-based authentication

# CORS & Security
'corsheaders',              # Cross-Origin Resource Sharing
```

### **Media & Storage**
```python
# Cloudinary Integration
'cloudinary_storage',       # Django storage backend for Cloudinary
'cloudinary',              # Cloudinary Python SDK for image processing
```

### **Why Each Library?**

- **📱 Django Allauth**: Handles complex authentication flows, social login, email verification
- **🔌 DRF**: Provides serializers, viewsets, authentication for clean API development  
- **🌐 CORS Headers**: Enables frontend-backend communication across different domains
- **☁️ Cloudinary**: CDN + image transformations + automatic optimization
- **🔐 REST Framework**: Token authentication, pagination, filtering for APIs

## 🤖 Face Recognition Pipeline

### **How It Works**

1. **📸 Image Upload**
   ```python
   # Frontend uploads to Django
   POST /api/imagegen/generate/
   Content-Type: multipart/form-data
   ```

2. **🔍 Face Detection**
   ```python
   import face_recognition
   
   # Detect faces in uploaded image
   face_locations = face_recognition.face_locations(image)
   face_encodings = face_recognition.face_encodings(image, face_locations)
   ```

3. **🚀 AI Processing**
   ```python
   from gradio_client import Client
   
   # Connect to Hugging Face Space
   client = Client(HUGGINGFACE_SPACE_NAME, hf_token=HUGGINGFACE_API_TOKEN)
   
   # Submit face swap job
   result = client.predict(
       source_image=source_file,
       target_image=target_file
   )
   ```

4. **📊 Status Tracking**
   ```python
   # Real-time status updates
   job = FaceSwapJob.objects.create(
       user=request.user,
       status='processing',
       prediction_id=result.job_id
   )
   ```

5. **💾 Result Storage**
   ```python
   # Store result in Cloudinary
   cloudinary.uploader.upload(
       result_image,
       public_id=f"faceswap/{job.id}",
       transformation={'quality': 'auto', 'fetch_format': 'auto'}
   )
   ```

### **AI Models Used**
- **Face Fusion**: Advanced face swapping with high fidelity
- **Face Detection**: dlib's HOG + CNN face detection
- **Face Alignment**: 68-point facial landmark detection
- **Style Transfer**: Neural style transfer for seamless blending

## 📡 API Endpoints

### Authentication
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login  
- `POST /api/accounts/logout/` - User logout
- `GET /api/accounts/profile/` - User profile

### Face Swap
- `POST /api/imagegen/generate/` - Generate face swap
- `GET /api/imagegen/status/{id}/` - Check processing status
- `GET /api/imagegen/list/` - List user's generations
- `POST /api/imagegen/unlock/` - Unlock premium generation

### Health & Debug
- `GET /health/` - Backend health status
- `GET /api/faceswap/debug/` - Debug Gradio connection
- `GET /api/faceswap/test-gradio/` - Test HF Space connectivity

## 🚀 Deployment

### Frontend (Netlify)

#### **1. Netlify Configuration**
Create `netlify.toml` in project root:
```toml
[build]
  publish = "frontend/dist"
  command = "cd frontend && npm ci && npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.processing]
  skip_processing = false

[build.processing.css]
  bundle = true
  minify = true

[build.processing.js]
  bundle = true
  minify = true
```

#### **2. Deployment Steps**
1. **Connect Repository**: Link GitHub repo to Netlify
2. **Build Settings**:
   - Build command: `cd frontend && npm ci && npm run build`
   - Publish directory: `frontend/dist`
   - Node version: `18`
3. **Environment Variables**: Set in Netlify dashboard
4. **Deploy**: Automatic on git push to main

### Backend (Fly.io)

#### **1. Fly.io Configuration (`fly.toml`)**
```toml
app = "ai-face-swap-app"
primary_region = "ewr"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  DJANGO_SETTINGS_MODULE = "django_project.settings"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health/"

[processes]
  app = "gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 300 django_project.wsgi:application"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

#### **2. Understanding fly.toml**

- **🏗️ `[build]`**: Specifies Dockerfile for containerization
- **🌍 `[env]`**: Environment variables available to all processes
- **🌐 `[http_service]`**: HTTP routing and health checks
  - `auto_stop_machines`: Enables auto-scaling to zero (cost optimization)
  - `auto_start_machines`: Automatic wake-up on requests (cold starts)
  - `min_machines_running = 0`: Allows complete hibernation
- **⚡ `[processes]`**: Defines how to run the application (Gunicorn WSGI server)
- **💻 `[[vm]]`**: Virtual machine specifications (CPU, memory)

#### **3. Deployment Steps**
```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Create app (if first time)
fly launch

# 4. Set secrets
fly secrets set DJANGO_SECRET_KEY=your-secret-key
fly secrets set DATABASE_URL=your-postgres-url
fly secrets set CLOUDINARY_URL=your-cloudinary-url
fly secrets set HUGGINGFACE_API_TOKEN=your-hf-token
# ... set all other secrets

# 5. Deploy
fly deploy

# 6. Check status
fly status
fly logs
```

#### **4. Auto-Scaling Behavior**
- **💤 Hibernation**: App sleeps after ~5 minutes of inactivity
- **⚡ Cold Start**: ~5-10 second wake-up time on first request
- **💰 Cost Optimization**: Only pay when actively processing requests
- **📈 Auto-scaling**: Scales up/down based on traffic automatically

### Database (Fly.io PostgreSQL)
```bash
# Create managed PostgreSQL
fly postgres create --name ai-face-swap-db --region ewr

# Attach to your app
fly postgres attach --app ai-face-swap-app ai-face-swap-db

# This automatically sets DATABASE_URL secret
```

## 🔧 Development Workflow

### **Local Development**
```bash
# Start all services
docker-compose up

# Backend only
docker-compose up backend db

# Frontend only (for faster iteration)
cd frontend && npm run dev

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# View logs
docker-compose logs -f backend
```

### **Testing**
```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests  
cd frontend && npm run test

# API testing
curl -X GET http://localhost:8002/health/
```

### **Database Management**
```bash
# Connect to database
docker-compose exec db psql -U postgres -d ai_face_swap

# Backup database
docker-compose exec db pg_dump -U postgres ai_face_swap > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U postgres -d ai_face_swap
```

## 🐛 Troubleshooting

### **Auto-Scaling Issues**
- **Cold Start Delays**: First request after hibernation takes 5-10 seconds
- **Solution**: Consider upgrading Fly.io plan to prevent auto-sleep for production

### **Hugging Face Space Issues**
- **Space Sleeping**: HF Spaces also auto-sleep to save compute costs
- **Solution**: Make a test request to wake up the space: `GET /api/faceswap/test-gradio/`

### **CORS Issues**
- **Symptoms**: Browser blocks requests with CORS policy errors
- **Check**: Ensure frontend domain is in `CORS_ALLOWED_ORIGINS`
- **Debug**: Temporarily set `CORS_ALLOW_ALL_ORIGINS = True` for testing

### **Docker Issues**
```bash
# Rebuild containers
docker-compose down && docker-compose up --build

# Clear volumes
docker-compose down -v

# View container logs
docker-compose logs backend
docker-compose logs frontend
```

### **Image Processing Failures**
- **Check**: Cloudinary quotas and API limits
- **Verify**: Hugging Face Space is running and accessible
- **Debug**: Use `/api/faceswap/debug/` endpoint for diagnostics

## 🔐 Security Best Practices

- **🔑 Secrets Management**: Use environment variables, never commit secrets
- **🌐 CORS**: Set specific origins in production (`CORS_ALLOW_ALL_ORIGINS = False`)
- **🔒 HTTPS**: Enforced by Netlify and Fly.io automatically
- **🛡️ CSRF Protection**: Enabled by default in Django
- **📝 Input Validation**: DRF serializers handle API input validation
- **🏗️ SQL Injection**: Django ORM protects against SQL injection
- **📊 Rate Limiting**: Consider adding rate limiting for API endpoints

## 📄 License

[Specify your license]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- 🐛 **Issues**: https://github.com/mattyray/ai-convert/issues
- 📧 **Email**: [mnraynor90@gmail.com]
- 📖 **Documentation**: [in ma head]

---

Built with ❤️ using modern web technologies and AI. Don't hate ma hands dont work