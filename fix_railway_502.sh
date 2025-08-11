#!/bin/bash

echo "🚀 Fixing Railway 502 Errors"
echo "============================"
echo

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📝 Committing the fixes..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "Fix Railway 502 errors: improve startup robustness and health checks"
    echo "✅ Changes committed"
fi

echo
echo "🚀 Pushing to GitHub (this will trigger Railway redeployment)..."
git push origin main

echo
echo "⏳ Railway will now automatically redeploy with the fixes..."
echo "This may take 2-5 minutes."
echo
echo "📊 Monitor deployment at: https://railway.app"
echo "🔍 Check logs for startup messages"
echo
echo "🧪 After deployment, test with:"
echo "   python test_railway_deployment.py"
echo
echo "🎯 Expected improvements:"
echo "   - App won't crash during startup"
echo "   - Better error handling for database issues"
echo "   - More robust health checks"
echo "   - Improved logging for debugging"
echo
echo "📋 If issues persist, check:"
echo "   1. Railway logs for specific error messages"
echo "   2. Database connection string in Railway environment variables"
echo "   3. All required environment variables are set"
echo "   4. Container resource limits in Railway"
