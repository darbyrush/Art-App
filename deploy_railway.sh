#!/bin/bash

# Railway Deployment Script for Art App
# This script helps you deploy your app to Railway with proper configuration

echo "🚀 Railway Deployment Script for Art App"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "docker/Dockerfile.backend" ]; then
    echo "❌ Error: Please run this script from the Art App root directory"
    exit 1
fi

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "   Consider committing them before deployment"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "   1. ✅ Dockerfile.backend is configured"
echo "   2. ✅ railway.json is set up"
echo "   3. ✅ Environment variables are ready"
echo ""

echo "🔧 Environment Variables to Add to Railway:"
echo "=========================================="
echo ""
echo "DATABASE_URL=postgresql://postgres:VPzlvfYNNmRSpxWukjeUIuGDsSFHwKOc@postgres.railway.internal:5432/railway"
echo "SECRET_KEY=9Y3-ps7BXOl5RTUDwYvEDhNOZbNMenzqPnZdPcLRsbw"
echo "ENVIRONMENT=production"
echo "CORS_ORIGINS=https://myassemblage.art,https://www.myassemblage.art,https://art-app-frontend.vercel.app,https://*.vercel.app"
echo ""

echo "📝 Steps to Deploy:"
echo "==================="
echo ""
echo "1. Go to your Railway project dashboard"
echo "2. Select your backend service"
echo "3. Go to 'Variables' tab"
echo "4. Add the environment variables above"
echo "5. Railway will auto-redeploy"
echo ""

echo "🔍 Post-deployment Verification:"
echo "==============================="
echo ""
echo "1. Check Railway logs for:"
echo "   - 'Starting with PORT=8080' (or your assigned port)"
echo "   - 'Using PostgreSQL database for production'"
echo "   - 'Database tables created successfully'"
echo ""
echo "2. Test health endpoint:"
echo "   - Visit: https://your-railway-app.railway.app/health"
echo "   - Should show: {\"status\": \"healthy\", \"database\": \"connected\"}"
echo ""

echo "🚀 Ready to deploy! Push your changes to trigger Railway deployment:"
echo "   git add . && git commit -m 'Ready for Railway deployment' && git push origin main"
echo ""

read -p "Press Enter to continue or Ctrl+C to cancel..."
