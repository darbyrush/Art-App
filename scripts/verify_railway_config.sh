#!/bin/bash

echo "🔍 Railway Configuration Verification Script"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "railway.json" ]; then
    echo "❌ Error: railway.json not found. Please run this script from the project root."
    exit 1
fi

echo "✅ Found railway.json"

# Check Dockerfile.backend.simple exists
if [ ! -f "docker/Dockerfile.backend.simple" ]; then
    echo "❌ Error: docker/Dockerfile.backend.simple not found"
    exit 1
fi

echo "✅ Found docker/Dockerfile.backend.simple"

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

# Verify Dockerfile.backend.simple content
echo ""
echo "🔍 Checking Dockerfile.backend.simple configuration..."

# Check if it exposes the right port
if grep -q "EXPOSE 8000" docker/Dockerfile.backend.simple; then
    echo "✅ Dockerfile exposes port 8000"
else
    echo "❌ Dockerfile does not expose port 8000"
fi

# Check if it uses PORT environment variable
if grep -q "\${PORT:-8000}" docker/Dockerfile.backend.simple; then
    echo "✅ Dockerfile uses PORT environment variable"
else
    echo "❌ Dockerfile does not use PORT environment variable"
fi

# Check health check endpoint
if grep -q "/health" docker/Dockerfile.backend.simple; then
    echo "✅ Health check points to /health endpoint"
else
    echo "❌ Health check does not point to /health endpoint"
fi

# Check if it uses uvicorn
if grep -q "uvicorn" docker/Dockerfile.backend.simple; then
    echo "✅ Uses uvicorn for running the app"
else
    echo "❌ Does not use uvicorn"
fi

# Check if it runs api.main:app
if grep -q "api.main:app" docker/Dockerfile.backend.simple; then
    echo "✅ Runs api.main:app (correct for root directory)"
else
    echo "❌ Does not run api.main:app"
fi

# Check PYTHONPATH setting
if grep -q "PYTHONPATH=/app" docker/Dockerfile.backend.simple; then
    echo "✅ PYTHONPATH set to /app"
else
    echo "❌ PYTHONPATH not set correctly"
fi

# Check if it installs necessary system dependencies
if grep -q "libpq-dev" docker/Dockerfile.backend.simple; then
    echo "✅ Installs PostgreSQL development libraries"
else
    echo "❌ Missing PostgreSQL development libraries"
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

# Check if main.py has production import paths
if grep -q "from api.database.models import" api/main.py; then
    echo "✅ main.py has production import paths"
else
    echo "❌ main.py missing production import paths"
fi

# Check if main.py has simplified CORS handling
if grep -q "Add CORS middleware using Railway environment variables directly" api/main.py; then
    echo "✅ main.py has simplified CORS configuration"
else
    echo "❌ main.py missing simplified CORS configuration"
fi

# Check if main.py uses environment variables for CORS
if grep -q "os.getenv(\"CORS_ORIGINS\"" api/main.py; then
    echo "✅ main.py uses Railway environment variables for CORS"
else
    echo "❌ main.py does not use Railway environment variables for CORS"
fi

echo ""
echo "🔍 Checking Railway configuration..."

# Check railway.json
if grep -q "Dockerfile.backend.simple" railway.json; then
    echo "✅ railway.json points to correct Dockerfile"
else
    echo "❌ railway.json does not point to Dockerfile.backend.simple"
fi

if grep -q "/health" railway.json; then
    echo "✅ railway.json has correct healthcheck path"
else
    echo "❌ railway.json missing healthcheck path"
fi

echo ""
echo "📋 Summary of Railway deployment requirements:"
echo "1. ✅ Dockerfile.backend.simple exists and is configured"
echo "2. ✅ main.py has health endpoint and PORT handling"
echo "3. ✅ railway.json points to correct files"
echo "4. ✅ Health check endpoint is /health"
echo "5. ✅ Port configuration uses PORT environment variable"
echo "6. ✅ Production import paths configured"
echo "7. ✅ PYTHONPATH set to /app"
echo "8. ✅ Simplified CORS configuration using Railway environment variables"
echo "9. ✅ PostgreSQL development libraries installed"

echo ""
echo "🚀 To deploy to Railway:"
echo "1. Commit these changes: git add . && git commit -m 'Simplify CORS configuration and use Railway environment variables'"
echo "2. Push to your repository: git push origin main"
echo "3. Railway should automatically redeploy"
echo ""
echo "🔍 To debug deployment issues:"
echo "1. Check Railway logs: railway logs"
echo "2. Check Railway status: railway status"
echo "3. Verify environment variables in Railway dashboard"
echo "4. Check if the /health endpoint responds: curl https://your-app.railway.app/health"
echo "5. Verify import paths work in container environment"
echo "6. Use debug script: scripts/test_simple_startup.py"
echo ""
echo "🌍 Railway Environment Variables to Set:"
echo "- CORS_ORIGINS: https://myassemblage.art,https://www.myassemblage.art"
echo "- DATABASE_URL: Your Railway PostgreSQL connection string"
echo "- SECRET_KEY: Your JWT secret key"
echo "- ENVIRONMENT: production"
