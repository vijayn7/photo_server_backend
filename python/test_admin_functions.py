#!/usr/bin/env python3
"""
Test script to verify the admin privilege management functions.
"""

import db_utils

def test_admin_functions():
    """Test admin functions in db_utils.py"""
    print("Testing admin functions...")
    
    # Create a test user
    print("Creating test user 'john'...")
    db_utils.create_user("john", "john@example.com", "John Doe", "password123", admin=False)
    
    # Try to grant admin privileges as a non-admin user
    print("\nTrying to grant admin privileges as non-admin user 'alice'...")
    result = db_utils.grant_admin_privileges("alice", "john")
    print(f"Result (should be False): {result}")
    
    # Grant admin privileges as vijayn7 (admin)
    print("\nGranting admin privileges to 'john' as admin user 'vijayn7'...")
    result = db_utils.grant_admin_privileges("vijayn7", "john")
    print(f"Result (should be True): {result}")
    
    # Check if john is now an admin
    john = db_utils.get_user("john")
    print(f"Is john an admin? {john['admin']}")
    
    # Revoke admin privileges
    print("\nRevoking admin privileges from 'john'...")
    result = db_utils.revoke_admin_privileges("vijayn7", "john")
    print(f"Result (should be True): {result}")
    
    # Check if john's admin status was revoked
    john = db_utils.get_user("john")
    print(f"Is john still an admin? {john['admin']}")
    
    # Try to revoke admin privileges from nonexistent user
    print("\nTrying to revoke admin privileges from nonexistent user...")
    result = db_utils.revoke_admin_privileges("vijayn7", "nonexistent")
    print(f"Result (should be False): {result}")
    
    print("\nAdmin function tests completed.")

if __name__ == "__main__":
    test_admin_functions()
