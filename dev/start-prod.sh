#!/bin/bash

# Start production server for React + FastAPI Photo Server
# This serves the built React app through FastAPI on port 8000

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting Photo Server Production Mode"
echo "======================================="

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

# Start FastAPI server
echo "🔧 Starting FastAPI server with React build on http://localhost:8000"
echo "📱 React app will be served from http://localhost:8000"
echo "🔌 API endpoints available at http://localhost:8000/api/*"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
