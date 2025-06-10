#!/bin/bash

# EETL AI Platform Setup Script
# This script sets up the development environment for the EETL AI Platform

set -e

echo "🚀 Setting up EETL AI Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "macOS detected"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "Windows detected"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker found"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose found"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    print_success "Git found"
    
    # Check Node.js (optional, for local development)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_warning "Node.js not found. Install Node.js 18+ for local frontend development."
    fi
    
    # Check Python (optional, for local development)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_warning "Python3 not found. Install Python 3.11+ for local backend development."
    fi
}

# Create environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "change-me-in-production")
        
        # Update .env file with generated secret key
        if [[ "$OS" == "macos" ]]; then
            sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
        else
            sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
        fi
        
        print_warning "Please update the .env file with your OpenRouter API key and other settings"
        print_warning "Required: OPENROUTER_API_KEY=your-api-key"
    else
        print_success ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "logs"
        "uploads"
        "media"
        "staticfiles"
        "chroma_db"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Setup Git hooks (optional)
setup_git_hooks() {
    print_status "Setting up Git hooks..."
    
    if [ -d ".git" ]; then
        # Pre-commit hook for code formatting
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for EETL AI Platform

echo "Running pre-commit checks..."

# Check if backend files changed
if git diff --cached --name-only | grep -q "backend/"; then
    echo "Backend files changed, running Python checks..."
    cd backend
    
    # Run black formatter (if available)
    if command -v black &> /dev/null; then
        black --check . || {
            echo "Code formatting issues found. Run 'black .' to fix."
            exit 1
        }
    fi
    
    # Run flake8 linter (if available)
    if command -v flake8 &> /dev/null; then
        flake8 . || {
            echo "Linting issues found. Please fix before committing."
            exit 1
        }
    fi
    
    cd ..
fi

# Check if frontend files changed
if git diff --cached --name-only | grep -q "frontend/"; then
    echo "Frontend files changed, running TypeScript checks..."
    cd frontend
    
    # Run ESLint (if available)
    if [ -f "node_modules/.bin/eslint" ]; then
        npm run lint || {
            echo "ESLint issues found. Please fix before committing."
            exit 1
        }
    fi
    
    cd ..
fi

echo "Pre-commit checks passed!"
EOF
        
        chmod +x .git/hooks/pre-commit
        print_success "Git pre-commit hook installed"
    else
        print_warning "Not a Git repository, skipping Git hooks setup"
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Pull latest images
    docker-compose pull
    
    # Build custom images
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    print_success "Services started successfully!"
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_services_health
}

# Check if services are running properly
check_services_health() {
    print_status "Checking service health..."
    
    # Check PostgreSQL
    if docker-compose exec -T postgres pg_isready -U eetl_user -d eetl_db &> /dev/null; then
        print_success "PostgreSQL is ready"
    else
        print_error "PostgreSQL is not ready"
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        print_success "Redis is ready"
    else
        print_error "Redis is not ready"
    fi
    
    # Check Backend
    if curl -f http://localhost:8000/api/health/ &> /dev/null; then
        print_success "Backend API is ready"
    else
        print_warning "Backend API is not ready yet (this is normal on first startup)"
    fi
    
    # Check Frontend
    if curl -f http://localhost:3000/health &> /dev/null; then
        print_success "Frontend is ready"
    else
        print_warning "Frontend is not ready yet (this is normal on first startup)"
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait for backend to be ready
    sleep 5
    
    # Run migrations
    docker-compose exec backend python manage.py migrate
    
    print_success "Database migrations completed"
}

# Create superuser (optional)
create_superuser() {
    print_status "Creating Django superuser..."
    
    read -p "Do you want to create a Django superuser? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec backend python manage.py createsuperuser
        print_success "Superuser created"
    else
        print_status "Skipping superuser creation"
    fi
}

# Display final information
show_completion_info() {
    print_success "🎉 EETL AI Platform setup completed!"
    
    echo
    echo "📋 Service URLs:"
    echo "  Frontend:        http://localhost:3000"
    echo "  Backend API:     http://localhost:8000"
    echo "  API Docs:        http://localhost:8000/api/docs/"
    echo "  Admin Panel:     http://localhost:8000/admin/"
    echo
    echo "🔧 Useful Commands:"
    echo "  View logs:       docker-compose logs -f"
    echo "  Stop services:   docker-compose down"
    echo "  Restart:         docker-compose restart"
    echo "  Shell access:    docker-compose exec backend bash"
    echo
    echo "📚 Next Steps:"
    echo "  1. Update .env file with your OpenRouter API key"
    echo "  2. Visit http://localhost:3000 to access the application"
    echo "  3. Check the documentation in the docs/ folder"
    echo "  4. Explore the Hugging Face demos in huggingface_demos/"
    echo
    print_warning "Remember to update your .env file with the correct API keys and settings!"
}

# Main execution
main() {
    echo "🤖 EETL AI Platform Setup Script"
    echo "================================="
    echo
    
    check_os
    check_dependencies
    setup_environment
    create_directories
    setup_git_hooks
    start_services
    run_migrations
    create_superuser
    show_completion_info
}

# Run main function
main "$@"
