#!/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH

# Create/overwrite the log file with a timestamp header
echo "[DEPLOY] Starting deployment at $(date)" > /home/vnannapu/deploy.log

cd /home/vnannapu/photo-server || exit 1

# Pull the latest code
echo "[DEPLOY] Pulling latest code..." >> /home/vnannapu/deploy.log
git pull origin main >> /home/vnannapu/deploy.log 2>&1

# Use a python virtual environment
echo "[DEPLOY] Setting up Python virtual environment..." >> /home/vnannapu/deploy.log
python3 -m venv venv
source venv/bin/activate
echo "[DEPLOY] Activated virtual environment." >> /home/vnannapu/deploy.log

# Install dependencies
echo "[DEPLOY] Installing dependencies..." >> /home/vnannapu/deploy.log
pip install -r requirements.txt
echo "[DEPLOY] Dependencies installed." >> /home/vnannapu/deploy.log

# Ensure .env file exists with proper settings
echo "[DEPLOY] Checking .env file..." >> /home/vnannapu/deploy.log
if [ ! -f .env ]; then
    echo "[DEPLOY] Creating .env file with default settings" >> /home/vnannapu/deploy.log
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
    echo "[DEPLOY] Created .env file with secure settings" >> /home/vnannapu/deploy.log
else
    echo "[DEPLOY] .env file exists, checking required variables" >> /home/vnannapu/deploy.log
    
    # Ensure PHOTO_SERVER_ADMIN_PASSWORD is set
    if ! grep -q "PHOTO_SERVER_ADMIN_PASSWORD" .env; then
        echo "[DEPLOY] Adding PHOTO_SERVER_ADMIN_PASSWORD to .env" >> /home/vnannapu/deploy.log
        echo "PHOTO_SERVER_ADMIN_PASSWORD=admin_password" >> .env
    fi
    
    # Ensure SECRET_KEY is set
    if ! grep -q "SECRET_KEY" .env; then
        echo "[DEPLOY] Adding SECRET_KEY to .env" >> /home/vnannapu/deploy.log
        echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    fi
fi


# Test and reload Nginx configuration
echo "[DEPLOY] Testing and reloading Nginx configuration..." >> /home/vnannapu/deploy.log

bash ~/photo-server/scripts/nginx-reload.sh >> /home/vnannapu/deploy.log 2>&1
if [ $? -eq 0 ]; then
  echo "[DEPLOY] Deployment completed successfully." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] Deployment failed. Check the logs for details." >> /home/vnannapu/deploy.log
fi

# Copy the updated photo-server service file to correct location
echo "[DEPLOY] Copying updated photo-server.service file..." >> /home/vnannapu/deploy.log
sudo cp /home/vnannapu/photo-server/services/photo-server.service /etc/systemd/system/photo-server.service
sudo chmod 644 /etc/systemd/system/photo-server.service
sudo systemctl daemon-reload

# Check if photo-server is running
echo "[DEPLOY] Restarting photo-server..." >> /home/vnannapu/deploy.log
sudo systemctl restart photo-server.service

# Verify the service status with detailed log output
echo "[DEPLOY] Checking photo-server service status..." >> /home/vnannapu/deploy.log
sudo systemctl status photo-server.service >> /home/vnannapu/deploy.log 2>&1
if systemctl is-active --quiet photo-server.service; then
  echo "[DEPLOY] photo-server is running successfully." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] ERROR: photo-server failed to start! Check journal logs." >> /home/vnannapu/deploy.log
  sudo journalctl -u photo-server.service --no-pager -n 50 >> /home/vnannapu/deploy.log 2>&1
fi

# Log completion
echo "[DEPLOY] Deployment script completed." >> /home/vnannapu/deploy.log
# Exit with success status
exit 0
# End of deploy.sh