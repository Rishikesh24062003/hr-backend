#!/usr/bin/env python3
"""
Script to fix admin user password hash
"""

import os
from database import get_collection, init_db
from werkzeug.security import generate_password_hash, check_password_hash

def fix_admin_user():
    """Fix admin user password hash."""
    print("Fixing admin user password hash...")
    
    # Initialize database connection
    if not init_db():
        print("❌ Failed to connect to database!")
        return False
    
    # Get users collection
    users_collection = get_collection('users')
    
    # Delete existing admin user
    users_collection.delete_one({"email": "admin@example.com"})
    print("🗑️  Deleted existing admin user")
    
    # Create new admin user with correct password hash
    password_hash = generate_password_hash("admin123")
    admin_data = {
        "email": "admin@example.com",
        "password_hash": password_hash,
        "role": "admin",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    
    result = users_collection.insert_one(admin_data)
    print(f"✅ Created new admin user with ID: {result.inserted_id}")
    
    # Verify the password works
    admin_user = users_collection.find_one({"email": "admin@example.com"})
    is_valid = check_password_hash(admin_user['password_hash'], "admin123")
    
    if is_valid:
        print("✅ Password verification successful!")
        print("Login credentials:")
        print("- Email: admin@example.com")
        print("- Password: admin123")
        return True
    else:
        print("❌ Password verification still failed!")
        return False

if __name__ == "__main__":
    fix_admin_user() 