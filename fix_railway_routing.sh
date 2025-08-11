#!/bin/bash

echo "🔧 Fixing Railway Routing Issue"
echo "==============================="
echo

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📝 The routing issue identified:"
echo "   1. Frontend calls /auth/login (from apiClient.js and auth.js)"
echo "   2. Backend only had /token endpoint"
echo "   3. Missing /auth/login endpoint causing 502 errors"
echo "   4. CORS preflight failing due to missing route"
echo

echo "🔧 Fixes applied:"
echo "   1. Added /auth/login endpoint that redirects to /token logic"
echo "   2. Added /auth/register endpoint for consistency"
echo "   3. Enhanced OPTIONS handlers for auth endpoints"
echo "   4. Added test endpoints to verify routing"
echo

echo "📝 Committing the routing fixes..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "Fix Railway routing: add missing /auth/login and /auth/register endpoints"
    echo "✅ Changes committed"
fi

echo
echo "🚀 Pushing to GitHub (this will trigger Railway redeployment)..."
git push origin main

echo
echo "⏳ Railway will now automatically redeploy with the routing fixes..."
echo "This may take 2-5 minutes."
echo
echo "📊 Monitor deployment at: https://railway.app"
echo "🔍 Check logs for these expected improvements:"
echo "   - /auth/login endpoint now exists"
echo "   - /auth/register endpoint now exists"
echo "   - CORS preflight requests should succeed"
echo "   - No more 502 errors on auth endpoints"
echo
echo "🧪 After deployment, test with:"
echo "   python test_railway_deployment.py"
echo
echo "🎯 Expected results:"
echo "   - OPTIONS /auth/login returns 200"
echo "   - POST /auth/login works for login"
echo "   - Frontend can successfully authenticate"
echo "   - No more CORS preflight failures"
echo
echo "📋 Test the specific endpoints:"
echo "   curl -X OPTIONS https://art-app-production.up.railway.app/auth/login"
echo "   curl -X GET https://art-app-production.up.railway.app/test/auth"
echo
echo "📋 If issues persist, check:"
echo "   1. Railway logs for new endpoint registration"
echo "   2. CORS headers in responses"
echo "   3. Frontend API calls are using correct paths"
echo "   4. All auth endpoints are responding"
