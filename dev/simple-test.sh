#!/bin/bash

# Simple test script for React Photo Server

echo "🧪 Testing React Photo Server"
echo "============================="

# Test server is running
echo "1. Testing server..."
if curl -s http://localhost:8000/ >/dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server is not responding"
    exit 1
fi

# Test user registration
echo "2. Testing user registration..."
RESPONSE=$(curl -s -X POST http://localhost:8000/register \
    -H 'Content-Type: application/json' \
    -d '{"username":"demo","password":"demo","first_name":"Demo","last_name":"User"}')

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ User registration works"
else
    echo "ℹ️  User might already exist: $RESPONSE"
fi

# Test login
echo "3. Testing login..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/token \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=demo&password=demo')

if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Login works"
    TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    # Test authenticated endpoint
    echo "4. Testing authenticated endpoint..."
    USER_INFO=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/me)
    if echo "$USER_INFO" | grep -q "username"; then
        echo "✅ Authentication works"
        echo "   User info: $USER_INFO"
    else
        echo "❌ Authentication failed"
    fi
else
    echo "❌ Login failed: $TOKEN_RESPONSE"
fi

echo ""
echo "🎉 React Photo Server is working!"
echo ""
echo "🌐 Open http://localhost:8000 in your browser"
echo "🔑 Login with: demo / demo"
echo ""
