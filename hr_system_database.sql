# HR Resume System Database Schema
# SQLite Database Creation Script

## Database Structure

### User Table
```sql
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Resume Table
```sql
CREATE TABLE IF NOT EXISTS resume (
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
);
```

### Job Table
```sql
CREATE TABLE IF NOT EXISTS job (
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
);
```

### Ranking Table
```sql
CREATE TABLE IF NOT EXISTS ranking (
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
);
```

## Indexes for Performance
```sql
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_resume_status ON resume(processing_status);
CREATE INDEX IF NOT EXISTS idx_job_status ON job(status);
CREATE INDEX IF NOT EXISTS idx_ranking_score ON ranking(overall_score);
```

## Sample Data

### Default Admin User
```sql
INSERT OR IGNORE INTO user (email, password_hash, role, is_active)
VALUES ('admin@example.com', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'admin', TRUE);
```

### Sample Jobs
```sql
INSERT INTO job (title, description, company, location, employment_type, requirements, salary_min, salary_max, currency, status, priority)
VALUES 
('Software Engineer', 'We are looking for a skilled software engineer to join our team', 'Tech Corp', 'San Francisco, CA', 'full-time', 
 '{"skills": ["Python", "React", "JavaScript", "SQL"], "experience_years": 3, "education": "Bachelor degree"}', 
 80000, 120000, 'USD', 'active', 1),

('Data Scientist', 'Join our data science team to analyze complex datasets', 'Data Analytics Inc', 'New York, NY', 'full-time',
 '{"skills": ["Python", "Machine Learning", "SQL", "Statistics"], "experience_years": 2, "education": "Master degree"}',
 90000, 140000, 'USD', 'active', 2);
```

## Database Usage Instructions

### 1. Create Database
```bash
sqlite3 hr_system.db < hr_system_database.sql
```

### 2. Connect to Database
```bash
sqlite3 hr_system.db
```

### 3. Basic Queries
```sql
-- View all users
SELECT * FROM user;

-- View all jobs
SELECT * FROM job;

-- View all resumes
SELECT * FROM resume;

-- View rankings with job and resume info
SELECT r.overall_score, j.title, res.candidate_name
FROM ranking r
JOIN job j ON r.job_id = j.id
JOIN resume res ON r.resume_id = res.id
ORDER BY r.overall_score DESC;
```

## Login Credentials

**Default Admin Account:**
- Email: admin@example.com
- Password: admin123

## Database File Location

The database file should be placed in your backend directory:
```
backend/
├── hr_system.db          # ← Database file goes here
├── app.py
├── requirements.txt
└── app/
    ├── models/
    ├── routes/
    └── utils/
```

## Backup and Restore

### Create Backup
```bash
sqlite3 hr_system.db ".backup hr_system_backup.db"
```

### Restore from Backup
```bash
sqlite3 hr_system.db ".restore hr_system_backup.db"
```

## Database Maintenance

### Vacuum (Optimize)
```sql
VACUUM;
```

### Analyze Statistics
```sql
ANALYZE;
```

### Check Integrity
```sql
PRAGMA integrity_check;
```