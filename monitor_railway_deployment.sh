#!/bin/bash

echo "🔍 Monitoring Railway Deployment"
echo "================================"
echo

RAILWAY_URL="https://art-app-production.up.railway.app"
MAX_ATTEMPTS=30
ATTEMPT=1

echo "🚀 Railway is now redeploying with our fixes..."
echo "⏳ This may take 3-5 minutes for a complete rebuild."
echo "🔍 Monitoring deployment progress..."
echo

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "🔍 Attempt $ATTEMPT/$MAX_ATTEMPTS - Testing endpoints..."
    
    # Test basic connectivity first
    if curl -s --connect-timeout 10 "$RAILWAY_URL/startup-health" > /dev/null 2>&1; then
        echo "✅ Basic connectivity established!"
        
        # Test specific endpoints
        echo "🧪 Testing key endpoints..."
        
        # Test startup health
        if curl -s "$RAILWAY_URL/startup-health" | grep -q "starting"; then
            echo "✅ /startup-health: Working"
        else
            echo "❌ /startup-health: Failed"
        fi
        
        # Test readiness check
        if curl -s "$RAILWAY_URL/ready" | grep -q "ready\|degraded"; then
            echo "✅ /ready: Working"
        else
            echo "❌ /ready: Failed"
        fi
        
        # Test auth login OPTIONS
        if curl -s -X OPTIONS "$RAILWAY_URL/auth/login" | grep -q "CORS preflight"; then
            echo "✅ /auth/login OPTIONS: Working"
        else
            echo "❌ /auth/login OPTIONS: Failed"
        fi
        
        # Test auth endpoint info
        if curl -s "$RAILWAY_URL/test/auth" | grep -q "login"; then
            echo "✅ /test/auth: Working"
        else
            echo "❌ /test/auth: Failed"
        fi
        
        echo
        echo "🎉 Railway deployment appears to be working!"
        echo "🧪 Run the full test: python3 test_railway_deployment.py"
        echo "🌐 Test in browser: $RAILWAY_URL/test"
        exit 0
        
    else
        echo "⏳ Still deploying... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
        echo "   Waiting 30 seconds before next attempt..."
        sleep 30
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done

echo
echo "❌ Deployment monitoring timed out after $MAX_ATTEMPTS attempts"
echo "🔍 Check Railway logs at: https://railway.app"
echo "📋 Common issues:"
echo "   - Database connection problems"
echo "   - Environment variable issues"
echo "   - Container resource limits"
echo "   - Build failures"
