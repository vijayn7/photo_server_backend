"""
Database utilities for the photo server backend.
Handles loading and saving users to JSON file.
"""

import json
import os
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Path to users JSON file
USERS_FILE = "users.json"

def load_users():
    """
    Load users from JSON file or return default if file doesn't exist
    
    Returns:
        dict: Dictionary of users with usernames as keys
    """
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return a default user if file doesn't exist or is invalid
        default_users = {
            "alice": {
                "username": "alice",
                "full_name": "Alice Smith",
                "email": "alice@example.com",
                "hashed_password": pwd_context.hash("secret"),
                "disabled": False,
            }
        }
        # Save the default users to create the file
        save_users(default_users)
        return default_users

def save_users(users_db):
    """
    Save users to JSON file
    
    Args:
        users_db (dict): Dictionary of users with usernames as keys
    """
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=4)

def get_user(username):
    """
    Get a user by username
    
    Args:
        username (str): Username to look up
        
    Returns:
        dict: User data if found, None otherwise
    """
    users = load_users()
    return users.get(username)

def create_user(username, email, full_name, password):
    """
    Create a new user in the database
    
    Args:
        username (str): Username for the new user
        email (str): Email address for the new user
        full_name (str): Full name for the new user
        password (str): Plain text password to be hashed
        
    Returns:
        bool: True if user was created, False if username already exists
    """
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    # Add the new user
    users[username] = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "disabled": False,
    }
    
    # Save updated user database
    save_users(users)
    return True

def verify_password(plain_password, hashed_password):
    """
    Verify that a plain password matches a hashed password
    
    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username, password):
    """
    Authenticate a user by username and password
    
    Args:
        username (str): Username to authenticate
        password (str): Plain text password to verify
        
    Returns:
        dict: User data if authentication succeeds, None otherwise
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user
