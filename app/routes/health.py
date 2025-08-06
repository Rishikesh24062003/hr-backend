from flask import Blueprint, jsonify

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "HR Resume System API is running",
        "version": "1.0.0"
    }), 200

@bp.route('/', methods=['GET'])
def root():
    """Root endpoint."""
    return jsonify({
        "message": "HR Resume System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/api/auth",
            "resumes": "/api/resumes",
            "jobs": "/api/jobs",
            "rankings": "/api/rankings",
            "analytics": "/api/analytics",
            "llm": "/api/llm"
        }
    }), 200 