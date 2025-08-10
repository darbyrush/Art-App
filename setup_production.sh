#!/bin/bash

# Production Setup Script for Art Explorer
# This script helps set up the production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log "Setting up production environment for Art Explorer..."

# Check if .env.production exists
if [[ ! -f ".env.production" ]]; then
    log "Creating .env.production from template..."
    cp PRODUCTION_ENV_TEMPLATE.txt .env.production
    success "Created .env.production from template"
    warning "Please edit .env.production with your actual production values"
else
    success ".env.production already exists"
fi

# Generate a secure SECRET_KEY if not already set
if ! grep -q "your_32_character_secret_key_here" .env.production; then
    success "SECRET_KEY appears to be configured"
else
    log "Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s/your_32_character_secret_key_here_change_this_in_production/$SECRET_KEY/" .env.production
    success "Generated and set SECRET_KEY"
fi

# Set proper file permissions
log "Setting secure file permissions..."
chmod 600 .env.production
success "Set .env.production permissions to 600"

# Check Docker installation
log "Checking Docker installation..."
if command -v docker &> /dev/null; then
    success "Docker is installed"
else
    error "Docker is not installed. Please install Docker first."
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    success "Docker Compose is installed"
else
    error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if SSL certificates exist
log "Checking SSL certificates..."
if [[ -d "docker/ssl" ]] && [[ -f "docker/ssl/myassemblage.art.crt" ]] && [[ -f "docker/ssl/myassemblage.art.key" ]]; then
    success "SSL certificates found"
else
    warning "SSL certificates not found in docker/ssl/"
    warning "You'll need to obtain SSL certificates for your domain"
    warning "Place them in docker/ssl/ with names:"
    warning "  - myassemblage.art.crt"
    warning "  - myassemblage.art.key"
fi

# Create necessary directories
log "Creating necessary directories..."
mkdir -p docker/ssl
mkdir -p uploads/profile_pictures
mkdir -p logs
mkdir -p backups
success "Created necessary directories"

# Check database configuration
log "Checking database configuration..."
if grep -q "your_secure_password_here" .env.production; then
    warning "Database password not configured in .env.production"
    warning "Please set POSTGRES_PASSWORD and DATABASE_URL"
else
    success "Database configuration appears to be set"
fi

# Check API keys
log "Checking API keys..."
MISSING_KEYS=()
if grep -q "your_smithsonian_api_key" .env.production; then
    MISSING_KEYS+=("SMITHSONIAN_API_KEY")
fi
if grep -q "your_met_api_key" .env.production; then
    MISSING_KEYS+=("MET_API_KEY")
fi
if grep -q "your_harvard_api_key" .env.production; then
    MISSING_KEYS+=("HARVARD_API_KEY")
fi

if [[ ${#MISSING_KEYS[@]} -gt 0 ]]; then
    warning "Missing API keys: ${MISSING_KEYS[*]}"
    warning "These are required for the art fetching functionality"
else
    success "All API keys appear to be configured"
fi

# Show next steps
echo ""
echo -e "${GREEN}Production environment setup completed!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env.production with your actual values:"
echo "   - Database credentials"
echo "   - API keys for art services"
echo "   - Domain names"
echo "   - SSL certificate paths"
echo ""
echo "2. Obtain SSL certificates for your domain"
echo "3. Run: ./deploy_production.sh"
echo ""
echo -e "${YELLOW}Important security notes:${NC}"
echo "- Keep .env.production secure and never commit it to git"
echo "- Use strong, unique passwords for all services"
echo "- Regularly update dependencies and monitor security"
echo ""
echo -e "${GREEN}Your Art Explorer app is ready for production deployment!${NC}"
