#!/bin/bash
set -e  # Exit on any error
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH

# Configuration
DEPLOY_USER="vnannapu"
DEPLOY_DIR="/home/${DEPLOY_USER}/photo-server"
LOG_FILE="/home/${DEPLOY_USER}/deploy.log"
SERVICE_NAME="photo-server"
REQUIRED_DIRS=("photos" "photos/global" "data" "thumbnails")

# Helper function to log with timestamp
log() {
    echo "[DEPLOY $(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Helper function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        log "✅ $1 completed successfully"
    else
        log "❌ ERROR: $1 failed"
        exit 1
    fi
}

# Create/overwrite the log file with a timestamp header
log "🚀 Starting deployment"
log "📁 Deploying to: $DEPLOY_DIR"

# Ensure we're in the correct directory
if [ ! -d "$DEPLOY_DIR" ]; then
    log "❌ ERROR: Deploy directory $DEPLOY_DIR does not exist!"
    exit 1
fi

cd "$DEPLOY_DIR"
log "📂 Changed to deployment directory: $(pwd)"

# Step 1: Pull the latest code
log "📥 Pulling latest code from repository..."
if [ -d ".git" ]; then
    git fetch origin >> "$LOG_FILE" 2>&1
    git reset --hard origin/main >> "$LOG_FILE" 2>&1
    check_success "Git pull"
else
    log "⚠️  WARNING: Not a git repository. Skipping git pull."
fi

