#!/bin/bash

# Railway startup script for Art Explorer Backend
# This script properly handles the PORT environment variable

echo "🚀 Starting Art Explorer Backend on Railway..."

# Set default port if not provided
PORT=${PORT:-8000}
echo "📡 Using port: $PORT"

# Check if we're in production mode
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🏭 Production mode detected"
    
    # Start with gunicorn for production
    echo "🔄 Starting gunicorn with uvicorn workers..."
    exec gunicorn api.main:app \
        --bind 0.0.0.0:$PORT \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 120 \
        --keep-alive 5 \
        --access-logfile - \
        --error-logfile -
else
    echo "🔧 Development mode detected"
    
    # Start with uvicorn for development
    echo "🔄 Starting uvicorn in development mode..."
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --reload
fi
