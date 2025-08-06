from datetime import datetime
from bson import ObjectId
from database import get_collection

class Job:
    """Job model for storing job postings and requirements."""
    
    def __init__(self, title=None, description=None, company=None, location=None,
                 employment_type='full-time', _id=None, **kwargs):
        self._id = _id or ObjectId()
        self.title = title
        self.description = description
        self.company = company
        self.location = location
        self.employment_type = employment_type
        
        # Job requirements (stored as dict)
        self.requirements = kwargs.get('requirements')
        
        # Salary information
        self.salary_min = kwargs.get('salary_min')
        self.salary_max = kwargs.get('salary_max')
        self.currency = kwargs.get('currency', 'USD')
        
        # Status and metadata
        self.status = kwargs.get('status', 'active')
        self.priority = kwargs.get('priority', 1)
        
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.expires_at = kwargs.get('expires_at')
    
    @classmethod
    def from_dict(cls, data):
        """Create Job instance from dictionary."""
        return cls(
            _id=data.get('_id'),
            title=data.get('title'),
            description=data.get('description'),
            company=data.get('company'),
            location=data.get('location'),
            employment_type=data.get('employment_type', 'full-time'),
            requirements=data.get('requirements'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            currency=data.get('currency', 'USD'),
            status=data.get('status', 'active'),
            priority=data.get('priority', 1),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            expires_at=data.get('expires_at')
        )
    
    def save(self):
        """Save job to database."""
        jobs_collection = get_collection('jobs')
        self.updated_at = datetime.utcnow()
        
        job_data = {
            'title': self.title,
            'description': self.description,
            'company': self.company,
            'location': self.location,
            'employment_type': self.employment_type,
            'requirements': self.requirements,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'currency': self.currency,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'expires_at': self.expires_at
        }
        
        if hasattr(self, '_id') and self._id:
            # Update existing job
            jobs_collection.update_one(
                {'_id': self._id},
                {'$set': job_data}
            )
        else:
            # Create new job
            result = jobs_collection.insert_one(job_data)
            self._id = result.inserted_id
        
        return self
    
    def delete(self):
        """Delete job from database."""
        jobs_collection = get_collection('jobs')
        rankings_collection = get_collection('rankings')
        
        if hasattr(self, '_id') and self._id:
            # Delete associated rankings first
            rankings_collection.delete_many({'job_id': self._id})
            # Delete job
            jobs_collection.delete_one({'_id': self._id})
    
    @classmethod
    def find_by_id(cls, job_id):
        """Find job by ID."""
        jobs_collection = get_collection('jobs')
        if isinstance(job_id, str):
            job_id = ObjectId(job_id)
        job_data = jobs_collection.find_one({'_id': job_id})
        return cls.from_dict(job_data) if job_data else None
    
    @classmethod
    def get_all(cls, status=None, page=1, per_page=10):
        """Get all jobs with optional filtering and pagination."""
        jobs_collection = get_collection('jobs')
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get jobs with pagination
        jobs_cursor = jobs_collection.find(query).skip(skip).limit(per_page).sort('created_at', -1)
        jobs = [cls.from_dict(job_data) for job_data in jobs_cursor]
        
        # Get total count
        total = jobs_collection.count_documents(query)
        
        return {
            'jobs': jobs,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def to_dict(self):
        """Convert job to dictionary."""
        return {
            'id': str(self._id),
            'title': self.title,
            'description': self.description,
            'company': self.company,
            'location': self.location,
            'employment_type': self.employment_type,
            'requirements': self.requirements,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'currency': self.currency,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @property
    def id(self):
        """Get string representation of ID."""
        return str(self._id)
    
    def __repr__(self):
        return f'<Job {self.title}>'
