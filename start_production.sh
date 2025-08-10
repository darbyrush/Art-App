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
