#!/bin/bash

echo "Cleaning previous build..."
rm -rf dist node_modules package-lock.json

echo "Installing dependencies..."
npm install

echo "Running build..."
npm run build

echo "Build completed successfully!"
ls -la dist/
