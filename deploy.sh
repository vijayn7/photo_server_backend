#!/bin/bash

echo "[DEPLOY] Pulling latest code..." >> /home/vnannapu/deploy.log

cd /home/vnannapu/photo-server || exit 1

# Pull the latest code
git pull origin main >> /home/vnannapu/deploy.log 2>&1

# (Optional) Install dependencies
# pip install -r requirements.txt >> /home/vnannapu/deploy.log 2>&1

# Restart the FastAPI server (assuming it's run by systemd)
echo "[DEPLOY] Restarting FastAPI service..." >> /home/vnannapu/deploy.log
sudo systemctl restart fastapi.service

# Test and reload Nginx configuration
echo "[DEPLOY] Testing and reloading Nginx configuration..." >> /home/vnannapu/deploy.log

# Test Nginx configuration
nginx_test=$(sudo nginx -t 2>&1)
if [[ $? -eq 0 ]]; then
    echo "[DEPLOY] Nginx configuration test passed, reloading..." >> /home/vnannapu/deploy.log
    sudo systemctl reload nginx >> /home/vnannapu/deploy.log 2>&1
    echo "[DEPLOY] Nginx reloaded successfully" >> /home/vnannapu/deploy.log
else
    echo "[DEPLOY] ERROR: Nginx configuration test failed:" >> /home/vnannapu/deploy.log
    echo "$nginx_test" >> /home/vnannapu/deploy.log
fi