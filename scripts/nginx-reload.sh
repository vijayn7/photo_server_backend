#!/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration paths
AVAILABLE_PATH="/etc/nginx/sites-available/default"
ENABLED_PATH="/etc/nginx/sites-enabled/default"
INITAL_PATH="~/photo-server/sites_available/default"

echo -e "${YELLOW}Copying Config from Repo to Available Sites...${NC}"
sudo rm -f "$AVAILABLE_PATH"  # Remove any existing file
sudo cp "$INITIAL_PATH" "$AVAILABLE_PATH"

#check if the copy was successful
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Configuration copied successfully to $AVAILABLE_PATH.${NC}"
else
  echo -e "${RED}Failed to copy configuration. Please check the file path and permissions.${NC}"
  exit 1
fi

echo -e "${YELLOW}Ensuring symbolic link exists...${NC}"

# Check if the symbolic link exists
if [ ! -L "$ENABLED_PATH" ] || [ ! -e "$ENABLED_PATH" ]; then
  echo -e "${YELLOW}Creating symbolic link for the configuration...${NC}"
  sudo rm -f "$ENABLED_PATH"  # Remove any existing broken link or file
  sudo ln -s "$AVAILABLE_PATH" "$ENABLED_PATH"
  echo -e "${GREEN}Symbolic link created.${NC}"
else
  echo -e "${GREEN}Symbolic link already exists.${NC}"
fi

echo -e "${YELLOW}Testing Nginx configuration...${NC}"

# Test the configuration
sudo nginx -t

# Check if the test was successful
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Configuration test successful.${NC}"

  echo -e "${YELLOW}Reloading Photo-Server...${NC}"
  sudo systemctl reload photo-server.service

  # Check if reload was successful
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Photo-Server reloaded successfully!${NC}"

    # Optional: Check if Photo-Server is running
    if systemctl is-active --quiet photo-server.service; then
      echo -e "${GREEN}Photo-Server is running.${NC}"
    else
      echo -e "${RED}Warning: Photo-Server is not running!${NC}"
      echo -e "${YELLOW}Attempting to start Photo-Server...${NC}"
      sudo systemctl start photo-server.service
    fi
    
  else
    echo -e "${RED}Failed to reload Photo-Server. Please check the error messages above.${NC}"
  fi
  
else
  echo -e "${RED}Configuration test failed. Please fix the errors before reloading.${NC}"
fi

# Display current Photo-Server status
echo -e "${YELLOW}Current Photo-Server status:${NC}"
sudo systemctl status photo-server.service --no-pager | head -n 5