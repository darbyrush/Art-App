#!/bin/bash

# Fix Railway Backend Issues Script
echo "🔧 Railway Backend Troubleshooting Script"
echo "=========================================="

echo ""
echo "🚨 Current Status: Backend returning 502 errors"
echo "   This means the app is deployed but not running properly"
echo ""

echo "📋 Checklist to fix:"
echo "1. ✅ Check Railway dashboard for deployment status"
echo "2. ✅ Verify environment variables are set"
echo "3. ✅ Check database connection"
echo "4. ✅ Review deployment logs"
echo "5. ✅ Restart the service if needed"
echo ""

echo "🌐 Your Railway URLs:"
echo "   Public: https://art-app-production.up.railway.app"
echo "   Private: art-app.railway.internal"
echo ""

echo "🔍 Quick diagnostic commands:"
echo "   curl -v https://art-app-production.up.railway.app/health"
echo "   curl -v https://art-app-production.up.railway.app/test"
echo ""

echo "📚 Next steps:"
echo "1. Go to railway.app and check your project"
echo "2. Look at the Deployments tab for failed builds"
echo "3. Check the Logs tab for error messages"
echo "4. Verify all environment variables are set"
echo "5. Check if PostgreSQL service is running"
echo ""

echo "💡 Common fixes:"
echo "   - Restart the service in Railway dashboard"
echo "   - Check DATABASE_URL is correct"
echo "   - Verify SECRET_KEY is set"
echo "   - Look for missing dependencies in logs"
echo ""

echo "🎯 Once backend is working, test with:"
echo "   python test_railway_connection.py https://art-app-production.up.railway.app"
echo ""

read -p "Press Enter to continue..."
