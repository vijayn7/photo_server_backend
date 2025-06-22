#!/bin/bash

# Development deployment script for React + FastAPI Photo Server
# This script works on macOS and other development environments

set -e  # Exit on any error

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_DIR/dev/deploy.log"
PHOTOS_DIR="$PROJECT_DIR/photos"
THUMBNAILS_DIR="$PROJECT_DIR/thumbnails"

# Create log file
echo "[DEV-DEPLOY] Starting development deployment at $(date)" > "$LOG_FILE"
echo "Project directory: $PROJECT_DIR" >> "$LOG_FILE"

cd "$PROJECT_DIR"

# Create necessary directories for development
echo "[DEV-DEPLOY] Creating necessary directories..." >> "$LOG_FILE"
mkdir -p "$PHOTOS_DIR"
mkdir -p "$PHOTOS_DIR/global"
mkdir -p "$THUMBNAILS_DIR"
mkdir -p data
echo "[DEV-DEPLOY] Directories created: $PHOTOS_DIR, $THUMBNAILS_DIR, data" >> "$LOG_FILE"

# Check if Python 3 is available
echo "[DEV-DEPLOY] Checking Python installation..." >> "$LOG_FILE"
if ! command -v python3 &> /dev/null; then
    echo "[DEV-DEPLOY] ERROR: Python 3 not found! Please install Python 3." >> "$LOG_FILE"
    echo "ERROR: Python 3 not found! Please install Python 3."
    exit 1
fi
echo "[DEV-DEPLOY] Python 3 found: $(python3 --version)" >> "$LOG_FILE"

# Set up Python virtual environment
echo "[DEV-DEPLOY] Setting up Python virtual environment..." >> "$LOG_FILE"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[DEV-DEPLOY] Created new virtual environment." >> "$LOG_FILE"
else
    echo "[DEV-DEPLOY] Using existing virtual environment." >> "$LOG_FILE"
fi

# Activate virtual environment
source venv/bin/activate
echo "[DEV-DEPLOY] Activated virtual environment." >> "$LOG_FILE"

# Install Python dependencies
echo "[DEV-DEPLOY] Installing Python dependencies..." >> "$LOG_FILE"
pip install -r requirements.txt >> "$LOG_FILE" 2>&1
echo "[DEV-DEPLOY] Python dependencies installed." >> "$LOG_FILE"

# Check if Node.js is installed
echo "[DEV-DEPLOY] Checking Node.js installation..." >> "$LOG_FILE"
if ! command -v node &> /dev/null; then
    echo "[DEV-DEPLOY] ERROR: Node.js not found!" >> "$LOG_FILE"
    echo "ERROR: Node.js not found! Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo "[DEV-DEPLOY] Node.js found: $(node --version)" >> "$LOG_FILE"
echo "[DEV-DEPLOY] npm version: $(npm --version)" >> "$LOG_FILE"

# Build React frontend
echo "[DEV-DEPLOY] Building React frontend..." >> "$LOG_FILE"
if [ -d "frontend" ]; then
    cd frontend
    
    # Install npm dependencies
    echo "[DEV-DEPLOY] Installing npm dependencies..." >> "$LOG_FILE"
    npm install >> "$LOG_FILE" 2>&1
    
    # Build the React app
    echo "[DEV-DEPLOY] Building React app..." >> "$LOG_FILE"
    npm run build >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[DEV-DEPLOY] React build completed successfully." >> "$LOG_FILE"
        echo "✅ React build completed successfully."
    else
        echo "[DEV-DEPLOY] ERROR: React build failed!" >> "$LOG_FILE"
        echo "❌ ERROR: React build failed! Check $LOG_FILE for details."
        exit 1
    fi
    
    cd ..
else
    echo "[DEV-DEPLOY] ERROR: frontend directory not found!" >> "$LOG_FILE"
    echo "❌ ERROR: frontend directory not found!"
    exit 1
fi

# Create development .env file
echo "[DEV-DEPLOY] Setting up development environment variables..." >> "$LOG_FILE"
if [ ! -f .env ]; then
    echo "[DEV-DEPLOY] Creating .env file with development settings" >> "$LOG_FILE"
    cat > .env << EOL
# Development Environment Variables for Photo Server Backend
PHOTO_SERVER_ADMIN=admin
PHOTO_SERVER_ADMIN_PASSWORD=admin

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database configuration (development)
DB_PATH=$PROJECT_DIR/data/users.json

# Photo storage (development - local directories)
PHOTOS_PATH=$PHOTOS_DIR
THUMBNAILS_PATH=$THUMBNAILS_DIR

# Development mode
ENVIRONMENT=development
EOL
    echo "[DEV-DEPLOY] Created .env file with development settings" >> "$LOG_FILE"
    echo "✅ Created .env file with development settings"
else
    echo "[DEV-DEPLOY] .env file already exists" >> "$LOG_FILE"
    echo "ℹ️  .env file already exists"
fi

# Verify React build exists
if [ ! -d "frontend/build" ]; then
    echo "[DEV-DEPLOY] ERROR: React build not found!" >> "$LOG_FILE"
    echo "❌ ERROR: React build not found!"
    exit 1
fi

echo "[DEV-DEPLOY] Development deployment completed successfully." >> "$LOG_FILE"
echo "✅ Development deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Start the development server: ./dev/start-dev.sh"
echo "2. Or start production server: ./dev/start-prod.sh"
echo "3. View logs: tail -f $LOG_FILE"
echo ""

exit 0
