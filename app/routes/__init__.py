from flask import Blueprint
from .auth import bp as auth_bp
from .resumes import bp as resumes_bp
from .jobs import bp as jobs_bp
from .rankings import bp as rankings_bp
from .analytics import bp as analytics_bp
from .llm import bp as llm_bp
from dotenv import load_dotenv
load_dotenv()


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(resumes_bp, url_prefix='/api/resumes')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(rankings_bp, url_prefix='/api/rankings')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(llm_bp, url_prefix='/api/llm')

