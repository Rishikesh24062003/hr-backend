from datetime import datetime
from bson import ObjectId
from database import get_collection

class Ranking:
    """Ranking model for storing candidate-job match scores."""
    
    def __init__(self, resume_id=None, job_id=None, overall_score=None, _id=None, **kwargs):
        self._id = _id or ObjectId()
        
        # Foreign keys - store as ObjectIds
        if isinstance(resume_id, str):
            self.resume_id = ObjectId(resume_id)
        else:
            self.resume_id = resume_id
            
        if isinstance(job_id, str):
            self.job_id = ObjectId(job_id)
        else:
            self.job_id = job_id
        
        # Scoring information
        self.overall_score = overall_score
        
        # Detailed scores (stored as dict)
        self.score_breakdown = kwargs.get('score_breakdown')
        
        # Ranking metadata
        self.algorithm_version = kwargs.get('algorithm_version', '1.0')
        self.confidence_score = kwargs.get('confidence_score')
        
        # Timestamps
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @classmethod
    def from_dict(cls, data):
        """Create Ranking instance from dictionary."""
        return cls(
            _id=data.get('_id'),
            resume_id=data.get('resume_id'),
            job_id=data.get('job_id'),
            overall_score=data.get('overall_score'),
            score_breakdown=data.get('score_breakdown'),
            algorithm_version=data.get('algorithm_version', '1.0'),
            confidence_score=data.get('confidence_score'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def save(self):
        """Save ranking to database."""
        rankings_collection = get_collection('rankings')
        self.updated_at = datetime.utcnow()
        
        ranking_data = {
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'overall_score': self.overall_score,
            'score_breakdown': self.score_breakdown,
            'algorithm_version': self.algorithm_version,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Check for existing ranking with same resume_id and job_id
        existing = rankings_collection.find_one({
            'resume_id': self.resume_id,
            'job_id': self.job_id
        })
        
        if existing and (not hasattr(self, '_id') or self._id != existing['_id']):
            # Update existing ranking
            rankings_collection.update_one(
                {'_id': existing['_id']},
                {'$set': ranking_data}
            )
            self._id = existing['_id']
        elif hasattr(self, '_id') and self._id:
            # Update by _id
            rankings_collection.update_one(
                {'_id': self._id},
                {'$set': ranking_data}
            )
        else:
            # Create new ranking
            result = rankings_collection.insert_one(ranking_data)
            self._id = result.inserted_id
        
        return self
    
    def delete(self):
        """Delete ranking from database."""
        rankings_collection = get_collection('rankings')
        if hasattr(self, '_id') and self._id:
            rankings_collection.delete_one({'_id': self._id})
    
    @classmethod
    def find_by_id(cls, ranking_id):
        """Find ranking by ID."""
        rankings_collection = get_collection('rankings')
        if isinstance(ranking_id, str):
            ranking_id = ObjectId(ranking_id)
        ranking_data = rankings_collection.find_one({'_id': ranking_id})
        return cls.from_dict(ranking_data) if ranking_data else None
    
    @classmethod
    def find_by_resume_and_job(cls, resume_id, job_id):
        """Find ranking by resume and job IDs."""
        rankings_collection = get_collection('rankings')
        if isinstance(resume_id, str):
            resume_id = ObjectId(resume_id)
        if isinstance(job_id, str):
            job_id = ObjectId(job_id)
            
        ranking_data = rankings_collection.find_one({
            'resume_id': resume_id,
            'job_id': job_id
        })
        return cls.from_dict(ranking_data) if ranking_data else None
    
    @classmethod
    def get_by_job(cls, job_id, page=1, per_page=10):
        """Get rankings for a specific job."""
        rankings_collection = get_collection('rankings')
        if isinstance(job_id, str):
            job_id = ObjectId(job_id)
        
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get rankings with pagination, sorted by score
        rankings_cursor = rankings_collection.find({'job_id': job_id}).skip(skip).limit(per_page).sort('overall_score', -1)
        rankings = [cls.from_dict(ranking_data) for ranking_data in rankings_cursor]
        
        # Get total count
        total = rankings_collection.count_documents({'job_id': job_id})
        
        return {
            'rankings': rankings,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @classmethod
    def get_by_resume(cls, resume_id):
        """Get rankings for a specific resume."""
        rankings_collection = get_collection('rankings')
        if isinstance(resume_id, str):
            resume_id = ObjectId(resume_id)
            
        rankings_cursor = rankings_collection.find({'resume_id': resume_id}).sort('overall_score', -1)
        return [cls.from_dict(ranking_data) for ranking_data in rankings_cursor]
    
    @classmethod
    def get_all(cls, page=1, per_page=10):
        """Get all rankings with pagination."""
        rankings_collection = get_collection('rankings')
        
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get rankings with pagination
        rankings_cursor = rankings_collection.find().skip(skip).limit(per_page).sort('overall_score', -1)
        rankings = [cls.from_dict(ranking_data) for ranking_data in rankings_cursor]
        
        # Get total count
        total = rankings_collection.count_documents({})
        
        return {
            'rankings': rankings,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def to_dict(self):
        """Convert ranking to dictionary."""
        return {
            'id': str(self._id),
            'resume_id': str(self.resume_id),
            'job_id': str(self.job_id),
            'overall_score': self.overall_score,
            'score_breakdown': self.score_breakdown,
            'algorithm_version': self.algorithm_version,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def id(self):
        """Get string representation of ID."""
        return str(self._id)
    
    def __repr__(self):
        return f'<Ranking Resume:{self.resume_id} Job:{self.job_id} Score:{self.overall_score}>'
