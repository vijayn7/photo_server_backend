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
                "admin": False,
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

def create_user(username, email, full_name, password, admin=False):
    """
    Create a new user in the database
    
    Args:
        username (str): Username for the new user
        email (str): Email address for the new user
        full_name (str): Full name for the new user
        password (str): Plain text password to be hashed
        admin (bool, optional): Whether user has admin privileges. Defaults to False.
        
    Returns:
        bool: True if user was created, False if username already exists
    """
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False
    
    # Hash the password
    hashed_password = pwd_context.hash(password)

    admin = True if username == "vijayn7" else False

    # Add the new user
    users[username] = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "disabled": False,
        "admin": admin,
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

def update_admin_status(admin_username, target_username, admin_status):
    """
    Update the admin status of a user
    
    Args:
        admin_username (str): Username of the admin making the change (must be "vijayn7")
        target_username (str): Username of the user whose admin status is being updated
        admin_status (bool): New admin status (True to grant admin, False to revoke)
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    # Check if the admin user is vijayn7
    if admin_username != "vijayn7":
        return False
    
    # Check if the admin user exists and is an admin
    admin_user = get_user(admin_username)
    if not admin_user or not admin_user.get("admin", False):
        return False
    
    # Check if the target user exists
    target_user = get_user(target_username)
    if not target_user:
        return False
    
    # Load all users
    users = load_users()
    
    # Update the admin status of the target user
    users[target_username]["admin"] = admin_status
    
    # Save updated user database
    save_users(users)
    
    return True

def grant_admin_privileges(admin_username, target_username):
    """
    Grant admin privileges to a user
    
    Args:
        admin_username (str): Username of the admin making the change (must be "vijayn7")
        target_username (str): Username of the user to grant admin privileges to
        
    Returns:
        bool: True if admin privileges were granted, False otherwise
    """
    return update_admin_status(admin_username, target_username, True)

def revoke_admin_privileges(admin_username, target_username):
    """
    Revoke admin privileges from a user
    
    Args:
        admin_username (str): Username of the admin making the change (must be "vijayn7")
        target_username (str): Username of the user to revoke admin privileges from
        
    Returns:
        bool: True if admin privileges were revoked, False otherwise
    """
    return update_admin_status(admin_username, target_username, False)
