import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
      SECRET_KEY=os.getenv("SECRET_KEY","dev"),
      SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL","sqlite:///hr_system.db"),
      SQLALCHEMY_TRACK_MODIFICATIONS=False,
      JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY","jwt-secret"),
      JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES","3600"))
    )
    CORS(app, origins=["http://localhost:3000","http://localhost:5173"], resources={r"/api/*":{"origins":["*"]}})
    db.init_app(app)
    jwt.init_app(app)
    from models.user import User
    from models.resume import Resume
    from models.job import Job
    from models.ranking import Ranking
    from routes import register_blueprints
    register_blueprints(app)
    with app.app_context():
        db.create_all()
    return app
