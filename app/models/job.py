from datetime import datetime
from .. import db

class Job(db.Model):
    """Job model for storing job postings and requirements."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    company = db.Column(db.String(200))
    location = db.Column(db.String(200))
    employment_type = db.Column(db.String(50))  # full-time, part-time, contract, etc.
    
    # Job requirements (stored as JSON)
    requirements = db.Column(db.JSON)
    
    # Salary information
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    
    # Status and metadata
    status = db.Column(db.String(50), default='active')  # active, paused, closed
    priority = db.Column(db.Integer, default=1)  # 1-5 priority scale
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    rankings = db.relationship('Ranking', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert job to dictionary."""
        return {
            'id': self.id,
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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def __repr__(self):
        return f'<Job {self.title}>'
