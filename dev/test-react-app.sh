#!/bin/bash

# Comprehensive test script for React Photo Server
# Tests all API endpoints and functionality

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🧪 Testing React Photo Server API endpoints"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for testing
test_endpoint() {
    local description="$1"
    local expected_code="$2"
    local curl_cmd="$3"
    
    echo -n "Testing: $description... "
    
    # Execute curl and capture both output and status code
    HTTP_CODE=$(curl -s -o /tmp/test_response.json -w "%{http_code}" $curl_cmd)
    RESPONSE=$(cat /tmp/test_response.json 2>/dev/null || echo "")
    
    if [ "$HTTP_CODE" -eq "$expected_code" ]; then
        echo -e "${GREEN}PASS${NC} (HTTP $HTTP_CODE)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        if [ "$4" = "show" ]; then
            echo "Response: $RESPONSE"
        fi
    else
        echo -e "${RED}FAIL${NC} (Expected HTTP $expected_code, got $HTTP_CODE)"
        echo "Response: $RESPONSE"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Start testing
echo ""
echo "1. Testing user registration..."
test_endpoint "Register new user" 200 \
    "curl -X POST http://localhost:8000/register -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"password\":\"testpass\",\"first_name\":\"Test\",\"last_name\":\"User\"}'"

echo ""
echo "2. Testing user authentication..."
test_endpoint "User login" 200 \
    "curl -X POST http://localhost:8000/token -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=testuser&password=testpass'"

# Extract token for subsequent requests
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/token -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=testuser&password=testpass')
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}ERROR: Could not extract auth token${NC}"
    exit 1
fi

echo ""
echo "3. Testing authenticated endpoints..."
test_endpoint "Get current user info" 200 \
    "curl -H 'Authorization: Bearer $TOKEN' http://localhost:8000/me" show

test_endpoint "Get user photos" 200 \
    "curl -H 'Authorization: Bearer $TOKEN' http://localhost:8000/photos"

test_endpoint "Get global photos" 200 \
    "curl -H 'Authorization: Bearer $TOKEN' http://localhost:8000/photos/global"

echo ""
echo "4. Testing admin user creation..."
test_endpoint "Register admin user" 200 \
    "curl -X POST http://localhost:8000/register -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\",\"first_name\":\"Admin\",\"last_name\":\"User\"}'"

# Get admin token
ADMIN_TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/token -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin&password=admin')
ADMIN_TOKEN=$(echo $ADMIN_TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$ADMIN_TOKEN" ]; then
    test_endpoint "Admin user info" 200 \
        "curl -H 'Authorization: Bearer $ADMIN_TOKEN' http://localhost:8000/me"
fi

echo ""
echo "5. Testing error cases..."
test_endpoint "Invalid login" 401 \
    "curl -X POST http://localhost:8000/token -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=invalid&password=wrong'"

test_endpoint "Duplicate user registration" 400 \
    "curl -X POST http://localhost:8000/register -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"password\":\"newpass\",\"first_name\":\"New\",\"last_name\":\"User\"}'"

test_endpoint "Unauthorized access" 401 \
    "curl http://localhost:8000/me"

echo ""
echo "6. Testing React app serving..."
test_endpoint "React app root" 200 \
    "curl http://localhost:8000/"

test_endpoint "React static assets" 200 \
    "curl -I http://localhost:8000/static/js/main.6d9a8364.js"

echo ""
echo "🎯 Test Results Summary"
echo "======================"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "🚀 Your React Photo Server is working correctly!"
    echo ""
    echo "Next steps:"
    echo "• Visit http://localhost:8000 to use the app"
    echo "• Login with: testuser / testpass"
    echo "• Or admin: admin / admin"
    echo "• Upload some photos to test the full workflow"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Check the output above.${NC}"
    exit 1
fi

# Cleanup
rm -f /tmp/test_response.json
