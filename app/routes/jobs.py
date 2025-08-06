from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from ..models.job import Job
from datetime import datetime

bp = Blueprint('jobs', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_jobs():
    """Get all jobs."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', 'active')
        
        result = Job.get_all(status=status, page=page, per_page=per_page)
        
        return jsonify({
            'jobs': [job.to_dict() for job in result['jobs']],
            'total': result['total'],
            'pages': result['pages'],
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get jobs error: {str(e)}")
        return jsonify({'error': 'Failed to get jobs'}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job."""
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': 'Job title is required'}), 400
        
        # Parse expires_at if provided
        expires_at = data.get('expires_at')
        if expires_at:
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except:
                expires_at = None
        
        job = Job(
            title=data.get('title'),
            description=data.get('description', ''),
            company=data.get('company', ''),
            location=data.get('location', ''),
            employment_type=data.get('employment_type', 'full-time'),
            requirements=data.get('requirements', {}),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            currency=data.get('currency', 'USD'),
            priority=data.get('priority', 1),
            expires_at=expires_at
        )
        
        job.save()
        
        return jsonify({
            'message': 'Job created successfully',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Create job error: {str(e)}")
        return jsonify({'error': 'Failed to create job'}), 500

@bp.route('/<job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    """Get specific job."""
    try:
        job = Job.find_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(job.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Get job error: {str(e)}")
        return jsonify({'error': 'Failed to get job'}), 500

@bp.route('/<job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update a job."""
    try:
        job = Job.find_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            job.title = data['title']
        if 'description' in data:
            job.description = data['description']
        if 'company' in data:
            job.company = data['company']
        if 'location' in data:
            job.location = data['location']
        if 'employment_type' in data:
            job.employment_type = data['employment_type']
        if 'requirements' in data:
            job.requirements = data['requirements']
        if 'salary_min' in data:
            job.salary_min = data['salary_min']
        if 'salary_max' in data:
            job.salary_max = data['salary_max']
        if 'currency' in data:
            job.currency = data['currency']
        if 'status' in data:
            job.status = data['status']
        if 'priority' in data:
            job.priority = data['priority']
        if 'expires_at' in data:
            expires_at = data['expires_at']
            if expires_at:
                try:
                    job.expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                except:
                    job.expires_at = None
            else:
                job.expires_at = None
        
        job.save()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update job error: {str(e)}")
        return jsonify({'error': 'Failed to update job'}), 500

@bp.route('/<job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """Delete a job."""
    try:
        job = Job.find_by_id(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        job.delete()
        
        return jsonify({'message': 'Job deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete job error: {str(e)}")
        return jsonify({'error': 'Failed to delete job'}), 500
