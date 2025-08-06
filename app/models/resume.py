from datetime import datetime
from bson import ObjectId
from database import get_collection

class Resume:
    """Resume model for storing candidate information."""
    
    def __init__(self, filename=None, original_filename=None, file_path=None, 
                 file_size=None, mime_type=None, _id=None, **kwargs):
        self._id = _id or ObjectId()
        self.filename = filename
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.mime_type = mime_type
        
        # Extracted text content
        self.raw_text = kwargs.get('raw_text')
        
        # Parsed structured data
        self.parsed_data = kwargs.get('parsed_data')
        
        # Candidate information
        self.candidate_name = kwargs.get('candidate_name')
        self.candidate_email = kwargs.get('candidate_email')
        self.candidate_phone = kwargs.get('candidate_phone')
        
        # Status and metadata
        self.processing_status = kwargs.get('processing_status', 'pending')
        self.error_message = kwargs.get('error_message')
        
        self.uploaded_at = kwargs.get('uploaded_at', datetime.utcnow())
        self.processed_at = kwargs.get('processed_at')
    
    @classmethod
    def from_dict(cls, data):
        """Create Resume instance from dictionary."""
        return cls(
            _id=data.get('_id'),
            filename=data.get('filename'),
            original_filename=data.get('original_filename'),
            file_path=data.get('file_path'),
            file_size=data.get('file_size'),
            mime_type=data.get('mime_type'),
            raw_text=data.get('raw_text'),
            parsed_data=data.get('parsed_data'),
            candidate_name=data.get('candidate_name'),
            candidate_email=data.get('candidate_email'),
            candidate_phone=data.get('candidate_phone'),
            processing_status=data.get('processing_status', 'pending'),
            error_message=data.get('error_message'),
            uploaded_at=data.get('uploaded_at'),
            processed_at=data.get('processed_at')
        )
    
    def save(self):
        """Save resume to database."""
        resumes_collection = get_collection('resumes')
        
        resume_data = {
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'raw_text': self.raw_text,
            'parsed_data': self.parsed_data,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'candidate_phone': self.candidate_phone,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'uploaded_at': self.uploaded_at,
            'processed_at': self.processed_at
        }
        
        if hasattr(self, '_id') and self._id:
            # Update existing resume
            resumes_collection.update_one(
                {'_id': self._id},
                {'$set': resume_data}
            )
        else:
            # Create new resume
            result = resumes_collection.insert_one(resume_data)
            self._id = result.inserted_id
        
        return self
    
    def delete(self):
        """Delete resume from database."""
        resumes_collection = get_collection('resumes')
        rankings_collection = get_collection('rankings')
        
        if hasattr(self, '_id') and self._id:
            # Delete associated rankings first
            rankings_collection.delete_many({'resume_id': self._id})
            # Delete resume
            resumes_collection.delete_one({'_id': self._id})
    
    @classmethod
    def find_by_id(cls, resume_id):
        """Find resume by ID."""
        resumes_collection = get_collection('resumes')
        if isinstance(resume_id, str):
            resume_id = ObjectId(resume_id)
        resume_data = resumes_collection.find_one({'_id': resume_id})
        return cls.from_dict(resume_data) if resume_data else None
    
    @classmethod
    def get_all(cls, status=None, page=1, per_page=10):
        """Get all resumes with optional filtering and pagination."""
        resumes_collection = get_collection('resumes')
        
        # Build query
        query = {}
        if status:
            query['processing_status'] = status
        
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get resumes with pagination
        resumes_cursor = resumes_collection.find(query).skip(skip).limit(per_page).sort('uploaded_at', -1)
        resumes = [cls.from_dict(resume_data) for resume_data in resumes_cursor]
        
        # Get total count
        total = resumes_collection.count_documents(query)
        
        return {
            'resumes': resumes,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def to_dict(self, include_text=True):
        """Convert resume to dictionary."""
        result = {
            'id': str(self._id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'candidate_phone': self.candidate_phone,
            'processing_status': self.processing_status,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'parsed_data': self.parsed_data
        }
        
        if include_text:
            result['raw_text'] = self.raw_text
            
        return result
    
    @property
    def id(self):
        """Get string representation of ID."""
        return str(self._id)
    
    def __repr__(self):
        return f'<Resume {self.filename}>'
