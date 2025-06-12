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

