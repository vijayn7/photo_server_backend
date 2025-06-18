#!/bin/bash
# Script to diagnose and fix environment variable issues in photo server

echo "===== Photo Server Environment Diagnosis ====="
echo "Starting diagnosis at $(date)"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: This script must be run from the photo_server_backend directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "1. Checking for .env file"
if [ -f ".env" ]; then
    echo "✓ .env file exists"
    echo "Content of .env file (sensitive values redacted):"
    grep -v "PASSWORD\|KEY" .env | sed 's/^/  /'
    echo "  PASSWORD/KEY values exist: $(grep -E 'PASSWORD|KEY' .env | wc -l) occurrences"
else
    echo "✗ .env file not found. Creating one with default values..."
    cat > .env << EOL
# Environment variables for Photo Server Backend
PHOTO_SERVER_ADMIN=vijayn7
PHOTO_SERVER_ADMIN_PASSWORD=admin_password

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database configuration
DB_PATH=./data/photos.db
EOL
    echo "✓ Created .env file with default settings"
fi

echo -e "\n2. Checking Python environment"
# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "✗ Python not found. Please install Python 3."
    exit 1
fi

echo "✓ Using Python: $($PYTHON_CMD --version)"

# Check for required packages
echo "Checking for required Python packages:"
required_packages=("fastapi" "passlib" "pyjwt" "uvicorn")
missing_packages=()

for package in "${required_packages[@]}"; do
    if ! $PYTHON_CMD -c "import $package" &> /dev/null; then
        echo "✗ Missing package: $package"
        missing_packages+=("$package")
    else
        echo "✓ Package found: $package"
    fi
done

if [ ${#missing_packages[@]} -gt 0 ]; then
    echo -e "\nMissing packages. Would you like to install them? (y/n)"
    read -r install_packages
    if [[ "$install_packages" =~ ^[Yy]$ ]]; then
        echo "Installing missing packages..."
        for package in "${missing_packages[@]}"; do
            $PYTHON_CMD -m pip install "$package"
        done
    fi
fi

echo -e "\n3. Checking users database"
if [ -f "python/users.json" ]; then
    echo "✓ users.json exists"
    echo "Users in database: $($PYTHON_CMD -c "import json; print(len(json.load(open('python/users.json'))))")"
else
    echo "✗ users.json not found"
fi

echo -e "\n4. Testing db_utils.py functionality"

# Create a temporary test script
cat > /tmp/test_db_utils.py << EOL
import sys
import os
sys.path.append(os.path.abspath("."))
from python import db_utils

print("Environment variables:")
print(f"ADMIN_USERNAME: '{db_utils.ADMIN_USERNAME}'")
print(f"ADMIN_PASSWORD set: {'Yes' if db_utils.ADMIN_PASSWORD else 'No'}")

# Test password hashing
try:
    hashed = db_utils.pwd_context.hash("test_password")
    print("✓ Password hashing works")
except Exception as e:
    print(f"✗ Password hashing failed: {str(e)}")

# Test user authentication
if os.path.exists(db_utils.USERS_FILE):
    user = db_utils.authenticate_user(db_utils.ADMIN_USERNAME, db_utils.ADMIN_PASSWORD)
    if user:
        print(f"✓ Authentication works for admin user")
    else:
        print(f"✗ Authentication failed for admin user")
else:
    print("✗ users.json not found, can't test authentication")
EOL

echo "Running test script..."
$PYTHON_CMD /tmp/test_db_utils.py
rm /tmp/test_db_utils.py

echo -e "\n5. Checking for systemd service"
if command -v systemctl &> /dev/null; then
    if systemctl list-unit-files | grep -q photo-api; then
        echo "✓ photo-api.service exists"
        echo "Service status:"
        systemctl status photo-api.service | head -n 3
    else
        echo "✗ photo-api.service not found"
    fi
else
    echo "✗ systemctl not found (not running on systemd)"
fi

echo -e "\n===== Diagnosis Complete ====="
echo "Based on the diagnosis, would you like to:"
echo "1. Create a fresh users database (will delete existing users)"
echo "2. Update admin credentials"
echo "3. Restart the service"
echo "4. Exit"

read -r choice

case $choice in
    1)
        echo "Creating fresh users database..."
        if [ -f python/users.json ]; then
            mv python/users.json python/users.json.bak.$(date +%Y%m%d%H%M%S)
        fi
        $PYTHON_CMD -c "import sys; import os; sys.path.append('python'); import db_utils; db_utils.load_users()"
        echo "✓ Created fresh users database"
        ;;
    2)
        echo "Updating admin credentials in .env file..."
        read -p "Enter admin username (default: vijayn7): " new_username
        new_username=${new_username:-vijayn7}
        
        read -sp "Enter admin password: " new_password
        echo
        
        # Update .env file
        sed -i.bak "s/^PHOTO_SERVER_ADMIN=.*/PHOTO_SERVER_ADMIN=$new_username/" .env
        sed -i.bak "s/^PHOTO_SERVER_ADMIN_PASSWORD=.*/PHOTO_SERVER_ADMIN_PASSWORD=$new_password/" .env
        
        echo "✓ Updated admin credentials in .env file"
        ;;
    3)
        if command -v systemctl &> /dev/null; then
            echo "Restarting photo-api.service..."
            sudo systemctl restart photo-api.service
            echo "✓ Service restarted"
        else
            echo "Restarting using start_server.sh..."
            ./start_server.sh &
            echo "✓ Server restarted"
        fi
        ;;
    *)
        echo "Exiting."
        ;;
esac

echo "Done."
