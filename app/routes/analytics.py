from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from ..models.resume import Resume
from ..models.job import Job
from ..models.ranking import Ranking
from .. import db

bp = Blueprint('analytics', __name__)

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get basic system statistics."""
    try:
        stats = {
            'resumes': Resume.query.count(),
            'jobs': Job.query.count(),
            'rankings': Ranking.query.count(),
            'active_jobs': Job.query.filter_by(status='active').count(),
            'processed_resumes': Resume.query.filter_by(processing_status='completed').count(),
            'failed_resumes': Resume.query.filter_by(processing_status='failed').count()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Get stats error: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get detailed analytics reports."""
    try:
        # Job statistics
        job_stats = db.session.query(
            Job.status,
            func.count(Job.id).label('count')
        ).group_by(Job.status).all()
        
        # Resume processing statistics
        resume_stats = db.session.query(
            Resume.processing_status,
            func.count(Resume.id).label('count')
        ).group_by(Resume.processing_status).all()
        
        # Top scoring rankings
        top_rankings = db.session.query(
            Ranking.overall_score,
            Resume.candidate_name,
            Job.title
        ).join(Resume).join(Job).order_by(
            Ranking.overall_score.desc()
        ).limit(10).all()
        
        # Average scores by job
        avg_scores = db.session.query(
            Job.title,
            func.avg(Ranking.overall_score).label('avg_score'),
            func.count(Ranking.id).label('candidate_count')
        ).join(Ranking).group_by(Job.id, Job.title).all()
        
        return jsonify({
            'job_statistics': [{'status': stat[0], 'count': stat[1]} for stat in job_stats],
            'resume_statistics': [{'status': stat[0], 'count': stat[1]} for stat in resume_stats],
            'top_rankings': [
                {
                    'score': ranking[0],
                    'candidate': ranking[1],
                    'job': ranking[2]
                }
                for ranking in top_rankings
            ],
            'average_scores': [
                {
                    'job': score[0],
                    'avg_score': float(score[1]) if score[1] else 0,
                    'candidate_count': score[2]
                }
                for score in avg_scores
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reports error: {str(e)}")
        return jsonify({'error': 'Failed to get reports'}), 500

@bp.route('/job-performance/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_performance(job_id):
    """Get performance analytics for a specific job."""
    try:
        job = Job.query.get_or_404(job_id)
        
        # Get all rankings for this job
        rankings = Ranking.query.filter_by(job_id=job_id).all()
        
        if not rankings:
            return jsonify({
                'job': job.to_dict(),
                'performance': {
                    'total_candidates': 0,
                    'avg_score': 0,
                    'score_distribution': [],
                    'top_candidates': []
                }
            }), 200
        
        scores = [r.overall_score for r in rankings]
        
        # Score distribution
        score_ranges = [
            (0.0, 0.2, 'Poor'),
            (0.2, 0.4, 'Below Average'),
            (0.4, 0.6, 'Average'),
            (0.6, 0.8, 'Good'),
            (0.8, 1.0, 'Excellent')
        ]
        
        distribution = []
        for min_score, max_score, label in score_ranges:
            count = sum(1 for score in scores if min_score <= score < max_score)
            distribution.append({
                'range': label,
                'count': count,
                'percentage': (count / len(scores)) * 100 if scores else 0
            })
        
        # Top candidates
        top_candidates = db.session.query(
            Ranking.overall_score,
            Resume.candidate_name,
            Resume.candidate_email
        ).join(Resume).filter(
            Ranking.job_id == job_id
        ).order_by(
            Ranking.overall_score.desc()
        ).limit(5).all()
        
        return jsonify({
            'job': job.to_dict(),
            'performance': {
                'total_candidates': len(rankings),
                'avg_score': sum(scores) / len(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'score_distribution': distribution,
                'top_candidates': [
                    {
                        'name': candidate[1],
                        'email': candidate[2],
                        'score': candidate[0]
                    }
                    for candidate in top_candidates
                ]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get job performance error: {str(e)}")
        return jsonify({'error': 'Failed to get job performance'}), 500
