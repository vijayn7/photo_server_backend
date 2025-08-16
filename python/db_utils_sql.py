"""
Database utilities for the photo server backend using SQLAlchemy/SQLite.
Handles user management with SQLite database instead of JSON files.
"""

import os
import json
from passlib.context import CryptContext
from database import database, users_table
from sqlalchemy import select, insert, update, delete
from typing import Dict, Optional, List

# Password hashing with defensive bcrypt initialization
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    print(f"⚠️ Warning: bcrypt initialization issue: {e}")
    print("🔧 Attempting alternative bcrypt configuration...")
    try:
        # Alternative configuration that's more compatible
        pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=12
        )
        print("✅ Successfully initialized bcrypt with alternative config")
    except Exception as e2:
        print(f"❌ Failed to initialize bcrypt: {e2}")
        print("💡 Please run: pip install bcrypt==4.0.1 passlib==1.7.4")
        raise

# Get admin username and password from environment variables
ADMIN_USERNAME = os.environ.get("PHOTO_SERVER_ADMIN")
ADMIN_PASSWORD = os.environ.get("PHOTO_SERVER_ADMIN_PASSWORD")

def load_users_config(config_file: str = "users_config.json") -> List[Dict]:
    """
    Load user configuration from JSON file
    
    Args:
        config_file (str): Path to the users configuration file
        
    Returns:
        list: List of user dictionaries
    """
    try:
        # Try to load from the project root directory
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_file)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get("default_users", [])
    except FileNotFoundError:
        print(f"Warning: {config_file} not found, using fallback default users")
        # Fallback to hardcoded users if file doesn't exist
        fallback_users = [
            {
                "username": "alice",
                "email": "alice@example.com",
                "full_name": "Alice Smith",
                "password": "secret",
                "disabled": False,
                "admin": False,
            },
            {
                "username": ADMIN_USERNAME or "vijayn7",
                "email": f"{ADMIN_USERNAME or 'vijayn7'}@example.com",
                "full_name": "Admin User",
                "password": ADMIN_PASSWORD or "admin_password",
                "disabled": False,
                "admin": True,
            }
        ]
        # Create the JSON file with fallback users
        save_users_config(fallback_users)
        return fallback_users
    except json.JSONDecodeError as e:
        print(f"Error parsing {config_file}: {e}")
        return []

def save_users_config(users: List[Dict], config_file: str = "users_config.json") -> bool:
    """
    Save user configuration to JSON file
    
    Args:
        users (list): List of user dictionaries
        config_file (str): Path to the users configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_file)
        
        config = {"default_users": users}
        
        with open(config_path, 'w') as f:
            json.dump(config, indent=2, fp=f)
        
        print(f"✅ Saved {len(users)} users to {config_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving users config: {e}")
        return False

def add_user_to_config(new_user: Dict, config_file: str = "users_config.json") -> bool:
    """
    Add a new user to the JSON configuration file
    
    Args:
        new_user (dict): User data to add
        config_file (str): Path to the users configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load existing users
        users = load_users_config(config_file)
        
        # Check if username already exists
        existing_usernames = [user["username"] for user in users]
        if new_user["username"] in existing_usernames:
            print(f"❌ User {new_user['username']} already exists in config")
            return False
        
        # Add new user
        users.append(new_user)
        
        # Save back to file
        return save_users_config(users, config_file)
        
    except Exception as e:
        print(f"❌ Error adding user to config: {e}")
        return False

