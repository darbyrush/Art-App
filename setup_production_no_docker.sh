#!/bin/bash

# Production Setup Script for Art Explorer (No Docker)
# This script helps set up the production environment without Docker

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

log "Setting up production environment for Art Explorer (No Docker mode)..."

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

# Check Python installation
log "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    success "Python found: $PYTHON_VERSION"
else
    error "Python3 is not installed"
    exit 1
fi

# Check pip installation
log "Checking pip installation..."
if command -v pip3 &> /dev/null; then
    success "pip3 is installed"
else
    error "pip3 is not installed"
    exit 1
fi

# Check Node.js installation
log "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    success "Node.js found: $NODE_VERSION"
else
    error "Node.js is not installed"
    exit 1
fi

# Check npm installation
log "Checking npm installation..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    success "npm found: $NPM_VERSION"
else
    error "npm is not installed"
    exit 1
fi

# Create necessary directories
log "Creating necessary directories..."
mkdir -p uploads/profile_pictures
mkdir -p logs
mkdir -p backups
mkdir -p ssl
success "Created necessary directories"

# Check virtual environment
log "Checking virtual environment..."
if [[ -d "venv" ]]; then
    success "Virtual environment found"
    log "Activating virtual environment..."
    source venv/bin/activate
else
    warning "Virtual environment not found, creating one..."
    python3 -m venv venv
    source venv/bin/activate
    success "Virtual environment created and activated"
fi

# Install Python dependencies
log "Installing Python dependencies..."
if [[ -f "backend/requirements.txt" ]]; then
    pip install -r backend/requirements.txt
    success "Python dependencies installed"
else
    warning "backend/requirements.txt not found"
fi

# Install frontend dependencies
log "Installing frontend dependencies..."
if [[ -d "frontend" ]] && [[ -f "frontend/package.json" ]]; then
    cd frontend
    npm install
    cd ..
    success "Frontend dependencies installed"
else
    warning "Frontend directory or package.json not found"
fi

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

# Create production start script
log "Creating production start script..."
cat > start_production.sh << 'EOF'
#!/bin/bash

# Production Start Script for Art Explorer (No Docker)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Art Explorer in production mode...${NC}"

# Activate virtual environment
source venv/bin/activate

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd frontend
npm run build
npx serve -s dist -l 3000 &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}Art Explorer is running!${NC}"
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo -e "${BLUE}Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
EOF

chmod +x start_production.sh
success "Created start_production.sh script"

# Create production stop script
log "Creating production stop script..."
cat > stop_production.sh << 'EOF'
#!/bin/bash

# Production Stop Script for Art Explorer

echo "Stopping Art Explorer services..."

# Kill backend processes
pkill -f "uvicorn main:app" || true

# Kill frontend processes
pkill -f "serve -s dist" || true

echo "All services stopped"
EOF

chmod +x stop_production.sh
success "Created stop_production.sh script"

# Show next steps
echo ""
echo -e "${GREEN}Production environment setup completed (No Docker mode)!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env.production with your actual values:"
echo "   - Database credentials"
echo "   - API keys for art services"
echo "   - Domain names"
echo ""
echo "2. Start production services:"
echo "   ./start_production.sh"
echo ""
echo "3. Stop production services:"
echo "   ./stop_production.sh"
echo ""
echo -e "${YELLOW}Important notes:${NC}"
echo "- This setup runs services directly on your machine"
echo "- For true production, consider installing Docker for containerization"
echo "- Keep .env.production secure and never commit it to git"
echo "- Use strong, unique passwords for all services"
echo ""
echo -e "${YELLOW}To install Docker (recommended for production):${NC}"
echo "1. Visit: https://www.docker.com/products/docker-desktop"
echo "2. Download Docker Desktop for Mac"
echo "3. Install and restart your computer"
echo "4. Run: ./setup_production.sh (for Docker mode)"
echo ""
echo -e "${GREEN}Your Art Explorer app is ready for production deployment!${NC}"
