#!/bin/bash
# Troubleshooting script for photo-server service

echo "=== Photo Server Troubleshooting Tool ==="
echo "This script will help diagnose issues with the photo-server service"
echo

# Check if service is installed
if [ ! -f "/etc/systemd/system/photo-server.service" ]; then
    echo "ERROR: photo-server.service file not found in /etc/systemd/system/"
    echo "  Fix: Copy the service file with:"
    echo "  sudo cp ~/photo-server/services/photo-server.service /etc/systemd/system/"
    echo
else
    echo "✓ Service file exists"
    echo
fi

# Check service status
echo "=== Service Status ==="
sudo systemctl status photo-server.service
echo

# Check directory existence
if [ ! -d "/home/vnannapu/photo-server" ]; then
    echo "ERROR: Working directory /home/vnannapu/photo-server does not exist"
    echo "  Fix: Create the directory:"
    echo "  mkdir -p /home/vnannapu/photo-server"
    echo
else
    echo "✓ Working directory exists"
    echo
fi

# Check file existence
if [ ! -f "/home/vnannapu/photo-server/main.py" ]; then
    echo "ERROR: main.py not found in /home/vnannapu/photo-server"
    echo "  Fix: Copy project files to the working directory"
    echo
else
    echo "✓ main.py file exists"
    echo
fi

# Check virtual environment
if [ ! -d "/home/vnannapu/photo-server/venv" ]; then
    echo "ERROR: Python virtual environment not found"
    echo "  Fix: Create a virtual environment:"
    echo "  cd /home/vnannapu/photo-server && python3 -m venv venv"
    echo
else
    echo "✓ Python virtual environment exists"
    echo
fi

# Check if uvicorn is installed
if [ ! -f "/home/vnannapu/photo-server/venv/bin/uvicorn" ]; then
    echo "ERROR: uvicorn not found in virtual environment"
    echo "  Fix: Install dependencies in virtual environment:"
    echo "  cd /home/vnannapu/photo-server && source venv/bin/activate && pip install -r requirements.txt"
    echo
else
    echo "✓ uvicorn exists in virtual environment"
    echo
fi

# Check logs for errors
echo "=== Recent Service Logs ==="
sudo journalctl -u photo-server.service --no-pager -n 20
echo

# Check uploads directory permissions
if [ ! -d "/home/vnannapu/photo-server/uploads" ]; then
    echo "ERROR: uploads directory does not exist"
    echo "  Fix: Create the uploads directory:"
    echo "  mkdir -p /home/vnannapu/photo-server/uploads"
    echo "  sudo chown -R vnannapu:vnannapu /home/vnannapu/photo-server/uploads"
    echo
else
    echo "✓ uploads directory exists"
    # Check permissions
    UPLOAD_OWNER=$(stat -c '%U:%G' /home/vnannapu/photo-server/uploads)
    if [ "$UPLOAD_OWNER" != "vnannapu:vnannapu" ]; then
        echo "WARNING: uploads directory has incorrect ownership: $UPLOAD_OWNER"
        echo "  Fix: Set correct ownership:"
        echo "  sudo chown -R vnannapu:vnannapu /home/vnannapu/photo-server/uploads"
        echo
    else
        echo "✓ uploads directory has correct ownership"
        echo
    fi
fi

echo "=== Manual Startup Test ==="
echo "Try starting the service manually with:"
echo "cd /home/vnannapu/photo-server && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"
echo "This will show any Python errors directly in the console"
echo

echo "=== Troubleshooting Complete ==="
