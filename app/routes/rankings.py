from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from ..models.resume import Resume
from ..models.job import Job
from ..models.ranking import Ranking
from ..utils.ranking_algorithm import calculate_ranking

bp = Blueprint('rankings', __name__)

@bp.route('/', methods=['POST'])
@jwt_required()
def create_rankings():
    """Create rankings for a job."""
    try:
        data = request.get_json()
        if not data or not data.get('job_id'):
            return jsonify({'error': 'Job ID is required'}), 400
        
        job_id = data.get('job_id')
        job = Job.find_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get all completed resumes
        result = Resume.get_all(status='completed', page=1, per_page=1000)  # Get all completed resumes
        resumes = result['resumes']
        
        if not resumes:
            return jsonify({'error': 'No processed resumes found'}), 400
        
        rankings = []
        
        for resume in resumes:
            try:
                # Calculate ranking score
                score_data = calculate_ranking(resume, job)
                
                # Check if ranking already exists
                existing_ranking = Ranking.find_by_resume_and_job(resume.id, job.id)
                
                if existing_ranking:
                    # Update existing ranking
                    existing_ranking.overall_score = score_data['overall_score']
                    existing_ranking.score_breakdown = score_data['score_breakdown']
                    existing_ranking.confidence_score = score_data['confidence_score']
                    ranking = existing_ranking
                else:
                    # Create new ranking
                    ranking = Ranking(
                        resume_id=resume.id,
                        job_id=job.id,
                        overall_score=score_data['overall_score'],
                        score_breakdown=score_data['score_breakdown'],
                        confidence_score=score_data['confidence_score'],
                        algorithm_version='1.0'
                    )
                
                ranking.save()
                
                rankings.append(ranking)
                
            except Exception as e:
                current_app.logger.error(f"Error ranking resume {resume.id}: {str(e)}")
                continue
        
        # Sort rankings by score
        rankings.sort(key=lambda x: x.overall_score, reverse=True)
        
        return jsonify({
            'message': f'Rankings calculated for {len(rankings)} resumes',
            'rankings': [ranking.to_dict() for ranking in rankings]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Create rankings error: {str(e)}")
        return jsonify({'error': 'Failed to create rankings'}), 500

@bp.route('/job/<job_id>', methods=['GET'])
@jwt_required()
def get_job_rankings(job_id):
    """Get rankings for a specific job."""
    try:
        job = Job.find_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        rankings_result = Ranking.get_by_job(job_id, page=page, per_page=per_page)
        
        # Include resume information
        result = []
        for ranking in rankings_result['rankings']:
            ranking_dict = ranking.to_dict()
            resume = Resume.find_by_id(ranking.resume_id)
            if resume:
                ranking_dict['resume'] = resume.to_dict()
            result.append(ranking_dict)
        
        return jsonify({
            'job': job.to_dict(),
            'rankings': result,
            'total': rankings_result['total'],
            'pages': rankings_result['pages'],
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get job rankings error: {str(e)}")
        return jsonify({'error': 'Failed to get job rankings'}), 500

@bp.route('/resume/<resume_id>', methods=['GET'])
@jwt_required()
def get_resume_rankings(resume_id):
    """Get rankings for a specific resume."""
    try:
        resume = Resume.find_by_id(resume_id)
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        rankings = Ranking.get_by_resume(resume_id)
        
        # Include job information
        result = []
        for ranking in rankings:
            ranking_dict = ranking.to_dict()
            job = Job.find_by_id(ranking.job_id)
            if job:
                ranking_dict['job'] = job.to_dict()
            result.append(ranking_dict)
        
        return jsonify({
            'resume': resume.to_dict(),
            'rankings': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get resume rankings error: {str(e)}")
        return jsonify({'error': 'Failed to get resume rankings'}), 500

@bp.route('/<ranking_id>', methods=['DELETE'])
@jwt_required()
def delete_ranking(ranking_id):
    """Delete a ranking."""
    try:
        ranking = Ranking.find_by_id(ranking_id)
        if not ranking:
            return jsonify({'error': 'Ranking not found'}), 404
        
        ranking.delete()
        
        return jsonify({'message': 'Ranking deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete ranking error: {str(e)}")
        return jsonify({'error': 'Failed to delete ranking'}), 500
