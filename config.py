#!/usr/bin/env python3
"""
Configuration module for HR Resume System
Loads and manages all environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # Application Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS').split(',')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH'))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    
    # LLM Configuration (Optional)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL')
    
    # Application Settings
    FLASK_ENV = os.getenv('FLASK_ENV')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    @classmethod
    def get_mongodb_uri(cls):
        """Get MongoDB connection string."""
        return cls.MONGODB_URI
    
    @classmethod
    def get_secret_key(cls):
        """Get Flask secret key."""
        return cls.SECRET_KEY
    
    @classmethod
    def get_jwt_secret_key(cls):
        """Get JWT secret key."""
        return cls.JWT_SECRET_KEY
    
    @classmethod
    def get_cors_origins(cls):
        """Get CORS origins list."""
        return cls.CORS_ORIGINS
    
    @classmethod
    def get_upload_config(cls):
        """Get file upload configuration."""
        return {
            'max_content_length': cls.MAX_CONTENT_LENGTH,
            'upload_folder': cls.UPLOAD_FOLDER
        }
    
    @classmethod
    def get_llm_config(cls):
        """Get LLM configuration."""
        return {
            'groq_api_key': cls.GROQ_API_KEY,
            'openai_model': cls.OPENAI_MODEL
        }
    
    @classmethod
    def is_production(cls):
        """Check if running in production mode."""
        return cls.FLASK_ENV == 'production'
    
    @classmethod
    def is_debug(cls):
        """Check if debug mode is enabled."""
        return cls.DEBUG

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default']) 