"""
Database utilities for the photo server backend using SQLAlchemy/SQLite.
Handles user management with SQLite database instead of JSON files.
"""

import os
from passlib.context import CryptContext
from database import database, users_table
from sqlalchemy import select, insert, update, delete
from typing import Dict, Optional, List

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get admin username and password from environment variables
ADMIN_USERNAME = os.environ.get("PHOTO_SERVER_ADMIN")
ADMIN_PASSWORD = os.environ.get("PHOTO_SERVER_ADMIN_PASSWORD")

async def ensure_default_users():
    """
    Ensure default users exist in the database, create them if they don't
    """
    # Check if any users exist
    query = select(users_table)
    users = await database.fetch_all(query)
    
    if not users:
        # Create default users
        default_users = [
            {
                "username": "alice",
                "email": "alice@example.com",
                "full_name": "Alice Smith",
                "hashed_password": pwd_context.hash("secret"),
                "disabled": False,
                "admin": False,
            },
            {
                "username": ADMIN_USERNAME,
                "email": f"{ADMIN_USERNAME}@example.com",
                "full_name": "Admin User",
                "hashed_password": pwd_context.hash(ADMIN_PASSWORD),
                "disabled": False,
                "admin": True,
            }
        ]
        
        for user_data in default_users:
            query = insert(users_table).values(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=user_data["hashed_password"],
                disabled=user_data["disabled"],
                admin=user_data["admin"]
            )
            await database.execute(query)

async def load_users() -> Dict:
    """
    Load all users from the database and return as a dictionary (for compatibility)
    
    Returns:
        dict: Dictionary of users with usernames as keys
    """
    query = select(users_table)
    users = await database.fetch_all(query)
    
    users_dict = {}
    for user in users:
        users_dict[user.username] = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "disabled": user.disabled,
            "admin": user.admin,
        }
    
    return users_dict

async def get_user(username: str) -> Optional[Dict]:
    """
    Get a user by username
    
    Args:
        username (str): Username to look up
        
    Returns:
        dict: User data if found, None otherwise
    """
    query = select(users_table).where(users_table.c.username == username)
    user = await database.fetch_one(query)
    
    if user:
        return {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "disabled": user.disabled,
            "admin": user.admin,
        }
    return None

async def create_user(username: str, email: str, full_name: str, password: str, admin: bool = False) -> bool:
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
    # Check if username already exists
    existing_user = await get_user(username)
    if existing_user:
        return False
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    # Ensure the configured admin username is always an admin
    is_admin = True if username == ADMIN_USERNAME else admin
    
    # Insert the new user
    query = insert(users_table).values(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        disabled=False,
        admin=is_admin,
    )
    
    await database.execute(query)
    return True

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with username and password
    
    Args:
        username (str): Username to authenticate
        password (str): Password to verify
        
    Returns:
        dict: User data if authentication successful, None otherwise
    """
    user = await get_user(username)
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    return user

async def update_admin_status(admin_username: str, target_username: str, admin_status: bool) -> bool:
    """
    Update the admin status of a user. Only admin users can perform this action.
    
    Args:
        admin_username (str): Username of the admin performing the action
        target_username (str): Username of the user whose admin status to update
        admin_status (bool): New admin status
        
    Returns:
        bool: True if successful, False if not authorized or user not found
    """
    # Verify that the requesting user is an admin
    admin_user = await get_user(admin_username)
    if not admin_user or not admin_user["admin"]:
        return False
    
    # Check if target user exists
    target_user = await get_user(target_username)
    if not target_user:
        return False
    
    # Update admin status
    query = update(users_table).where(
        users_table.c.username == target_username
    ).values(admin=admin_status)
    
    await database.execute(query)
    return True

async def grant_admin_privileges(admin_username: str, target_username: str) -> bool:
    """
    Grant admin privileges to a user
    
    Args:
        admin_username (str): Username of the admin performing the action
        target_username (str): Username of the user to grant admin privileges to
        
    Returns:
        bool: True if successful, False otherwise
    """
    return await update_admin_status(admin_username, target_username, True)

async def revoke_admin_privileges(admin_username: str, target_username: str) -> bool:
    """
    Revoke admin privileges from a user
    
    Args:
        admin_username (str): Username of the admin performing the action
        target_username (str): Username of the user to revoke admin privileges from
        
    Returns:
        bool: True if successful, False otherwise
    """
    return await update_admin_status(admin_username, target_username, False)
