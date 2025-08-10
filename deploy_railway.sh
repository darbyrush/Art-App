#!/bin/bash

# Railway Deployment Script for Art Explorer App
# This script helps prepare and deploy your app to Railway

set -e

echo "🚂 Railway Deployment Script for Art Explorer"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "railway.json" ]; then
    echo "❌ Error: railway.json not found. Please run this script from the project root."
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not initialized. Please run 'git init' first."
    exit 1
fi

# Check if changes are committed
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes."
    echo "   Please commit your changes before deploying:"
    echo "   git add . && git commit -m 'Prepare for Railway deployment'"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Pre-deployment checks passed"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI already installed"
fi

echo ""
echo "🔧 Next steps:"
echo "1. Login to Railway: railway login"
echo "2. Initialize project: railway init"
echo "3. Deploy: railway up"
echo ""
echo "📚 For detailed instructions, see RAILWAY_DEPLOYMENT.md"
echo ""
echo "🌐 To configure your custom domain:"
echo "   - Add domain in Railway dashboard"
echo "   - Update DNS records at your registrar"
echo "   - Set environment variables for production"
echo ""

# Check if user wants to proceed with Railway commands
read -p "Would you like to run 'railway login' now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Logging into Railway..."
    railway login
fi

echo ""
echo "🎉 Setup complete! Your app is ready for Railway deployment."
echo "   Follow the steps above or check RAILWAY_DEPLOYMENT.md for details."
