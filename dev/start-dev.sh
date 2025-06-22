#!/bin/bash

# Start development servers for React + FastAPI Photo Server
# This runs React dev server on port 3000 and FastAPI on port 8000

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting Photo Server Development Environment"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./dev/deploy-dev.sh first."
    exit 1
fi

# Check if React build exists
if [ ! -d "frontend/build" ]; then
    echo "❌ React build not found. Run ./dev/deploy-dev.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Activated Python virtual environment"

# Create necessary directories
mkdir -p photos/global
mkdir -p thumbnails
mkdir -p data

echo "✅ Created/verified necessary directories"

# Start FastAPI server in background
echo "🔧 Starting FastAPI server on http://localhost:8000"
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
FASTAPI_PID=$!

# Give FastAPI a moment to start
sleep 2

# Check if FastAPI started successfully
if kill -0 $FASTAPI_PID 2>/dev/null; then
    echo "✅ FastAPI server started (PID: $FASTAPI_PID)"
else
    echo "❌ Failed to start FastAPI server"
    exit 1
fi

# Start React development server
echo "🔧 Starting React development server on http://localhost:3000"
cd frontend

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $FASTAPI_PID 2>/dev/null || true
    cd "$PROJECT_DIR"
    echo "✅ Cleanup complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start React dev server (this will block)
npm start

# This line should never be reached due to npm start blocking
# But if it does, cleanup
cleanup
