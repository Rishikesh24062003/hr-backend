#!/usr/bin/env python3
"""
Test script to verify User model functionality
"""

import os
from database import get_collection, init_db
from app.models.user import User

def test_user_model():
    """Test User model functionality."""
    print("Testing User model functionality...")
    
    # Initialize database connection
    if not init_db():
        print("❌ Failed to connect to database!")
        return False
    
    # Test find_by_email
    user = User.find_by_email("admin@example.com")
    
    if not user:
        print("❌ User not found!")
        return False
    
    print(f"✅ User found: {user.email}")
    print(f"User role: {user.role}")
    print(f"User active: {user.is_active}")
    
    # Test password check
    is_valid = user.check_password("admin123")
    
    if is_valid:
        print("✅ Password check successful!")
    else:
        print("❌ Password check failed!")
        return False
    
    # Test to_dict
    user_dict = user.to_dict()
    print(f"✅ User dict: {user_dict}")
    
    return True

if __name__ == "__main__":
    test_user_model() 