async def ensure_default_users():
    """
    Ensure users in JSON config exist in the database, sync both ways
    This function acts as the source of truth synchronizer between JSON and DB
    """
    print("🔄 Synchronizing users between JSON config and database...")
    
    # Load users from JSON configuration file
    json_users = load_users_config()
    print(f"📖 Loaded {len(json_users)} users from JSON config")
    
    # Load existing users from database
    db_users = await load_users()
    print(f"💾 Found {len(db_users)} users in database")
    
    # Sync JSON users to database
    for user_config in json_users:
        username = user_config["username"]
        
        # Override admin status and password from environment variables if specified
        is_admin = user_config.get("admin", False)
        password_to_use = user_config["password"]
        
        if ADMIN_USERNAME and username == ADMIN_USERNAME:
            is_admin = True
            if ADMIN_PASSWORD:
                password_to_use = ADMIN_PASSWORD
        
        if username not in db_users:
            # User exists in JSON but not in DB - add to DB
            hashed_password = pwd_context.hash(password_to_use)
            
            query = insert(users_table).values(
                username=username,
                email=user_config["email"],
                full_name=user_config["full_name"],
                hashed_password=hashed_password,
                disabled=user_config.get("disabled", False),
                admin=is_admin
            )
            await database.execute(query)
            print(f"➕ Added {username} to database from JSON config")
        else:
            # User exists in both - check if we need to update from JSON
            db_user = db_users[username]
            needs_update = False
            update_fields = {}
            
            # Check for differences (except password which we won't auto-update)
            if db_user["email"] != user_config["email"]:
                update_fields["email"] = user_config["email"]
                needs_update = True
            if db_user["full_name"] != user_config["full_name"]:
                update_fields["full_name"] = user_config["full_name"]
                needs_update = True
            if db_user["disabled"] != user_config.get("disabled", False):
                update_fields["disabled"] = user_config.get("disabled", False)
                needs_update = True
            if db_user["admin"] != is_admin:
                update_fields["admin"] = is_admin
                needs_update = True
            
            if needs_update:
                query = update(users_table).where(
                    users_table.c.username == username
                ).values(**update_fields)
                await database.execute(query)
                print(f"🔄 Updated {username} in database from JSON config")
    
    print(f"✅ User synchronization complete - {len(json_users)} users active")

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
    Get a user by username - checks JSON config first, then database
    
    Args:
        username (str): Username to look up
        
    Returns:
        dict: User data if found, None otherwise
    """
    # First check JSON config
    json_users = load_users_config()
    for user in json_users:
        if user["username"] == username:
            # Return user data formatted like database format
            return {
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "hashed_password": pwd_context.hash(user["password"]),  # Hash the plain text password
                "disabled": user.get("disabled", False),
                "admin": user.get("admin", False),
            }
    
    # Fallback to database lookup
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
    Create a new user in both the database and JSON config file
    
    Args:
        username (str): Username for the new user
        email (str): Email address for the new user
        full_name (str): Full name for the new user
        password (str): Plain text password to be hashed
        admin (bool, optional): Whether user has admin privileges. Defaults to False.
        
    Returns:
        bool: True if user was created, False if username already exists
    """
    print(f"👤 Creating new user: {username}")
    
    # Check if username already exists in JSON config
    json_users = load_users_config()
    existing_usernames = [user["username"] for user in json_users]
    if username in existing_usernames:
        print(f"❌ User {username} already exists in JSON config")
        return False
    
    # Check if username already exists in database
    existing_user = await get_user(username)
    if existing_user:
        print(f"❌ User {username} already exists in database")
        return False
    
    # Ensure the configured admin username is always an admin
    is_admin = True if username == ADMIN_USERNAME else admin
    
    # Create user object for JSON
    new_user_json = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password,  # Store plain text in JSON
        "disabled": False,
        "admin": is_admin
    }
    
    # Add to JSON config first
    if not add_user_to_config(new_user_json):
        print(f"❌ Failed to add {username} to JSON config")
        return False
    
    # Hash the password for database
    hashed_password = pwd_context.hash(password)
    
    # Insert the new user into database
    try:
        query = insert(users_table).values(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            disabled=False,
            admin=is_admin,
        )
        
        await database.execute(query)
        print(f"✅ Created user {username} in both JSON config and database")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create user {username} in database: {e}")
        # TODO: Remove from JSON config if database creation failed
        return False

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
    First checks JSON config, then falls back to database
    
    Args:
        username (str): Username to authenticate
        password (str): Password to verify
        
    Returns:
        dict: User data if authentication successful, None otherwise
    """
    print(f"🔐 Authenticating user: {username}")
    
    # First, check if user exists in JSON config
    json_users = load_users_config()
    json_user = None
    for user in json_users:
        if user["username"] == username:
            json_user = user
            break
    
    if json_user:
        print(f"👤 Found {username} in JSON config")
        # Check if user is disabled in JSON
        if json_user.get("disabled", False):
            print(f"🚫 User {username} is disabled in JSON config")
            return None
        
        # For JSON config users, check plain text password first
        if json_user["password"] == password:
            print(f"✅ Plain text password match for {username}")
            # Return user data from JSON (we'll sync to DB later if needed)
            return {
                "username": json_user["username"],
                "email": json_user["email"],
                "full_name": json_user["full_name"],
                "hashed_password": pwd_context.hash(password),  # Hash for consistency
                "disabled": json_user.get("disabled", False),
                "admin": json_user.get("admin", False)
            }
    
    # Fallback to database authentication (for hashed passwords)
    print(f"🔍 Checking database for {username}")
    user = await get_user(username)
    if not user:
        print(f"❌ User {username} not found in database")
        return None
    
    if not verify_password(password, user["hashed_password"]):
        print(f"❌ Password verification failed for {username}")
        return None
    
    print(f"✅ Database authentication successful for {username}")
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
