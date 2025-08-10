#!/bin/bash

# Production Deployment Script for Art Explorer
# This script handles the complete production deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="art-explorer"
ENV_FILE=".env.production"
DOCKER_COMPOSE_FILE="docker/docker-compose.prod.yml"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check if .env.production exists
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Production environment file $ENV_FILE not found"
    fi
    
    success "Prerequisites check passed"
}

# Validate environment variables
validate_environment() {
    log "Validating environment variables..."
    
    # Source environment file
    source "$ENV_FILE"
    
    # Check required variables
    required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "ENVIRONMENT"
        "CORS_ORIGINS"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            error "Required environment variable $var is not set"
        fi
    done
    
    # Validate SECRET_KEY length
    if [[ ${#SECRET_KEY} -lt 32 ]]; then
        error "SECRET_KEY must be at least 32 characters long"
    fi
    
    # Validate ENVIRONMENT
    if [[ "$ENVIRONMENT" != "production" ]]; then
        error "ENVIRONMENT must be set to 'production'"
    fi
    
    success "Environment validation passed"
}

# Security checks
security_checks() {
    log "Running security checks..."
    
    # Check for hardcoded secrets
    if grep -r "password\|secret\|key" . --exclude-dir=venv --exclude-dir=node_modules --exclude="*.pyc" --exclude="*.log" | grep -v "your_" | grep -v "example" | grep -v "template"; then
        warning "Potential hardcoded secrets found. Please review the output above."
    fi
    
    # Check file permissions
    if [[ -f "$ENV_FILE" ]]; then
        perms=$(stat -c "%a" "$ENV_FILE")
        if [[ "$perms" != "600" ]]; then
            warning "Environment file permissions should be 600, current: $perms"
            chmod 600 "$ENV_FILE"
        fi
    fi
    
    success "Security checks completed"
}

# Build and deploy
deploy() {
    log "Starting deployment..."
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    
    # Clean up old images
    log "Cleaning up old images..."
    docker system prune -f
    
    # Build images
    log "Building Docker images..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_health
    
    success "Deployment completed successfully"
}

# Health check
check_health() {
    log "Checking service health..."
    
    # Check backend health
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        success "Backend is healthy"
    else
        error "Backend health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost:3000/ > /dev/null 2>&1; then
        success "Frontend is healthy"
    else
        error "Frontend health check failed"
    fi
    
    # Check database connection
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T backend python -c "
from database.config import test_connection
exit(0 if test_connection() else 1)
" > /dev/null 2>&1; then
        success "Database connection is healthy"
    else
        error "Database connection check failed"
    fi
}

# Backup database
backup_database() {
    log "Creating database backup..."
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backup_${PROJECT_NAME}_${timestamp}.sql"
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$backup_file"; then
        success "Database backup created: $backup_file"
    else
        warning "Database backup failed"
    fi
}

# Show deployment status
show_status() {
    log "Deployment status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    log "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8001"
    echo "  Nginx: http://localhost:80"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001"
}

# Main execution
main() {
    log "Starting production deployment for $PROJECT_NAME"
    
    check_root
    check_prerequisites
    validate_environment
    security_checks
    
    # Ask for confirmation
    echo ""
    echo -e "${YELLOW}Are you sure you want to deploy to production? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log "Deployment cancelled by user"
        exit 0
    fi
    
    # Create backup
    backup_database
    
    # Deploy
    deploy
    
    # Show status
    show_status
    
    success "Production deployment completed successfully!"
}

# Run main function
main "$@"
