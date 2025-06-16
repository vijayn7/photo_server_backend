#!/bin/bash
# Script to test and apply Nginx configuration changes

echo "=== Nginx Configuration Test ==="

# Check if we're running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root to test and reload Nginx configuration."
    exit 1
fi

# Copy our configuration to Nginx sites-available
echo "Copying configuration file..."
cp /home/vnannapu/photo-server/sites_available/default /etc/nginx/sites-available/

# Check if symlink exists, create if it doesn't
if [ ! -L /etc/nginx/sites-enabled/default ]; then
    echo "Creating symlink in sites-enabled..."
    ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
fi

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx configuration test passed!"
    
    # Reload Nginx
    echo "Reloading Nginx..."
    systemctl reload nginx
    
    echo "Nginx configuration has been updated successfully!"
else
    echo "Nginx configuration test failed. Please check the errors above."
    exit 1
fi

# Display Nginx status
echo ""
echo "=== Nginx Status ==="
systemctl status nginx

echo ""
echo "=== Upload File Size Settings ==="
echo "Current client_max_body_size settings in Nginx:"
grep -r "client_max_body_size" /etc/nginx/
