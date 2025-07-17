import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    load_dotenv()  # Load .env variables
    
    app = Flask(__name__)
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///hr_system.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'jwt-secret-key'),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600')),
        UPLOAD_FOLDER=os.path.join(app.root_path, '..', 'uploads'),
        MAX_CONTENT_LENGTH=int(os.getenv('MAX_CONTENT_LENGTH', '16777216')),
    )
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    print(f"DEBUG: CORS Origins are {cors_origins}")
    CORS(app, origins=cors_origins)
    
    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)
    
    # Create database tables and default admin user
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from .models.user import User
        if not User.query.filter_by(email='admin@example.com').first():
            admin_user = User(email='admin@example.com', role='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
    
    return app
