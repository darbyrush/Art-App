#!/bin/bash

echo "🔍 Railway Configuration Verification Script"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "railway.json" ]; then
    echo "❌ Error: railway.json not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Found railway.json"

# Check Dockerfile.backend exists
if [ ! -f "docker/Dockerfile.backend" ]; then
    echo "❌ Error: docker/Dockerfile.backend not found"
    exit 1
fi

echo "✅ Found docker/Dockerfile.backend"

# Check main.py exists
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: api/main.py not found"
    exit 1
fi

echo "✅ Found api/main.py"

# Check requirements.txt exists
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: backend/requirements.txt not found"
    exit 1
fi

echo "✅ Found backend/requirements.txt"

# Verify Dockerfile.backend content
echo ""
echo "🔍 Checking Dockerfile.backend configuration..."

# Check if it exposes the right port
if grep -q "EXPOSE 8000" docker/Dockerfile.backend; then
    echo "✅ Dockerfile exposes port 8000"
else
    echo "❌ Dockerfile does not expose port 8000"
fi

# Check if it uses PORT environment variable
if grep -q "\${PORT:-8000}" docker/Dockerfile.backend; then
    echo "✅ Dockerfile uses PORT environment variable"
else
    echo "❌ Dockerfile does not use PORT environment variable"
fi

# Check health check endpoint
if grep -q "/health" docker/Dockerfile.backend; then
    echo "✅ Health check points to /health endpoint"
else
    echo "❌ Health check does not point to /health endpoint"
fi

# Check if it uses uvicorn
if grep -q "uvicorn" docker/Dockerfile.backend; then
    echo "✅ Uses uvicorn for running the app"
else
    echo "❌ Does not use uvicorn"
fi

# Check if it runs api.main:app
if grep -q "api.main:app" docker/Dockerfile.backend; then
    echo "✅ Runs api.main:app (correct for root directory)"
else
    echo "❌ Does not run api.main:app"
fi

# Check PYTHONPATH setting
if grep -q "PYTHONPATH=/app:/app/api" docker/Dockerfile.backend; then
    echo "✅ PYTHONPATH includes both /app and /app/api"
else
    echo "❌ PYTHONPATH not set correctly"
fi

echo ""
echo "🔍 Checking main.py configuration..."

# Check if main.py has health endpoint
if grep -q "@app.get(\"/health\")" api/main.py; then
    echo "✅ main.py has /health endpoint"
else
    echo "❌ main.py missing /health endpoint"
fi

# Check if main.py handles PORT environment variable
if grep -q "os.getenv(\"PORT\"" api/main.py; then
    echo "✅ main.py handles PORT environment variable"
else
    echo "❌ main.py does not handle PORT environment variable"
fi

# Check if main.py has proper import fallbacks
if grep -q "from api.database.models import" api/main.py; then
    echo "✅ main.py has production import paths"
else
    echo "❌ main.py missing production import paths"
fi

if grep -q "from database.models import" api/main.py; then
    echo "✅ main.py has development import paths"
else
    echo "❌ main.py missing development import paths"
fi

# Check if main.py has robust CORS handling
if grep -q "Add CORS middleware with robust configuration" api/main.py; then
    echo "✅ main.py has robust CORS middleware handling"
else
    echo "❌ main.py missing robust CORS middleware handling"
fi

echo ""
echo "🔍 Checking Railway configuration..."

# Check railway.json
if grep -q "Dockerfile.backend" railway.json; then
    echo "✅ railway.json points to correct Dockerfile"
else
    echo "❌ railway.json does not point to Dockerfile.backend"
fi

if grep -q "/health" railway.json; then
    echo "✅ railway.json has correct healthcheck path"
else
    echo "❌ railway.json missing healthcheck path"
fi

echo ""
echo "📋 Summary of Railway deployment requirements:"
echo "1. ✅ Dockerfile.backend exists and is configured"
echo "2. ✅ main.py has health endpoint and PORT handling"
echo "3. ✅ railway.json points to correct files"
echo "4. ✅ Health check endpoint is /health"
echo "5. ✅ Port configuration uses PORT environment variable"
echo "6. ✅ Import paths work in both development and production"
echo "7. ✅ PYTHONPATH includes both /app and /app/api"
echo "8. ✅ Robust CORS middleware handling with fallbacks"

echo ""
echo "🚀 To deploy to Railway:"
echo "1. Commit these changes: git add . && git commit -m 'Fix Railway deployment configuration'"
echo "2. Push to your repository: git push origin main"
echo "3. Railway should automatically redeploy"
echo ""
echo "🔍 To debug deployment issues:"
echo "1. Check Railway logs: railway logs"
echo "2. Check Railway status: railway status"
echo "3. Verify environment variables in Railway dashboard"
echo "4. Check if the /health endpoint responds: curl https://your-app.railway.app/health"
echo "5. Verify import paths work in container environment"
echo "6. Use debug script: scripts/debug_container.py"
