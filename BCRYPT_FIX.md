# Raspberry Pi bcrypt Fix Guide

## Problem
You're seeing this error on Raspberry Pi:
```
(trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```

## Solution

### Option 1: Use the Fix Script (Recommended)
```bash
# On your Raspberry Pi, run:
./scripts/fix_bcrypt_pi.sh
```

### Option 2: Manual Fix
```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Uninstall conflicting packages
pip uninstall -y bcrypt passlib

# 3. Install compatible versions
pip install bcrypt==4.0.1
pip install passlib==1.7.4

# 4. Reinstall requirements
pip install -r requirements.txt
```

### Option 3: Alternative bcrypt package
```bash
# If the above doesn't work, try:
pip uninstall -y bcrypt
pip install bcrypt-cffi
```

## Why This Happens
- The `passlib` library expects bcrypt to have `__about__.__version__`
- Newer bcrypt versions changed their version attribute structure
- This creates compatibility issues on some systems, especially ARM-based devices

## Verification
After applying the fix:
```bash
python3 -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print('✅ bcrypt is working!')
"
```

## Notes
- The warning message may still appear but functionality should work
- Our code now has defensive initialization to handle this gracefully
- Environment variables and JSON user configuration will still work normally
