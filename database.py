#!/usr/bin/env python3
"""
MongoDB Database Configuration and Connection
"""

import os
from pymongo import MongoClient
from bson import ObjectId
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    """MongoDB connection and configuration class."""
    
    def __init__(self):
        # MongoDB connection string
        self.connection_string = os.getenv('MONGODB_URI', 'mongodb+srv://rishikeshmishra477:LKXmeF6EWDi1pKeh@cluster0.s0xf7bg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        self.client = None
        self.db = None
       
    def connect(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.connection_string)
            # Extract database name from connection string or use default
            if 'hr_system' in self.connection_string:
                db_name = 'hr_system'
            else:
                db_name = 'hr_system'
            self.db = self.client[db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"Connected to MongoDB successfully! Database: {db_name}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    def get_database(self):
        """Get database instance."""
        return self.db
    
    def get_collection(self, collection_name):
        """Get collection instance."""
        return self.db[collection_name]
    
    def create_indexes(self):
        """Create indexes for better performance."""
        try:
            # User collection indexes
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("is_active")
            
            # Resume collection indexes
            self.db.resumes.create_index("processing_status")
            self.db.resumes.create_index("candidate_email")
            self.db.resumes.create_index("uploaded_at")
            
            # Job collection indexes
            self.db.jobs.create_index("status")
            self.db.jobs.create_index("created_at")
            self.db.jobs.create_index("priority")
            
            # Ranking collection indexes
            self.db.rankings.create_index("overall_score")
            self.db.rankings.create_index([("resume_id", 1), ("job_id", 1)], unique=True)
            self.db.rankings.create_index("created_at")
            
            print("Indexes created successfully!")
            
        except Exception as e:
            print(f"Error creating indexes: {str(e)}")
    
    def setup_default_data(self):
        """Set up default admin user and sample data."""
        try:
            # Create default admin user if not exists
            admin_user = self.db.users.find_one({"email": "admin@example.com"})
            if not admin_user:
                from werkzeug.security import generate_password_hash
                password_hash = generate_password_hash("admin123")
                admin_data = {
                    "email": "admin@example.com",
                    "password_hash": password_hash,
                    "role": "admin",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                self.db.users.insert_one(admin_data)
                print("Default admin user created!")
            
            # Create sample jobs if none exist
            job_count = self.db.jobs.count_documents({})
            if job_count == 0:
                sample_jobs = [
                    {
                        "title": "Software Engineer",
                        "description": "We are looking for a skilled software engineer to join our team",
                        "company": "Tech Corp",
                        "location": "San Francisco, CA",
                        "employment_type": "full-time",
                        "requirements": {
                            "skills": ["Python", "React", "JavaScript", "SQL"],
                            "experience_years": 3,
                            "education": "Bachelor degree"
                        },
                        "salary_min": 80000,
                        "salary_max": 120000,
                        "currency": "USD",
                        "status": "active",
                        "priority": 1,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    },
                    {
                        "title": "Data Scientist",
                        "description": "Join our data science team to analyze complex datasets",
                        "company": "Data Analytics Inc",
                        "location": "New York, NY",
                        "employment_type": "full-time",
                        "requirements": {
                            "skills": ["Python", "Machine Learning", "SQL", "Statistics"],
                            "experience_years": 2,
                            "education": "Master degree"
                        },
                        "salary_min": 90000,
                        "salary_max": 140000,
                        "currency": "USD",
                        "status": "active",
                        "priority": 2,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                ]
                self.db.jobs.insert_many(sample_jobs)
                print("Sample jobs created!")
            
            print("Default data setup complete!")
            
        except Exception as e:
            print(f"Error setting up default data: {str(e)}")

# Global MongoDB instance
mongodb = MongoDB()

def get_db():
    """Get MongoDB database instance."""
    return mongodb.get_database()

def get_collection(collection_name):
    """Get MongoDB collection instance."""
    return mongodb.get_collection(collection_name)

def init_db():
    """Initialize database connection and setup."""
    if mongodb.connect():
        mongodb.create_indexes()
        mongodb.setup_default_data()
        return True
    return False

def close_db():
    """Close database connection."""
    mongodb.close()