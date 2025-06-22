#!/bin/bash

# Development server for React + FastAPI photo server
# This runs React dev server (hot reload) + FastAPI server

set -e  # Exit on any error

echo "=== Photo Server Development Mode ==="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the project root directory."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "Checking dependencies..."

if ! command_exists python3; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "Error: Node.js is required but not installed."
    exit 1
fi

echo "✓ Dependencies verified"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating Python virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install React dependencies
if [ -d "frontend" ]; then
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install
    fi
    cd ..
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file with default settings..."
    cat > .env << EOL
# Environment variables for Photo Server Backend
PHOTO_SERVER_ADMIN=admin
PHOTO_SERVER_ADMIN_PASSWORD=admin_password

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "your-secret-key-change-this")
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database configuration
DB_PATH=./data/photos.db
EOL
    echo "✓ Created .env file"
fi

# Create data directory if it doesn't exist
mkdir -p data

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Shutting down servers..."
    if [ ! -z "$FASTAPI_PID" ]; then
        kill $FASTAPI_PID 2>/dev/null || true
    fi
    if [ ! -z "$REACT_PID" ]; then
        kill $REACT_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "=== Starting Development Servers ==="
echo "FastAPI server: http://localhost:8000"
echo "React dev server: http://localhost:3000"
echo "Press Ctrl+C to stop both servers"
echo ""

# Start FastAPI server in background
echo "Starting FastAPI server..."
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
FASTAPI_PID=$!

# Give FastAPI time to start
sleep 3

# Start React dev server in background
echo "Starting React development server..."
cd frontend
npm start &
REACT_PID=$!
cd ..

# Wait for user to stop the servers
wait
