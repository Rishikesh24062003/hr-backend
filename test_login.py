#!/usr/bin/env python3
"""
Test script to verify login functionality
"""

import os
from database import get_collection, init_db
from werkzeug.security import check_password_hash

def test_login():
    """Test login functionality."""
    print("Testing login functionality...")
    
    # Initialize database connection
    if not init_db():
        print("❌ Failed to connect to database!")
        return False
    
    # Get users collection
    users_collection = get_collection('users')
    
    # Check if admin user exists
    admin_user = users_collection.find_one({"email": "admin@example.com"})
    
    if not admin_user:
        print("❌ Admin user not found!")
        return False
    
    print(f"✅ Admin user found: {admin_user['email']}")
    print(f"Password hash: {admin_user['password_hash'][:20]}...")
    
    # Test password verification
    test_password = "admin123"
    is_valid = check_password_hash(admin_user['password_hash'], test_password)
    
    if is_valid:
        print("✅ Password verification successful!")
        return True
    else:
        print("❌ Password verification failed!")
        return False

if __name__ == "__main__":
    test_login() 