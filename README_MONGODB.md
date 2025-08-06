# MongoDB Migration for HR Resume System

The HR Resume System has been successfully migrated from SQLite to MongoDB.

## Prerequisites

1. **MongoDB**: Install MongoDB locally or use MongoDB Atlas
   - Local installation: https://docs.mongodb.com/manual/installation/
   - MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas

2. **Python Dependencies**: Install the updated requirements
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory or set these environment variables:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/hr_system

# For MongoDB Atlas (cloud):
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/hr_system

# Other settings
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Local MongoDB Setup

If using local MongoDB:

1. **Start MongoDB**:
   ```bash
   # On macOS with Homebrew
   brew services start mongodb-community

   # On Ubuntu/Debian
   sudo systemctl start mongod

   # On Windows
   # Start MongoDB service from Services
   ```

2. **Verify MongoDB is running**:
   ```bash
   mongosh
   # Should connect successfully
   ```

## Database Setup

Run the setup script to initialize the database:

```bash
cd backend
python setup_mongodb.py
```

This will:
- Connect to MongoDB
- Create necessary indexes
- Create default admin user
- Add sample job data

## Running the Application

Start the Flask application:

```bash
cd backend
python app.py
```

## Default Login

- **Email**: admin@example.com
- **Password**: admin123

## Database Structure

### Collections

1. **users** - User accounts and authentication
2. **resumes** - Uploaded resume files and parsed data
3. **jobs** - Job postings and requirements
4. **rankings** - Candidate-job match scores

### Key Changes from SQL

- **Object IDs**: MongoDB uses ObjectId instead of auto-incrementing integers
- **Embedded Documents**: JSON data is stored natively without serialization
- **Flexible Schema**: Documents can have varying structures
- **No Foreign Keys**: Relationships are managed through ObjectId references

## MongoDB Operations

### Basic Queries

Connect to your database:
```bash
mongosh "mongodb://localhost:27017/hr_system"
```

View collections:
```javascript
show collections
```

View users:
```javascript
db.users.find().pretty()
```

View jobs:
```javascript
db.jobs.find().pretty()
```

View resumes:
```javascript
db.resumes.find().pretty()
```

### Indexes

The following indexes are created for performance:

- `users.email` (unique)
- `users.is_active`
- `resumes.processing_status`
- `resumes.candidate_email`
- `resumes.uploaded_at`
- `jobs.status`
- `jobs.created_at`
- `jobs.priority`
- `rankings.overall_score`
- `rankings.resume_id + job_id` (unique compound)
- `rankings.created_at`

## Backup and Restore

### Create Backup
```bash
mongodump --db hr_system --out backup/
```

### Restore Backup
```bash
mongorestore --db hr_system backup/hr_system/
```

## Troubleshooting

### Connection Issues

1. **MongoDB not running**:
   ```bash
   # Check if MongoDB is running
   ps aux | grep mongod
   
   # Start MongoDB
   brew services start mongodb-community  # macOS
   sudo systemctl start mongod             # Linux
   ```

2. **Connection string issues**:
   - Verify MONGODB_URI in environment variables
   - Check if MongoDB is accessible on the specified port

3. **Authentication errors**:
   - Ensure credentials are correct in connection string
   - Check if authentication is enabled in MongoDB

### Performance Issues

- Ensure indexes are created (run setup script)
- Monitor query performance with MongoDB Compass
- Consider using aggregation pipelines for complex queries

## Migration Notes

- All existing functionality has been preserved
- API endpoints remain unchanged
- Data structure is equivalent to previous SQL schema
- Pagination and filtering work the same way
- Authentication and authorization unchanged

## Development

When developing:

1. **Model Changes**: Update the model classes in `app/models/`
2. **New Queries**: Use MongoDB query syntax in route handlers
3. **Indexes**: Add new indexes in `database.py` if needed
4. **Testing**: Test with sample data using the setup script