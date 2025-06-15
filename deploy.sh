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

# Restart the photo-api service (assuming it's run by systemd)
echo "[DEPLOY] Restarting photo-api service..." >> /home/vnannapu/deploy.log
sudo systemctl restart photo-api.service

# Test and reload Nginx configuration
echo "[DEPLOY] Testing and reloading Nginx configuration..." >> /home/vnannapu/deploy.log

bash ~/photo-server/scripts/nginx-reload.sh >> /home/vnannapu/deploy.log 2>&1
if [ $? -eq 0 ]; then
  echo "[DEPLOY] Deployment completed successfully." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] Deployment failed. Check the logs for details." >> /home/vnannapu/deploy.log
fi

# Optional: Check if photo-api service is running
if systemctl is-active --quiet photo-api.service; then
  echo "[DEPLOY] photo-api service is running." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] Warning: photo-api service is not running! Attempting to start..." >> /home/vnannapu/deploy.log
  sudo systemctl start photo-api.service
fi

# Optional: Check if photo-server is running
if systemctl is-active --quiet photo-server.service; then
  echo "[DEPLOY] photo-server is running." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] Warning: photo-server is not running! Attempting to start..." >> /home/vnannapu/deploy.log
  sudo systemctl start photo-server.service
fi

# Log completion
echo "[DEPLOY] Deployment script completed." >> /home/vnannapu/deploy.log
# Exit with success status
exit 0
# End of deploy.sh