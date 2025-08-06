#!/usr/bin/env python3
"""
MongoDB Database Setup Script for HR Resume System
This script initializes the MongoDB database with proper configurations.
"""

import os
from database import init_db

def main():
    """Initialize MongoDB database."""
    print("Setting up MongoDB database for HR Resume System...")
    
    # Check if MongoDB URI is set
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/hr_system')
    print(f"MongoDB URI: {mongodb_uri}")
    
    # Initialize database
    if init_db():
        print("\n✅ MongoDB database setup completed successfully!")
        print("\nWhat was created:")
        print("- Connected to MongoDB")
        print("- Created indexes for performance")
        print("- Created default admin user")
        print("- Added sample job data")
        print("\nDefault Login Credentials:")
        print("- Email: admin@example.com")
        print("- Password: admin123")
        print("\nYou can now start the Flask application.")
    else:
        print("\n❌ Database setup failed!")
        print("Please check your MongoDB connection and try again.")
        exit(1)

if __name__ == "__main__":
    main()