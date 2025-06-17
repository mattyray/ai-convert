#!/bin/bash
# Docker commands for AI Face Swap project

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 AI Face Swap Docker Commands${NC}"
echo "=================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
}

# Function to create .env file if it doesn't exist
create_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}📝 Creating .env file...${NC}"
        cat << EOF > .env
# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key-change-this-in-production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database
DATABASE_URL=postgresql://postgres:postgres_password@db:5432/faceswap_db

# Cloudinary (get from cloudinary.com)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Hugging Face
HUGGINGFACE_FACESWAP_URL=https://mnraynor90-facefusionfastapi.hf.space

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF
        echo -e "${GREEN}✅ .env file created. Please edit it with your actual API keys.${NC}"
    fi
}

# Development commands
dev_build() {
    echo -e "${BLUE}🔨 Building development containers...${NC}"
    docker-compose build
}

dev_up() {
    echo -e "${BLUE}🚀 Starting development environment...${NC}"
    docker-compose up -d db redis
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
    sleep 10
    docker-compose up backend frontend
}

dev_logs() {
    echo -e "${BLUE}📋 Showing logs...${NC}"
    docker-compose logs -f
}

dev_shell() {
    echo -e "${BLUE}🐚 Opening Django shell...${NC}"
    docker-compose exec backend python manage.py shell
}

dev_migrate() {
    echo -e "${BLUE}🗃️  Running migrations...${NC}"
    docker-compose exec backend python manage.py migrate
}

dev_superuser() {
    echo -e "${BLUE}👤 Creating superuser...${NC}"
    docker-compose exec backend python manage.py createsuperuser
}

dev_test() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    docker-compose exec backend python manage.py test
}

# Production commands
prod_build() {
    echo -e "${BLUE}🔨 Building production containers...${NC}"
    docker-compose -f docker-compose.yml build
}

prod_up() {
    echo -e "${BLUE}🚀 Starting production environment...${NC}"
    docker-compose --profile production up -d
}

# Utility commands
clean() {
    echo -e "${YELLOW}🧹 Cleaning up containers and volumes...${NC}"
    docker-compose down -v
    docker system prune -f
}

reset() {
    echo -e "${RED}⚠️  Resetting everything (this will delete all data!)${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker volume prune -f
        echo -e "${GREEN}✅ Reset complete${NC}"
    fi
}

status() {
    echo -e "${BLUE}📊 Container status:${NC}"
    docker-compose ps
    echo
    echo -e "${BLUE}📊 Volume usage:${NC}"
    docker volume ls | grep faceswap
}

# Main command handler
case "$1" in
    "build")
        check_docker
        create_env
        dev_build
        ;;
    "up"|"start")
        check_docker
        create_env
        dev_up
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "shell")
        dev_shell
        ;;
    "migrate")
        dev_migrate
        ;;
    "superuser")
        dev_superuser
        ;;
    "test")
        dev_test
        ;;
    "prod-build")
        check_docker
        create_env
        prod_build
        ;;
    "prod-up")
        check_docker
        create_env
        prod_up
        ;;
    "clean")
        clean
        ;;
    "reset")
        reset
        ;;
    "status")
        status
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Stopping containers...${NC}"
        docker-compose down
        ;;
    *)
        echo -e "${GREEN}Available commands:${NC}"
        echo "  build      - Build development containers"
        echo "  up/start   - Start development environment"
        echo "  logs       - Show container logs"
        echo "  shell      - Open Django shell"
        echo "  migrate    - Run database migrations"
        echo "  superuser  - Create Django superuser"
        echo "  test       - Run tests"
        echo "  prod-build - Build production containers"
        echo "  prod-up    - Start production environment"
        echo "  clean      - Clean up containers and images"
        echo "  reset      - Reset everything (deletes data!)"
        echo "  status     - Show container and volume status"
        echo "  stop       - Stop all containers"
        echo ""
        echo -e "${BLUE}Example usage:${NC}"
        echo "  ./docker.sh build"
        echo "  ./docker.sh up"
        echo "  ./docker.sh logs"
        ;;
esac