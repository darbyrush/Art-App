#!/bin/bash

# Production Stop Script for Art Explorer

echo "Stopping Art Explorer services..."

# Kill backend processes
pkill -f "uvicorn main:app" || true

# Kill frontend processes
pkill -f "serve -s dist" || true

echo "All services stopped"
