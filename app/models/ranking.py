from datetime import datetime
from .. import db

class Ranking(db.Model):
    """Ranking model for storing candidate-job match scores."""
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    
    # Scoring information
    overall_score = db.Column(db.Float, nullable=False)
    
    # Detailed scores (stored as JSON)
    score_breakdown = db.Column(db.JSON)
    
    # Ranking metadata
    algorithm_version = db.Column(db.String(50), default='1.0')
    confidence_score = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('resume_id', 'job_id', name='unique_resume_job_ranking'),
    )
    
    def to_dict(self):
        """Convert ranking to dictionary."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'overall_score': self.overall_score,
            'score_breakdown': self.score_breakdown,
            'algorithm_version': self.algorithm_version,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Ranking Resume:{self.resume_id} Job:{self.job_id} Score:{self.overall_score}>'
