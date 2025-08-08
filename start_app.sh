#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting Art Explorer Application"
echo "=================================="

# Start backend in background
echo "Starting backend server..."
source venv/bin/activate
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend development server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
