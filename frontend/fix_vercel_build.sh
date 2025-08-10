#!/bin/bash

echo "Fixing Vercel build issue..."

# Clean everything
echo "Cleaning previous build artifacts..."
rm -rf dist node_modules package-lock.json

# Install dependencies with clean slate
echo "Installing dependencies..."
npm install --legacy-peer-deps

# Verify terser is installed
echo "Verifying terser installation..."
npm list terser

# Test build
echo "Testing build process..."
npm run build

echo "Build test completed!"
