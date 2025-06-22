#!/bin/bash

# Setup demo users for React Photo Server testing

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🔧 Setting up demo users for testing..."

# Create testadmin user
echo "Creating admin user..."
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin","first_name":"Admin","last_name":"User"}'
echo ""

# Create regular test user
echo "Creating regular user..."
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo","first_name":"Demo","last_name":"User"}'
echo ""

echo "✅ Demo users created!"
echo ""
echo "Login credentials:"
echo "Admin: admin / admin"
echo "User:  demo / demo"
echo ""
echo "Note: The admin user needs to be manually promoted to admin status in the database."
