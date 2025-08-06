#!/usr/bin/env python3
"""
Test script to verify environment variable loading
"""

import os
from dotenv import load_dotenv
from config import Config

def test_environment_loading():
    """Test environment variable loading."""
    print("🔧 Testing environment variable loading...")
    
    # Load environment variables
    load_dotenv()
    
    print("\n📋 Environment Variables:")
    print(f"MONGODB_URI: {'✅ Set' if os.getenv('MONGODB_URI') else '❌ Not set'}")
    print(f"SECRET_KEY: {'✅ Set' if os.getenv('SECRET_KEY') else '❌ Not set'}")
    print(f"JWT_SECRET_KEY: {'✅ Set' if os.getenv('JWT_SECRET_KEY') else '❌ Not set'}")
    print(f"CORS_ORIGINS: {'✅ Set' if os.getenv('CORS_ORIGINS') else '❌ Not set'}")
    print(f"GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Not set (optional)'}")
    
    print("\n🔧 Configuration Values:")
    print(f"MongoDB URI: {Config.get_mongodb_uri()[:50]}...")
    print(f"Secret Key: {Config.get_secret_key()[:20]}...")
    print(f"JWT Secret: {Config.get_jwt_secret_key()[:20]}...")
    print(f"CORS Origins: {Config.get_cors_origins()}")
    print(f"Upload Config: {Config.get_upload_config()}")
    print(f"LLM Config: {Config.get_llm_config()}")
    print(f"Environment: {Config.FLASK_ENV}")
    print(f"Debug Mode: {Config.is_debug()}")
    
    print("\n✅ Environment loading test complete!")

if __name__ == "__main__":
    test_environment_loading() 