#!/bin/bash

echo "🚨 Emergency Fallback: Deploying Ultra-Minimal Version"
echo "======================================================"
echo

echo "⚠️  Current deployment has import issues"
echo "🔄 Deploying ultra-minimal version as fallback"
echo

# Replace main.py with ultra-minimal version
cp api/main_minimal.py api/main.py
echo "✅ Replaced main.py with ultra-minimal version"

# Commit and push the fallback
git add api/main.py
git commit -m "Emergency fallback: deploy ultra-minimal working version"
echo "✅ Committed ultra-minimal version"

git push origin main
echo "✅ Pushed ultra-minimal version to GitHub"

echo
echo "🎯 This ultra-minimal version:"
echo "   - Has NO database dependencies"
echo "   - Has NO complex imports"
echo "   - Has NO authentication logic"
echo "   - Just basic FastAPI endpoints"
echo "   - Should definitely deploy successfully"
echo
echo "⏳ Railway will now redeploy with the ultra-minimal version..."
echo "This should resolve the import errors and get your app running."
echo
echo "🧪 After deployment, test:"
echo "   curl https://art-app-production.up.railway.app/health"
echo "   curl https://art-app-production.up.railway.app/"
echo "   curl https://art-app-production.up.railway.app/test"
echo
echo "💡 Once this works, we can gradually add features back:"
echo "   1. First: Basic endpoints working"
echo "   2. Second: Database connection"
echo "   3. Third: Authentication"
echo "   4. Fourth: Complex features"
echo
echo "🎉 Let's get something working first!"
