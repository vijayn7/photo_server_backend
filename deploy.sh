#!/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH

echo "[DEPLOY] Pulling latest code..." >> /home/vnannapu/deploy.log

cd /home/vnannapu/photo-server || exit 1

# Pull the latest code
git pull origin main >> /home/vnannapu/deploy.log 2>&1

# Install dependencies
pip install -r requirements.txt >> /home/vnannapu/deploy.log 2>&1

# Restart the FastAPI server (assuming it's run by systemd)
echo "[DEPLOY] Restarting FastAPI service..." >> /home/vnannapu/deploy.log
sudo systemctl restart fastapi.service

# Test and reload Nginx configuration
echo "[DEPLOY] Testing and reloading Nginx configuration..." >> /home/vnannapu/deploy.log

bash /scripts/nginx-reload.sh >> /home/vnannapu/deploy.log 2>&1
if [ $? -eq 0 ]; then
  echo "[DEPLOY] Deployment completed successfully." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] Deployment failed. Check the logs for details." >> /home/vnannapu/deploy.log
fi

# Optional: Check if FastAPI service is running
if systemctl is-active --quiet fastapi.service; then
  echo "[DEPLOY] FastAPI service is running." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] Warning: FastAPI service is not running! Attempting to start..." >> /home/vnannapu/deploy.log
  sudo systemctl start fastapi.service
fi

# Optional: Check if Nginx is running
if systemctl is-active --quiet nginx; then
  echo "[DEPLOY] Nginx is running." >> /home/vnannapu/deploy.log
else
  echo "[DEPLOY] Warning: Nginx is not running! Attempting to start..." >> /home/vnannapu/deploy.log
  sudo systemctl start nginx
fi

# Log completion
echo "[DEPLOY] Deployment script completed." >> /home/vnannapu/deploy.log
# Exit with success status
exit 0
# End of deploy.sh