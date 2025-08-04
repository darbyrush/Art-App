#!/bin/bash

echo "🚀 Art App Deployment Script"
echo "=============================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  You're not on the main branch. Current branch: $current_branch"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes:"
    git status --short
    read -p "Commit changes before deploying? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Deploy $(date)"
    fi
fi

echo "📦 Preparing for deployment..."

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm run build
cd ..

# Check if build was successful
if [ ! -d "frontend/dist" ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend built successfully!"

# Push to git
echo "📤 Pushing to git..."
git add .
git commit -m "Deploy $(date)" --allow-empty
git push origin main

echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Deploy backend to Railway: https://railway.app"
echo "2. Deploy frontend to Vercel: https://vercel.com"
echo "3. Set environment variables (see DEPLOYMENT.md)"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions" 