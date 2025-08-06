import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import init_db, close_db
from config import Config

# Initialize extensions
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    load_dotenv()  # Load .env variables
    
    app = Flask(__name__)
    
    # Configuration using centralized config
    app.config.from_mapping(
        SECRET_KEY=Config.get_secret_key(),
        MONGODB_URI=Config.get_mongodb_uri(),
        JWT_SECRET_KEY=Config.get_jwt_secret_key(),
        JWT_ACCESS_TOKEN_EXPIRES=Config.JWT_ACCESS_TOKEN_EXPIRES,
        UPLOAD_FOLDER=os.path.join(app.root_path, '..', Config.UPLOAD_FOLDER),
        MAX_CONTENT_LENGTH=Config.MAX_CONTENT_LENGTH,
    )
    
    # Initialize extensions
    jwt.init_app(app)
    
    # Configure CORS using centralized config
    cors_origins = Config.get_cors_origins()
    print(f"DEBUG: CORS Origins are {cors_origins}")
    
    # More comprehensive CORS configuration for Vercel
    CORS(app, 
         origins=cors_origins,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True,
         max_age=3600)
    
    # Add CORS preflight handler
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)
    
    # Initialize MongoDB
    with app.app_context():
        init_db()
    
    return app
