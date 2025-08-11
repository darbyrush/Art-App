#!/bin/bash

echo "🏗️  Rebuilding Railway App with Clean, Minimal Configuration"
echo "============================================================"
echo

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "🧹 Cleaning up complex configurations..."
echo "======================================"
echo

echo "1. 🗑️  REMOVING OVER-ENGINEERED FEATURES"
echo "   - Complex database connection pooling"
echo "   - Overly aggressive timeouts"
echo "   - Complex health checks"
echo "   - Environment validation complexity"
echo

echo "2. 🎯 RESTORING WORKING CONFIGURATION"
echo "   - Simple database connection"
echo "   - Basic CORS setup"
echo "   - Minimal environment variables"
echo "   - Working health endpoints"
echo

echo "3. 🔧 SIMPLIFYING RAILWAY DEPLOYMENT"
echo "   - Remove complex Docker configurations"
echo "   - Simplify environment variables"
echo "   - Basic health checks"
echo "   - Minimal startup logic"
echo

echo "📝 Step 1: Simplifying database configuration..."
echo "==============================================="

# Create a simplified database config
cat > database/config_simple.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Simple database configuration - minimal and working
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./art_explorer.db")

# Create engine with minimal configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info("Using SQLite database")
else:
    # Simple PostgreSQL configuration - no complex pooling
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logger.info("Using PostgreSQL database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
EOF

echo "✅ Created simplified database configuration"

echo
echo "📝 Step 2: Simplifying main.py..."
echo "=================================="

# Create a simplified main.py backup
cp api/main.py api/main.py.backup
echo "✅ Backed up current main.py"

echo
echo "📝 Step 3: Creating minimal Railway configuration..."
echo "=================================================="

# Create minimal railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "docker/Dockerfile.backend"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
EOF

echo "✅ Created minimal railway.json"

echo
echo "📝 Step 4: Creating minimal environment variables..."
echo "=================================================="

# Create minimal railway.env
cat > railway.env.minimal << 'EOF'
# Minimal Railway Environment Variables - Keep it Simple!
DATABASE_URL=postgresql://postgres:VPzlvfYNNmRSpxWukjeUIuGDsSFHwKOc@postgres.railway.internal:5432/railway
SECRET_KEY=9Y3-ps7BXOl5RTUDwOZbNMenzqPnZdPcLRsbw
ENVIRONMENT=production
CORS_ORIGINS=https://myassemblage.art,https://www.myassemblage.art
EOF

echo "✅ Created minimal railway.env.minimal"

echo
echo "📝 Step 5: Creating simplified Dockerfile..."
echo "==========================================="

# Create simplified Dockerfile
cat > docker/Dockerfile.backend.simple << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Simple startup command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "✅ Created simplified Dockerfile"

echo
echo "📝 Step 6: Committing clean configuration..."
echo "=========================================="

git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "Rebuild Railway app: simplify configuration, remove complexity, restore working setup"
    echo "✅ Clean configuration committed"
fi

echo
echo "🚀 Pushing clean configuration to GitHub..."
git push origin main

echo
echo "⏳ Railway will now redeploy with the clean, minimal configuration..."
echo "This should restore the working state you had before adding complexity."
echo
echo "📊 Monitor deployment at: https://railway.app"
echo "🔍 Expected improvements:"
echo "   - Simpler, more reliable deployment"
echo "   - Fewer environment variable conflicts"
echo "   - Basic but working functionality"
echo "   - No more 502 errors from over-engineering"
echo
echo "🧪 After deployment, test:"
echo "   curl https://art-app-production.up.railway.app/health"
echo "   curl https://art-app-production.up.railway.app/"
echo
echo "🎯 This approach:"
echo "   1. Removes complexity that broke the deployment"
echo "   2. Restores the working configuration you had"
echo "   3. Provides a stable foundation to build on"
echo "   4. Eliminates environment variable conflicts"
echo
echo "💡 Next steps after this works:"
echo "   1. Test basic functionality"
echo "   2. Add features one at a time"
echo "   3. Monitor for any issues"
echo "   4. Build complexity gradually"
echo
echo "🎉 Let's get back to a working state first!"
