#!/bin/bash

# Fix bcrypt version compatibility issue on Raspberry Pi
# This script resolves the AttributeError: module 'bcrypt' has no attribute '__about__'

echo "🔧 Fixing bcrypt compatibility issue on Raspberry Pi..."

# Navigate to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "📍 Working in: $PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "🐍 Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

echo "🗑️ Uninstalling conflicting bcrypt/passlib packages..."
pip uninstall -y bcrypt passlib

echo "📦 Installing compatible versions..."
pip install bcrypt==4.0.1
pip install passlib==1.7.4

echo "🔄 Installing other requirements..."
pip install -r requirements.txt

echo "🧪 Testing bcrypt functionality..."
python3 -c "
import bcrypt
from passlib.context import CryptContext

print('✅ bcrypt version:', bcrypt.__version__)

# Test passlib with bcrypt
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
test_hash = pwd_context.hash('test_password')
print('✅ Password hashing works')

test_verify = pwd_context.verify('test_password', test_hash)
print('✅ Password verification works:', test_verify)

print('🎉 bcrypt compatibility fixed!')
"

echo ""
echo "✅ bcrypt fix complete!"
echo "📝 Next steps:"
echo "   1. Try starting your server again"
echo "   2. If issues persist, run this script again"
echo "   3. Check that your virtual environment is activated"
