#!/bin/bash

echo "🔧 Fixing Railway Multiple Process Issues"
echo "========================================="
echo

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📝 The main issues identified:"
echo "   1. Multiple Uvicorn processes starting (processes 2, 4, 5, 6, 7)"
echo "   2. Port mismatch: Dockerfile expects 8000, Railway sets 8080"
echo "   3. Health check failing due to process confusion"
echo

echo "🔧 Fixes applied:"
echo "   1. Changed Dockerfile to use exec form and single worker"
echo "   2. Added startup completion flag to prevent multiple initializations"
echo "   3. Fixed health check to use correct port"
echo "   4. Added process ID logging for debugging"
echo

echo "📝 Committing the fixes..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "Fix Railway multiple process issues: single worker, port handling, startup flags"
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
echo "🔍 Check logs for these expected improvements:"
echo "   - Single process starting (not multiple)"
echo "   - Correct port usage (8080 from Railway)"
echo "   - Startup completion flag working"
echo "   - Health checks passing"
echo
echo "🧪 After deployment, test with:"
echo "   python test_railway_deployment.py"
echo
echo "🎯 Expected results:"
echo "   - Single Uvicorn process"
echo "   - App responds on port 8080"
echo "   - Health checks pass"
echo "   - No more 502 errors"
echo
echo "📋 If issues persist, check:"
echo "   1. Railway logs for single process startup"
echo "   2. Port configuration in Railway"
echo "   3. Health check endpoint responses"
echo "   4. Process ID consistency in logs"
