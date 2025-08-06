import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import init_db, close_db

# Initialize extensions
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    load_dotenv()  # Load .env variables
    
    app = Flask(__name__)
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key'),
        MONGODB_URI=os.getenv('MONGODB_URI', 'mongodb+srv://rishikeshmishra477:LKXmeF6EWDi1pKeh@cluster0.s0xf7bg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'jwt-secret-key'),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600')),
        UPLOAD_FOLDER=os.path.join(app.root_path, '..', 'uploads'),
        MAX_CONTENT_LENGTH=int(os.getenv('MAX_CONTENT_LENGTH', '16777216')),
    )
    
    # Initialize extensions
    jwt.init_app(app)
    
    # Configure CORS
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    print(f"DEBUG: CORS Origins are {cors_origins}")
    CORS(app, origins=cors_origins)
    
    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)
    
    # Initialize MongoDB
    with app.app_context():
        init_db()
    
    return app
