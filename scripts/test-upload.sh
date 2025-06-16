#!/bin/bash
# Script to test large file uploads to the FastAPI server

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TEST_FILE="/tmp/test_upload.dat"
SIZE_MB=30  # Size in MB for the test file
URL="https://nannapuraju.xyz/upload"  # Change to match your server URL
TOKEN=""     # Add your authentication token here if needed

echo -e "${YELLOW}=== Large File Upload Test ===${NC}"
echo -e "Testing upload of a ${SIZE_MB}MB file to $URL"

# Create a test file of specified size
echo -e "\n${YELLOW}Creating test file of ${SIZE_MB}MB...${NC}"
dd if=/dev/urandom of=$TEST_FILE bs=1M count=$SIZE_MB

# Get the actual file size
ACTUAL_SIZE=$(du -h $TEST_FILE | cut -f1)

echo -e "Test file created: $TEST_FILE ($ACTUAL_SIZE)"

# Test upload with curl, with detailed error information
echo -e "\n${YELLOW}Uploading test file...${NC}"

# Check if we have a token
HEADERS=""
if [ ! -z "$TOKEN" ]; then
    HEADERS="-H \"Authorization: Bearer $TOKEN\""
fi

echo "Command: curl -v -X POST -F \"file=@$TEST_FILE\" $HEADERS $URL"

# Create form data for curl
curl -v -X POST \
  -F "file=@$TEST_FILE" \
  ${TOKEN:+-H "Authorization: Bearer $TOKEN"} \
  $URL 2>&1 | tee /tmp/upload_result.log

# Check the result
if grep -q "HTTP/.*2.." /tmp/upload_result.log; then
    echo -e "\n${GREEN}Success! The server accepted the ${SIZE_MB}MB file.${NC}"
else
    echo -e "\n${RED}Failed! The server rejected the ${SIZE_MB}MB file.${NC}"
    
    # Look for common errors
    if grep -q "413" /tmp/upload_result.log; then
        echo -e "${RED}Error 413: Request Entity Too Large${NC}"
        echo "This suggests Nginx or FastAPI is limiting the upload size."
        echo -e "${YELLOW}Troubleshooting steps:${NC}"
        echo "1. Check Nginx configuration: client_max_body_size directive should be set to a large value"
        echo "2. Verify Nginx configuration is loaded: sudo nginx -t"
        echo "3. Reload Nginx: sudo systemctl reload nginx"
        echo "4. Check FastAPI service configuration for any size limits"
        echo "5. Restart the FastAPI service: sudo systemctl restart photo-server"
    fi
    
    # Look for other error codes
    ERROR_CODE=$(grep -oE "HTTP/[0-9.]+ ([0-9]+)" /tmp/upload_result.log | grep -oE "[0-9]{3}")
    if [ ! -z "$ERROR_CODE" ] && [ "$ERROR_CODE" != "413" ]; then
        echo -e "${RED}Error $ERROR_CODE detected${NC}"
        grep -A 5 "$ERROR_CODE" /tmp/upload_result.log
    fi
fi

# Clean up
echo -e "\n${YELLOW}Cleaning up test file...${NC}"
rm $TEST_FILE

echo -e "\n${YELLOW}=== Test Completed ===${NC}"