# Step 2: Create required directories
log "📁 Creating required directories..."
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log "📁 Created directory: $dir"
    fi
    
    # Set proper permissions
    chmod 755 "$dir"
    if [ "$dir" = "photos" ] || [[ "$dir" == photos/* ]]; then
        chmod 777 "$dir"  # Photos directories need write access
    fi
done
check_success "Directory creation"

# Step 3: Set up Python virtual environment
log "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv >> "$LOG_FILE" 2>&1
    check_success "Virtual environment creation"
else
    log "🐍 Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
check_success "Virtual environment activation"

# Upgrade pip to latest version
log "⬆️  Upgrading pip..."
pip install --upgrade pip >> "$LOG_FILE" 2>&1
check_success "Pip upgrade"

# Step 4: Install Python dependencies
log "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt >> "$LOG_FILE" 2>&1
    check_success "Python dependencies installation"
else
    log "⚠️  WARNING: requirements.txt not found"
fi

# Step 5: Check and install Node.js if needed
log "🟢 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    log "📥 Node.js not found. Installing Node.js..."
    
    # Detect OS and install accordingly
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - >> "$LOG_FILE" 2>&1
        sudo apt-get install -y nodejs >> "$LOG_FILE" 2>&1
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash - >> "$LOG_FILE" 2>&1
        sudo yum install -y nodejs >> "$LOG_FILE" 2>&1
    else
        log "❌ ERROR: Cannot install Node.js automatically. Please install manually."
        exit 1
    fi
    check_success "Node.js installation"
else
    log "🟢 Node.js already installed: $(node --version)"
fi

# Verify npm is available
if ! command -v npm &> /dev/null; then
    log "❌ ERROR: npm not found after Node.js installation"
    exit 1
fi
log "📦 npm version: $(npm --version)"

# Step 6: Build React frontend
log "⚛️  Building React frontend..."
if [ -d "frontend" ]; then
    cd frontend
    
    # Verify package.json exists
    if [ ! -f "package.json" ]; then
        log "❌ ERROR: package.json not found in frontend directory"
        exit 1
    fi
    
    # Clean any previous builds and cache
    log "🧹 Cleaning previous React build..."
    rm -rf build/ node_modules/.cache/ >> "$LOG_FILE" 2>&1
    
    # Install npm dependencies
    log "📦 Installing npm dependencies..."
    npm ci --production=false >> "$LOG_FILE" 2>&1
    check_success "npm dependencies installation"
    
    # Build the React app
    log "🔨 Building React app..."
    npm run build >> "$LOG_FILE" 2>&1
    check_success "React build"
    
    # Verify build directory exists and has content
    if [ -d "build" ] && [ "$(ls -A build 2>/dev/null)" ]; then
        log "✅ React build verified - files found in build directory"
        
        # List some key build files for verification
        log "📄 Build contents:"
        ls -la build/ >> "$LOG_FILE" 2>&1
        if [ -f "build/index.html" ]; then
            log "✅ index.html found in build"
        else
            log "⚠️  WARNING: index.html not found in build directory"
        fi
    else
        log "❌ ERROR: React build directory is empty or missing!"
        exit 1
    fi
    
    cd ..
else
    log "⚠️  WARNING: frontend directory not found. Skipping React build."
fi

# Step 7: Configure environment variables
log "⚙️  Configuring environment variables..."
if [ ! -f ".env" ]; then
    log "📝 Creating .env file with default settings"
    cat > .env << 'EOL'
# Environment variables for Photo Server Backend
PHOTO_SERVER_ADMIN=vijayn7
PHOTO_SERVER_ADMIN_PASSWORD=admin_password

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database configuration
DB_PATH=./data/users.json

# Photo storage (production paths)
PHOTOS_PATH=./photos
THUMBNAILS_PATH=./thumbnails

# Production mode
ENVIRONMENT=production
EOL
    # Replace the SECRET_KEY placeholder with actual random key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/SECRET_KEY=\$(openssl rand -hex 32)/SECRET_KEY=$SECRET_KEY/" .env
    
    check_success ".env file creation"
else
    log "⚙️  .env file exists, checking required variables"
    
    # Ensure all required variables are set
    required_vars=("PHOTO_SERVER_ADMIN_PASSWORD" "SECRET_KEY" "DB_PATH" "PHOTOS_PATH")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env; then
            case $var in
                "PHOTO_SERVER_ADMIN_PASSWORD")
                    echo "PHOTO_SERVER_ADMIN_PASSWORD=admin_password" >> .env
                    log "➕ Added $var to .env"
                    ;;
                "SECRET_KEY")
                    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
                    log "➕ Added $var to .env"
                    ;;
                "DB_PATH")
                    echo "DB_PATH=./data/users.json" >> .env
                    log "➕ Added $var to .env"
                    ;;
                "PHOTOS_PATH")
                    echo "PHOTOS_PATH=./photos" >> .env
                    log "➕ Added $var to .env"
                    ;;
            esac
        fi
    done
fi

# Ensure .env has proper permissions
chmod 600 .env
check_success "Environment configuration"

# Step 8: Set up systemd service
log "🔧 Setting up systemd service..."
if [ -f "services/photo-server.service" ]; then
    # Copy the updated service file
    sudo cp "services/photo-server.service" "/etc/systemd/system/photo-server.service"
    sudo chmod 644 "/etc/systemd/system/photo-server.service"
    sudo systemctl daemon-reload
    check_success "Systemd service configuration"
else
    log "⚠️  WARNING: services/photo-server.service not found"
fi

# Step 9: Test application before deployment
log "🧪 Testing application configuration..."

# Test that main.py can be imported
log "🐍 Testing Python application..."
if python3 -c "import main" >> "$LOG_FILE" 2>&1; then
    log "✅ Python application loads successfully"
else
    log "❌ ERROR: Python application failed to load"
    python3 -c "import main" 2>&1 | tail -10 >> "$LOG_FILE"
    exit 1
fi

# Verify React build exists if we're using React
if [ -d "frontend/build" ] && [ ! -f "frontend/build/index.html" ]; then
    log "❌ ERROR: React build exists but index.html is missing"
    exit 1
fi

# Step 10: Handle Nginx configuration (if present)
log "🌐 Checking Nginx configuration..."
if [ -f "scripts/nginx-reload.sh" ]; then
    log "🔄 Reloading Nginx configuration..."
    bash scripts/nginx-reload.sh >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log "✅ Nginx configuration reloaded successfully"
    else
        log "⚠️  WARNING: Nginx reload failed, continuing with deployment"
    fi
else
    log "ℹ️  No Nginx reload script found, skipping"
fi

# Step 11: Stop existing service gracefully
log "🛑 Stopping existing service..."
if systemctl is-active --quiet "$SERVICE_NAME.service"; then
    sudo systemctl stop "$SERVICE_NAME.service"
    
    # Wait for service to stop completely
    timeout=30
    while [ $timeout -gt 0 ] && systemctl is-active --quiet "$SERVICE_NAME.service"; do
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if systemctl is-active --quiet "$SERVICE_NAME.service"; then
        log "⚠️  WARNING: Service did not stop gracefully, forcing stop"
        sudo systemctl kill "$SERVICE_NAME.service"
        sleep 2
    fi
    
    log "🛑 Service stopped successfully"
else
    log "ℹ️  Service was not running"
fi

# Step 12: Start the service
log "🚀 Starting photo-server service..."

# Final verification before starting
if [ -d "frontend" ] && [ ! -d "frontend/build" ]; then
    log "❌ ERROR: React build not found! Service cannot start without frontend build."
    exit 1
fi

# Enable and start the service
sudo systemctl enable "$SERVICE_NAME.service" >> "$LOG_FILE" 2>&1
sudo systemctl start "$SERVICE_NAME.service"

# Wait a moment for service to start
sleep 3

# Step 13: Verify deployment
log "✅ Verifying deployment..."
sudo systemctl status "$SERVICE_NAME.service" --no-pager >> "$LOG_FILE" 2>&1

if systemctl is-active --quiet "$SERVICE_NAME.service"; then
    log "🎉 photo-server is running successfully!"
    
    # Get service details
    SERVICE_PORT=$(grep -o 'port [0-9]*' "/etc/systemd/system/$SERVICE_NAME.service" | grep -o '[0-9]*' || echo "8000")
    log "🌐 Service is running on port: $SERVICE_PORT"
    
    # Test if the service responds
    log "🔍 Testing service response..."
    sleep 2  # Give service time to fully start
    
    if curl -f -s "http://localhost:$SERVICE_PORT/" > /dev/null 2>&1; then
        log "✅ Service is responding to HTTP requests"
    else
        log "⚠️  WARNING: Service is running but not responding to HTTP requests yet"
        log "ℹ️  This might be normal if the service is still starting up"
    fi
    
    # Show recent logs
    log "📄 Recent service logs:"
    sudo journalctl -u "$SERVICE_NAME.service" --no-pager -n 10 --since "1 minute ago" >> "$LOG_FILE" 2>&1
    
else
    log "❌ ERROR: photo-server failed to start!"
    log "📄 Checking service logs..."
    sudo journalctl -u "$SERVICE_NAME.service" --no-pager -n 50 >> "$LOG_FILE" 2>&1
    
    log "🔍 Checking for common issues..."
    if [ ! -f "main.py" ]; then
        log "❌ main.py not found in $DEPLOY_DIR"
    fi
    if [ ! -d "venv" ]; then
        log "❌ Virtual environment not found"
    fi
    if [ ! -f ".env" ]; then
        log "❌ .env file not found"
    fi
    
    exit 1
fi

# Step 14: Cleanup and final tasks
log "🧹 Performing cleanup..."

# Clean up old build artifacts if present
if [ -d "frontend/node_modules/.cache" ]; then
    rm -rf frontend/node_modules/.cache
    log "🗑️  Cleaned npm cache"
fi

# Set final permissions
chmod +x "$0"  # Ensure deploy script remains executable

# Final success message
log "🎉 Deployment completed successfully!"
log "📊 Deployment Summary:"
log "   📁 Deploy directory: $DEPLOY_DIR"
log "   🐍 Python virtual environment: $(which python3)"
log "   ⚛️  React build: $([ -d "frontend/build" ] && echo "✅ Present" || echo "❌ Missing")"
log "   🔧 Service status: $(systemctl is-active "$SERVICE_NAME.service")"
log "   📝 Log file: $LOG_FILE"

exit 0