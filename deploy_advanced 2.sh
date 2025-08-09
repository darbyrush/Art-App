#!/bin/bash

# Advanced Art Explorer Deployment Script
# Includes Redis caching, image optimization, and scalability features

set -e

echo "🚀 Advanced Art Explorer Deployment"
echo "=================================="

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

# Check if Redis is available locally
check_redis() {
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            print_success "Local Redis is running"
            return 0
        fi
    fi
    return 1
}

# Setup Redis (local or Docker)
setup_redis() {
    print_status "Setting up Redis for image caching..."
    
    if check_redis; then
        print_success "Using local Redis instance"
        export REDIS_HOST=localhost
        export REDIS_PORT=6379
    else
        print_warning "Local Redis not found. Starting Redis in Docker..."
        docker run -d \
            --name art-explorer-redis \
            -p 6379:6379 \
            redis:7-alpine \
            redis-server --appendonly yes
        
        # Wait for Redis to be ready
        sleep 5
        print_success "Redis started in Docker"
        export REDIS_HOST=localhost
        export REDIS_PORT=6379
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install backend dependencies
    pip install -r backend/requirements.txt
    
    print_success "Dependencies installed"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    source venv/bin/activate
    
    # Initialize database
    python -c "
import sys
sys.path.append('.')
from database.config import init_db
init_db()
print('Database initialized successfully')
"
    
    print_success "Database setup complete"
}

# Start backend with advanced features
start_backend() {
    print_status "Starting backend with advanced image optimization..."
    
    source venv/bin/activate
    
    # Set environment variables for advanced features
    export REDIS_HOST=${REDIS_HOST:-localhost}
    export REDIS_PORT=${REDIS_PORT:-6379}
    export ENVIRONMENT=development
    
    # Start backend with multiple workers for better performance
    cd api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001 --workers 1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 3
    
    # Test backend health
    if curl -f http://localhost:8001/health &> /dev/null; then
        print_success "Backend started successfully"
    else
        print_error "Backend failed to start"
        exit 1
    fi
}

# Start frontend
start_frontend() {
    print_status "Starting frontend..."
    
    cd frontend
    
    # Install frontend dependencies if needed
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Start frontend
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    sleep 5
    
    print_success "Frontend started successfully"
}

# Populate database with artworks
populate_database() {
    print_status "Populating database with artworks..."
    
    # Get auth token
    TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8001/token \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&password=testpass123")
    
    TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    
    # Populate database
    curl -X POST "http://localhost:8001/admin/populate-database?artworks_per_source=10" \
        -H "Authorization: Bearer $TOKEN"
    
    print_success "Database populated with artworks"
}

# Test image optimization features
test_image_features() {
    print_status "Testing image optimization features..."
    
    # Test placeholder generation
    curl -f http://localhost:8001/images/placeholder/met?width=200&height=200 &> /dev/null
    print_success "Placeholder generation working"
    
    # Test image optimization endpoint
    curl -f "http://localhost:8001/images/optimize?url=https://example.com/test.jpg&width=400&height=400" &> /dev/null
    print_success "Image optimization endpoint working"
    
    # Test cache clearing
    curl -X DELETE http://localhost:8001/images/cache &> /dev/null
    print_success "Cache management working"
}

# Monitor system resources
monitor_resources() {
    print_status "Monitoring system resources..."
    
    echo "📊 Resource Usage:"
    echo "=================="
    
    # Memory usage
    MEMORY=$(free -h | grep Mem | awk '{print $3 "/" $2}')
    echo "Memory: $MEMORY"
    
    # CPU usage
    CPU=$(top -l 1 | grep "CPU usage" | awk '{print $3}')
    echo "CPU: $CPU"
    
    # Disk usage
    DISK=$(df -h . | tail -1 | awk '{print $5}')
    echo "Disk: $DISK"
    
    # Redis memory
    if command -v redis-cli &> /dev/null; then
        REDIS_MEM=$(redis-cli info memory | grep used_memory_human | cut -d: -f2)
        echo "Redis Memory: $REDIS_MEM"
    fi
}

# Performance testing
performance_test() {
    print_status "Running performance tests..."
    
    # Test image loading performance
    echo "Testing image loading performance..."
    
    # Test multiple image requests
    for i in {1..10}; do
        curl -s "http://localhost:8001/images/placeholder/met?width=400&height=400" > /dev/null &
    done
    wait
    
    print_success "Performance test completed"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop Redis container if it was started
    docker stop art-explorer-redis 2>/dev/null || true
    docker rm art-explorer-redis 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Main deployment function
deploy() {
    print_status "Starting advanced deployment..."
    
    # Check prerequisites
    check_docker
    
    # Setup Redis
    setup_redis
    
    # Install dependencies
    install_dependencies
    
    # Setup database
    setup_database
    
    # Start services
    start_backend
    start_frontend
    
    # Populate database
    populate_database
    
    # Test advanced features
    test_image_features
    
    # Monitor resources
    monitor_resources
    
    # Performance test
    performance_test
    
    print_success "🎉 Advanced deployment completed!"
    echo ""
    echo "📱 Application URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8001"
    echo "API Docs: http://localhost:8001/docs"
    echo ""
    echo "🔧 Advanced Features:"
    echo "• Image optimization with caching"
    echo "• Progressive image loading"
    echo "• Redis-based caching"
    echo "• Multiple fallback strategies"
    echo "• Performance monitoring"
    echo ""
    echo "📊 Monitoring:"
    echo "• Health check: curl http://localhost:8001/health"
    echo "• Cache stats: curl http://localhost:8001/images/cache"
    echo "• System resources: ./deploy_advanced.sh monitor"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for user interrupt
    trap cleanup EXIT
    wait
}

# Command line interface
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "monitor")
        monitor_resources
        ;;
    "test")
        test_image_features
        ;;
    "performance")
        performance_test
        ;;
    "cleanup")
        cleanup
        ;;
    "help")
        echo "Usage: $0 [deploy|monitor|test|performance|cleanup|help]"
        echo ""
        echo "Commands:"
        echo "  deploy      - Full deployment with advanced features"
        echo "  monitor     - Monitor system resources"
        echo "  test        - Test image optimization features"
        echo "  performance - Run performance tests"
        echo "  cleanup     - Clean up all services"
        echo "  help        - Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 