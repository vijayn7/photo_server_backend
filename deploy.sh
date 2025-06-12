#!/bin/bash

cd /home/pi/photo-server  # change to your actual project path

echo "Pulling latest code from GitHub..."
git pull origin main

echo "Restarting the FastAPI server..."
sudo systemctl restart photo-server