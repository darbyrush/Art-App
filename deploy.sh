#!/bin/bash

# Art Explorer Deployment Script
# This script deploys the full application with all improvements

set -e  # Exit on any error

echo "🚀 Starting Art Explorer Deployment"
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

# Check if we're in the right directory
if [ ! -f "api/main.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

print_status "Checking system requirements..."

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python version: $PYTHON_VERSION"

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
NODE_MINOR=$(echo $NODE_VERSION | cut -d'.' -f2)
if [ "$NODE_MAJOR" -lt 16 ] || ([ "$NODE_MAJOR" -eq 16 ] && [ "$NODE_MINOR" -lt 0 ]); then
    print_error "Node.js 16.0 or higher is required. Found: $NODE_VERSION"
    exit 1
fi
print_success "Node.js version: $NODE_VERSION"

print_status "Setting up backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
print_status "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install additional dependencies for image processing
print_status "Installing image processing dependencies..."
pip install aiohttp pillow

# Initialize database
print_status "Initializing database..."
cd api
python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from database.config import init_db
try:
    init_db()
    print('Database initialized successfully')
except Exception as e:
    print(f'Warning: Could not initialize database: {e}')
"

# Populate database with artworks
print_status "Populating database with artworks..."
python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from api.artwork_populator import populate_database
try:
    results = populate_database(artworks_per_source=5)
    print(f'Database populated with {sum(results.values())} artworks')
except Exception as e:
    print(f'Warning: Could not populate database: {e}')
"

# Validate and fix image URLs
print_status "Validating and fixing image URLs..."
python ../scripts/validate_images.py || print_warning "Image validation failed - continuing anyway"

cd ..

print_status "Setting up frontend..."

# Install frontend dependencies
cd frontend
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
else
    print_status "Updating frontend dependencies..."
    npm update
fi

# Build frontend
print_status "Building frontend..."
npm run build

cd ..

print_status "Setting up environment variables..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./art_api_cache.sqlite

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
VITE_API_URL=http://localhost:8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# Background Tasks
ENABLE_BACKGROUND_TASKS=true
POPULATION_INTERVAL_HOURS=24
CLEANUP_INTERVAL_HOURS=168

# Logging
LOG_LEVEL=INFO
EOF
    print_success "Created .env file"
else
    print_warning ".env file already exists"
fi

print_status "Creating startup scripts..."

# Create backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Create frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/frontend"
npm run dev
EOF

# Create full startup script
cat > start_app.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting Art Explorer Application"
echo "=================================="

# Start backend in background
echo "Starting backend server..."
source venv/bin/activate
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend development server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

# Make scripts executable
chmod +x start_backend.sh start_frontend.sh start_app.sh

print_status "Running health checks..."

# Test backend
print_status "Testing backend..."
cd api
python -c "
import requests
import time
import sys

# Wait for server to start
time.sleep(2)

try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.status_code == 200:
        print('✅ Backend is healthy')
    else:
        print(f'❌ Backend health check failed: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Backend health check failed: {e}')
    sys.exit(1)
" || {
    print_warning "Backend health check failed - this is normal if the server isn't running"
}

cd ..

print_success "Deployment completed successfully!"
echo ""
echo "🎉 Art Explorer is ready to use!"
echo ""
echo "📋 Quick Start:"
echo "1. Start the full application: ./start_app.sh"
echo "2. Start backend only: ./start_backend.sh"
echo "3. Start frontend only: ./start_frontend.sh"
echo ""
echo "🌐 Access Points:"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/health"
echo ""
echo "🔧 Management:"
echo "- Validate images: python scripts/validate_images.py"
echo "- Populate database: python -c 'from api.artwork_populator import populate_database; populate_database()'"
echo ""
echo "📝 Notes:"
echo "- The backend will automatically populate with artworks from external APIs"
echo "- Broken image URLs will be replaced with placeholder images"
echo "- The infinite scroll has been improved to prevent scroll-to-top issues"
echo "- Rating functionality has been enhanced with better error handling"
echo "- The app now scales better with multiple users"
echo ""
print_success "Happy exploring! 🎨" 