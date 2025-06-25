# 🔄 AI Face Swap App

A modern, full-stack AI face swap application that allows users to upload photos and generate AI-powered face swaps using advanced machine learning models.

## 🌟 Features

- **🤖 AI Face Swap**: Advanced face swapping using Hugging Face Spaces
- **📱 Modern UI**: Responsive React frontend with Tailwind CSS
- **🔐 Authentication**: User accounts with Google OAuth integration
- **💳 Payments**: Stripe integration for premium features
- **☁️ Cloud Storage**: Cloudinary for image hosting and optimization
- **📊 Real-time Status**: Live updates on processing status
- **🚀 Auto-scaling**: Serverless architecture with automatic scaling

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
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Lucide React** for icons

### Backend
- **Django 5.1** with Python 3.10+
- **Django REST Framework** for API
- **PostgreSQL** database
- **Cloudinary** for media storage
- **Stripe** for payments
- **Allauth** for authentication

### AI/ML
- **Hugging Face Spaces** for face swap models
- **Gradio Client** for API integration
- **Face Recognition** libraries

### Deployment
- **Frontend**: Netlify
- **Backend**: Fly.io
- **Database**: Fly.io PostgreSQL
- **Storage**: Cloudinary CDN

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-face-swap-app
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Configure environment variables (see below)
python manage.py migrate
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Configure environment variables
npm run dev
```

### 4. Docker Development (Alternative)
```bash
docker-compose up --build
```

## 🔧 Environment Variables

### Backend (.env)
```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Cloudinary
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Hugging Face
HUGGINGFACE_SPACE_NAME=your-username/space-name
HUGGINGFACE_API_TOKEN=hf_...

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Frontend (.env.local)
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_API_TOKEN=your-api-token
```

## 📡 API Endpoints

### Authentication
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login
- `POST /api/accounts/logout/` - User logout

### Face Swap
- `POST /api/imagegen/generate/` - Generate face swap
- `GET /api/imagegen/status/{id}/` - Check processing status
- `GET /api/imagegen/list/` - List user's generations

### Health Check
- `GET /health/` - Backend health status

## 🚀 Deployment

### Frontend (Netlify)
1. Connect your GitHub repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Configure environment variables in Netlify dashboard
5. Deploy!

### Backend (Fly.io)
```bash
# Install Fly CLI
fly auth login

# Initialize Fly app
fly launch

# Set environment variables
fly secrets set DJANGO_SECRET_KEY=your-secret-key
fly secrets set DATABASE_URL=your-db-url
# ... set all other secrets

# Deploy
fly deploy
```

### Database (Fly.io PostgreSQL)
```bash
# Create database
fly postgres create --name ai-face-swap-db

# Connect to your app
fly postgres attach --app your-app-name ai-face-swap-db
```

## 🔧 Development

### Running Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm run test
```

### Code Formatting
```bash
# Backend (Black + isort)
cd backend
black .
isort .

# Frontend (Prettier)
cd frontend
npm run format
```

### Database Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## 🐛 Troubleshooting

### Common Issues

#### CORS Errors
- Ensure frontend URL is in `CORS_ALLOWED_ORIGINS` in Django settings
- Check that `corsheaders` middleware is first in `MIDDLEWARE` list

#### Hugging Face Space Errors
- Verify `HUGGINGFACE_API_TOKEN` is set correctly
- Check space name format: `username/space-name` (not full URL)
- Restart the Hugging Face Space if needed (cold start issue)

#### Fly.io Auto-sleep
- Apps auto-scale to zero after inactivity (cost optimization)
- First request after sleep will have ~5-10 second cold start delay
- Consider upgrading to prevent auto-sleep for production

#### Image Upload Issues
- Check Cloudinary configuration and quota
- Verify file size limits (default: 10MB)
- Ensure proper CORS headers for file uploads

### Logs
```bash
# Frontend (browser console)
Open Developer Tools → Console

# Backend local
Check terminal output

# Backend production (Fly.io)
fly logs --app your-app-name

# Hugging Face Spaces
Check space logs in HF interface
```

## 🔐 Security Notes

- Never commit `.env` files to version control
- Use strong, unique secret keys for production
- Enable HTTPS in production (handled by Netlify/Fly.io)
- Regularly rotate API tokens and secrets
- Set `CORS_ALLOW_ALL_ORIGINS = False` in production

## 📄 License

[Add your license here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- 📧 Email: [your-email]
- 🐛 Issues: [GitHub Issues URL]
- 📖 Documentation: [Docs URL]

---

Built with ❤️ using modern web technologies