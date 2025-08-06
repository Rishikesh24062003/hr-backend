from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from ..models.resume import Resume
from ..models.job import Job
from ..models.ranking import Ranking
from database import get_collection

bp = Blueprint('analytics', __name__)

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get basic system statistics."""
    try:
        resumes_collection = get_collection('resumes')
        jobs_collection = get_collection('jobs')
        rankings_collection = get_collection('rankings')
        
        stats = {
            'resumes': resumes_collection.count_documents({}),
            'jobs': jobs_collection.count_documents({}),
            'rankings': rankings_collection.count_documents({}),
            'active_jobs': jobs_collection.count_documents({'status': 'active'}),
            'processed_resumes': resumes_collection.count_documents({'processing_status': 'completed'}),
            'failed_resumes': resumes_collection.count_documents({'processing_status': 'failed'})
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
        resumes_collection = get_collection('resumes')
        jobs_collection = get_collection('jobs')
        rankings_collection = get_collection('rankings')
        
        # Job statistics
        job_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        job_stats = list(jobs_collection.aggregate(job_pipeline))
        
        # Resume processing statistics
        resume_pipeline = [
            {"$group": {"_id": "$processing_status", "count": {"$sum": 1}}}
        ]
        resume_stats = list(resumes_collection.aggregate(resume_pipeline))
        
        # Top scoring rankings with resume and job info
        top_rankings_pipeline = [
            {"$sort": {"overall_score": -1}},
            {"$limit": 10},
            {"$lookup": {
                "from": "resumes",
                "localField": "resume_id",
                "foreignField": "_id",
                "as": "resume"
            }},
            {"$lookup": {
                "from": "jobs",
                "localField": "job_id",
                "foreignField": "_id",
                "as": "job"
            }},
            {"$unwind": {"path": "$resume", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$job", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "overall_score": 1,
                "candidate_name": "$resume.candidate_name",
                "job_title": "$job.title"
            }}
        ]
        top_rankings = list(rankings_collection.aggregate(top_rankings_pipeline))
        
        # Average scores by job
        avg_scores_pipeline = [
            {"$lookup": {
                "from": "jobs",
                "localField": "job_id",
                "foreignField": "_id",
                "as": "job"
            }},
            {"$unwind": {"path": "$job", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": "$job_id",
                "job_title": {"$first": "$job.title"},
                "avg_score": {"$avg": "$overall_score"},
                "candidate_count": {"$sum": 1}
            }}
        ]
        avg_scores = list(rankings_collection.aggregate(avg_scores_pipeline))
        
        return jsonify({
            'job_statistics': [{'status': stat['_id'], 'count': stat['count']} for stat in job_stats],
            'resume_statistics': [{'status': stat['_id'], 'count': stat['count']} for stat in resume_stats],
            'top_rankings': [
                {
                    'score': ranking['overall_score'],
                    'candidate': ranking.get('candidate_name', 'Unknown'),
                    'job': ranking.get('job_title', 'Unknown')
                }
                for ranking in top_rankings
            ],
            'average_scores': [
                {
                    'job': score.get('job_title', 'Unknown'),
                    'avg_score': float(score['avg_score']) if score['avg_score'] else 0,
                    'candidate_count': score['candidate_count']
                }
                for score in avg_scores
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reports error: {str(e)}")
        return jsonify({'error': 'Failed to get reports'}), 500

@bp.route('/job-performance/<job_id>', methods=['GET'])
@jwt_required()
def get_job_performance(job_id):
    """Get performance analytics for a specific job."""
    try:
        job = Job.find_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get all rankings for this job
        rankings_result = Ranking.get_by_job(job_id, page=1, per_page=1000)  # Get all rankings
        rankings = rankings_result['rankings']
        
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
        
        # Top candidates - get top 5 rankings with resume info
        top_rankings = sorted(rankings, key=lambda x: x.overall_score, reverse=True)[:5]
        top_candidates = []
        
        for ranking in top_rankings:
            resume = Resume.find_by_id(ranking.resume_id)
            if resume:
                top_candidates.append({
                    'name': resume.candidate_name or 'Unknown',
                    'email': resume.candidate_email or 'Unknown',
                    'score': ranking.overall_score
                })
        
        return jsonify({
            'job': job.to_dict(),
            'performance': {
                'total_candidates': len(rankings),
                'avg_score': sum(scores) / len(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'score_distribution': distribution,
                'top_candidates': top_candidates
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get job performance error: {str(e)}")
        return jsonify({'error': 'Failed to get job performance'}), 500
