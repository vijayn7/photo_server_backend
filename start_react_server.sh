#!/bin/bash

# Build and run the React + FastAPI photo server

set -e  # Exit on any error

echo "=== Photo Server React + FastAPI Startup ==="

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
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command_exists npm; then
    echo "Error: npm is required but not installed."
    exit 1
fi

echo "✓ Python 3: $(python3 --version)"
echo "✓ Node.js: $(node --version)"
echo "✓ npm: $(npm --version)"

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

# Build React frontend
echo "Building React frontend..."
if [ -d "frontend" ]; then
    cd frontend
    
    # Check if node_modules exists, install if not
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install
    else
        echo "npm dependencies already installed."
    fi
    
    # Build the React app
    echo "Building React app for production..."
    npm run build
    
    if [ $? -eq 0 ]; then
        echo "✓ React build completed successfully."
    else
        echo "✗ React build failed!"
        exit 1
    fi
    
    cd ..
else
    echo "Warning: frontend directory not found!"
    exit 1
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
    echo "✓ Created .env file with default settings."
fi

# Create data directory if it doesn't exist
mkdir -p data

echo "=== Starting FastAPI server ==="
echo "Server will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
