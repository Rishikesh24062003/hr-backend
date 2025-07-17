#!/usr/bin/env python3
"""
HR Resume System Database Setup Script
This script creates the SQLite database for the HR Resume System
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime

def create_password_hash(password):
    """Create a simple password hash"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    """Set up the HR Resume System database"""

    # Remove existing database if it exists
    if os.path.exists('hr_system.db'):
        os.remove('hr_system.db')
        print("Removed existing database file")

    # Create new database
    conn = sqlite3.connect('hr_system.db')
    cursor = conn.cursor()

    # Create tables
    print("Creating database tables...")

    # User table
    cursor.execute("""
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'admin',
        is_active BOOLEAN DEFAULT TRUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Resume table
    cursor.execute("""
    CREATE TABLE resume (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename VARCHAR(255) NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size INTEGER,
        mime_type VARCHAR(100),
        raw_text TEXT,
        parsed_data JSON,
        candidate_name VARCHAR(255),
        candidate_email VARCHAR(255),
        candidate_phone VARCHAR(50),
        processing_status VARCHAR(50) DEFAULT 'pending',
        error_message TEXT,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        processed_at DATETIME
    )
    """)

    # Job table
    cursor.execute("""
    CREATE TABLE job (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        company VARCHAR(200),
        location VARCHAR(200),
        employment_type VARCHAR(50),
        requirements JSON,
        salary_min REAL,
        salary_max REAL,
        currency VARCHAR(10) DEFAULT 'USD',
        status VARCHAR(50) DEFAULT 'active',
        priority INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME
    )
    """)

    # Ranking table
    cursor.execute("""
    CREATE TABLE ranking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        overall_score REAL NOT NULL,
        score_breakdown JSON,
        algorithm_version VARCHAR(50) DEFAULT '1.0',
        confidence_score REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resume (id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES job (id) ON DELETE CASCADE,
        UNIQUE(resume_id, job_id)
    )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX idx_user_email ON user(email)")
    cursor.execute("CREATE INDEX idx_resume_status ON resume(processing_status)")
    cursor.execute("CREATE INDEX idx_job_status ON job(status)")
    cursor.execute("CREATE INDEX idx_ranking_score ON ranking(overall_score)")

    print("Database tables created successfully!")

    # Insert default admin user
    password_hash = create_password_hash('admin123')
    cursor.execute("""
    INSERT INTO user (email, password_hash, role, is_active)
    VALUES (?, ?, ?, ?)
    """, ('admin@example.com', password_hash, 'admin', True))

    # Insert sample jobs
    sample_jobs = [
        ('Software Engineer', 'We are looking for a skilled software engineer to join our team', 
         'Tech Corp', 'San Francisco, CA', 'full-time', 
         '{"skills": ["Python", "React", "JavaScript", "SQL"], "experience_years": 3, "education": "Bachelor degree"}',
         80000, 120000, 'USD', 'active', 1),
        ('Data Scientist', 'Join our data science team to analyze complex datasets',
         'Data Analytics Inc', 'New York, NY', 'full-time',
         '{"skills": ["Python", "Machine Learning", "SQL", "Statistics"], "experience_years": 2, "education": "Master degree"}',
         90000, 140000, 'USD', 'active', 2)
    ]

    for job in sample_jobs:
        cursor.execute("""
        INSERT INTO job (title, description, company, location, employment_type, 
                         requirements, salary_min, salary_max, currency, status, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, job)

    conn.commit()
    conn.close()

    print("Default admin user created!")
    print("Sample jobs inserted!")
    print("\nDatabase setup complete!")
    print("\nLogin credentials:")
    print("- Email: admin@example.com")
    print("- Password: admin123")
    print("\nDatabase file: hr_system.db")

if __name__ == "__main__":
    setup_database()
