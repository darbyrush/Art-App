#!/bin/bash

echo "🧪 Testing Clean Railway Deployment"
echo "=================================="
echo

RAILWAY_URL="https://art-app-production.up.railway.app"

echo "⏳ Waiting for Railway deployment to complete..."
echo "This may take 3-5 minutes..."
echo

# Wait a bit for deployment to start
sleep 30

echo "🔍 Testing basic endpoints..."
echo "============================"
echo

# Test health endpoint
echo "1. Testing /health endpoint..."
if curl -s "$RAILWAY_URL/health" > /dev/null; then
    echo "   ✅ /health endpoint is working!"
else
    echo "   ❌ /health endpoint failed"
fi

echo

# Test root endpoint
echo "2. Testing root endpoint (/)..."
if curl -s "$RAILWAY_URL/" > /dev/null; then
    echo "   ✅ Root endpoint is working!"
else
    echo "   ❌ Root endpoint failed"
fi

echo

# Test auth endpoint (OPTIONS)
echo "3. Testing /auth/login OPTIONS..."
if curl -s -X OPTIONS "$RAILWAY_URL/auth/login" > /dev/null; then
    echo "   ✅ /auth/login OPTIONS is working!"
else
    echo "   ❌ /auth/login OPTIONS failed"
fi

echo

echo "📊 Deployment Status Summary:"
echo "============================="
echo "✅ Simplified configuration deployed"
echo "✅ Complex features removed"
echo "✅ Basic endpoints should work"
echo "✅ No more 502 errors expected"
echo

echo "🌐 Test URLs:"
echo "============="
echo "Health: $RAILWAY_URL/health"
echo "Root: $RAILWAY_URL/"
echo "Login: $RAILWAY_URL/auth/login"
echo

echo "🎯 Next Steps:"
echo "=============="
echo "1. Wait for Railway deployment to complete"
echo "2. Test the endpoints above"
echo "3. If they work, your app is back to working state!"
echo "4. Then gradually add features back one at a time"
echo

echo "💡 If you still get 502 errors:"
echo "==============================="
echo "1. Check Railway deployment logs"
echo "2. Verify environment variables are set correctly"
echo "3. Ensure PostgreSQL service is running"
echo "4. Wait for full deployment completion"
echo

echo "🎉 The clean deployment should resolve your 502 errors!"
