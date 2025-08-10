#!/bin/bash

echo "🔍 Verifying Railway Backend Configuration"
echo "=========================================="

# Check if the config file has the correct Railway URL
echo "1. Checking frontend config.js..."
if grep -q "https://art-app-production.up.railway.app" src/config.js; then
    echo "✅ config.js has correct Railway URL"
else
    echo "❌ config.js missing Railway URL"
fi

# Check if environment files are correct
echo "2. Checking environment files..."
if grep -q "https://art-app-production.up.railway.app" env.production; then
    echo "✅ env.production has correct Railway URL"
else
    echo "❌ env.production missing Railway URL"
fi

# Check if any localhost references remain in source files
echo "3. Checking for remaining localhost references..."
localhost_count=$(grep -r "localhost:8000" src/ --include="*.vue" --include="*.js" | wc -l)
if [ $localhost_count -eq 0 ]; then
    echo "✅ No localhost:8000 references found in source files"
else
    echo "❌ Found $localhost_count localhost:8000 references in source files:"
    grep -r "localhost:8000" src/ --include="*.vue" --include="*.js"
fi

# Check if config imports are properly added
echo "4. Checking config imports..."
components_with_config=$(grep -l "import.*config.*from.*@/config" src/components/*.vue src/views/*.vue | wc -l)
echo "✅ $components_with_config components have config imports"

# Check if the build works
echo "5. Testing build..."
if npm run build > /dev/null 2>&1; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    echo "Running build to see errors..."
    npm run build
fi

echo ""
echo "🎯 Configuration Summary:"
echo "- Frontend should point to: https://art-app-production.up.railway.app"
echo "- Backend CORS should allow: https://myassemblage.art"
echo "- Environment variables should be set in Railway dashboard"
echo ""
echo "📝 Next steps:"
echo "1. Commit these changes"
echo "2. Push to your repository"
echo "3. Redeploy on Vercel"
echo "4. Verify the frontend connects to Railway backend"
