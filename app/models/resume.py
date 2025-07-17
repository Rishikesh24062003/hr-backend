from datetime import datetime
from .. import db

class Resume(db.Model):
    """Resume model for storing candidate information."""
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Extracted text content
    raw_text = db.Column(db.Text)
    
    # Parsed structured data
    parsed_data = db.Column(db.JSON)
    
    # Candidate information
    candidate_name = db.Column(db.String(255))
    candidate_email = db.Column(db.String(255))
    candidate_phone = db.Column(db.String(50))
    
    # Status and metadata
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    rankings = db.relationship('Ranking', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_text=True):
        """Convert resume to dictionary."""
        result = {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'candidate_phone': self.candidate_phone,
            'processing_status': self.processing_status,
            'uploaded_at': self.uploaded_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'parsed_data': self.parsed_data
        }
        
        if include_text:
            result['raw_text'] = self.raw_text
            
        return result
    
    def __repr__(self):
        return f'<Resume {self.filename}>'
