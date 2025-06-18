#!/usr/bin/env python3
"""
Debug script to check user authentication and environment variable loading.
"""

import os
import json
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import db_utils

def debug_users():
    """Debug users in db_utils.py"""
    print("=== Environment Variables ===")
    print(f"ADMIN_USERNAME: '{db_utils.ADMIN_USERNAME}'")
    print(f"ADMIN_PASSWORD: '{db_utils.ADMIN_PASSWORD}'")
    
    print("\n=== Checking users file ===")
    if os.path.exists(db_utils.USERS_FILE):
        print(f"Users file exists at: {db_utils.USERS_FILE}")
        try:
            with open(db_utils.USERS_FILE, "r") as f:
                users = json.load(f)
                print(f"Found {len(users)} users:")
                for username, user_data in users.items():
                    # Don't print the actual hashed password
                    has_password = "hashed_password" in user_data
                    print(f"  - {username}: admin={user_data.get('admin', False)}, has_password={has_password}")
        except Exception as e:
            print(f"Error reading users file: {str(e)}")
    else:
        print("Users file does not exist - it will be created with default users")
        
    print("\n=== Testing Authentication ===")
    # Try authenticating with vijayn7
    result = db_utils.authenticate_user(db_utils.ADMIN_USERNAME, db_utils.ADMIN_PASSWORD)
    if result:
        print(f"Authentication successful for {db_utils.ADMIN_USERNAME}")
    else:
        print(f"Authentication failed for {db_utils.ADMIN_USERNAME}")
    
    # Try authenticating with default user
    result = db_utils.authenticate_user("alice", "secret")
    if result:
        print(f"Authentication successful for alice")
    else:
        print(f"Authentication failed for alice")
    
    print("\n=== Creating Fresh Users Database ===")
    # Rename the users file if it exists
    if os.path.exists(db_utils.USERS_FILE):
        backup_file = f"{db_utils.USERS_FILE}.bak"
        print(f"Renaming {db_utils.USERS_FILE} to {backup_file}")
        os.rename(db_utils.USERS_FILE, backup_file)
    
    # Create new users
    users = db_utils.load_users()
    print(f"New users database created with {len(users)} users:")
    for username, user_data in users.items():
        # Don't print the actual hashed password
        has_password = "hashed_password" in user_data
        print(f"  - {username}: admin={user_data.get('admin', False)}, has_password={has_password}")
        
    print("\n=== Testing Authentication with New Database ===")
    # Try authenticating with vijayn7
    result = db_utils.authenticate_user(db_utils.ADMIN_USERNAME, db_utils.ADMIN_PASSWORD)
    if result:
        print(f"Authentication successful for {db_utils.ADMIN_USERNAME}")
    else:
        print(f"Authentication failed for {db_utils.ADMIN_USERNAME}")
    
    # Try authenticating with default user
    result = db_utils.authenticate_user("alice", "secret")
    if result:
        print(f"Authentication successful for alice")
    else:
        print(f"Authentication failed for alice")

if __name__ == "__main__":
    debug_users()
