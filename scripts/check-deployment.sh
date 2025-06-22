#!/bin/bash
# Deployment verification script

set -e
SERVICE_NAME="photo-server"
DEPLOY_DIR="/home/vnannapu/photo-server"

echo "🔍 Checking Photo Server Deployment"
echo "=================================="

# Check if service is running
echo -n "Service Status: "
if systemctl is-active --quiet "$SERVICE_NAME.service"; then
    echo "✅ Running"
else
    echo "❌ Not Running"
    exit 1
fi

# Check service details
echo -n "Service Enabled: "
if systemctl is-enabled --quiet "$SERVICE_NAME.service"; then
    echo "✅ Yes"
else
    echo "⚠️  No"
fi

# Check if port is listening
PORT=$(grep -o 'port [0-9]*' "/etc/systemd/system/$SERVICE_NAME.service" | grep -o '[0-9]*' 2>/dev/null || echo "8000")
echo -n "Port $PORT Listening: "
if netstat -ln | grep -q ":$PORT "; then
    echo "✅ Yes"
else
    echo "❌ No"
fi

# Test HTTP response
echo -n "HTTP Response: "
if curl -f -s "http://localhost:$PORT/" > /dev/null 2>&1; then
    echo "✅ Responding"
else
    echo "❌ Not Responding"
fi

# Check key directories
echo -n "Deploy Directory: "
if [ -d "$DEPLOY_DIR" ]; then
    echo "✅ Exists"
else
    echo "❌ Missing"
fi

echo -n "Virtual Environment: "
if [ -d "$DEPLOY_DIR/venv" ]; then
    echo "✅ Exists"
else
    echo "❌ Missing"
fi

echo -n "React Build: "
if [ -d "$DEPLOY_DIR/frontend/build" ] && [ -f "$DEPLOY_DIR/frontend/build/index.html" ]; then
    echo "✅ Complete"
else
    echo "❌ Missing"
fi

echo -n "Environment File: "
if [ -f "$DEPLOY_DIR/.env" ]; then
    echo "✅ Present"
else
    echo "❌ Missing"
fi

echo -n "Photos Directory: "
if [ -d "$DEPLOY_DIR/photos" ]; then
    echo "✅ Exists ($(ls -1 "$DEPLOY_DIR/photos" 2>/dev/null | wc -l) items)"
else
    echo "❌ Missing"
fi

echo ""
echo "Recent Service Logs:"
echo "==================="
sudo journalctl -u "$SERVICE_NAME.service" --no-pager -n 5 --since "10 minutes ago"

echo ""
echo "✅ Deployment check completed"
