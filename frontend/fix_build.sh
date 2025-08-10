#!/bin/bash

# 🔧 Frontend Build Fix Script
# This script fixes common Vite build issues

set -e

echo "🔧 Fixing frontend build issues..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the frontend directory
if [[ ! -f "package.json" ]]; then
    print_error "Please run this script from the frontend directory"
    exit 1
fi

# Clean up any existing build artifacts
print_status "Cleaning build artifacts..."
rm -rf node_modules package-lock.json dist .vite

# Install dependencies fresh
print_status "Installing dependencies..."
npm install

# Install terser specifically (in case it's missing)
print_status "Ensuring terser is installed..."
npm install --save-dev terser@^5.24.0

# Verify critical dependencies
print_status "Verifying critical dependencies..."
if ! npm list terser > /dev/null 2>&1; then
    print_error "Terser not found after installation!"
    exit 1
fi

if ! npm list vite > /dev/null 2>&1; then
    print_error "Vite not found after installation!"
    exit 1
fi

print_status "Dependencies verified ✓"

# Test build
print_status "Testing build..."
if npm run build; then
    print_status "Build successful! ✓"
else
    print_error "Build failed! Check the error messages above."
    exit 1
fi

# Check build output
if [[ -d "dist" ]]; then
    print_status "Build output directory created ✓"
    ls -la dist/
else
    print_error "Build output directory not found!"
    exit 1
fi

print_status "Frontend build issues fixed! 🎉"
echo ""
echo "📋 Next steps:"
echo "1. Your build should now work properly"
echo "2. For production deployment, use: npm run build"
echo "3. The dist/ folder contains your built application"
echo ""
echo "💡 If you still encounter issues, check:"
echo "   - Node.js version (recommend v18+ or v20+)"
echo "   - npm version (recommend v8+)"
echo "   - Available disk space"
