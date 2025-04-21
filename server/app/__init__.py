from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os

# Initialize extensions
db = SQLAlchemy()
limiter = Limiter(key_func=lambda: "global")

def create_app():
    main = Flask(__name__)
    
    # Load configuration
    main.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(main)
    CORS(main)
    limiter.init_app(main)
    
    # Register blueprints
    from app.auth import auth_bp
    from app.spotify import spotify_bp
    from app.recommend import recommend_bp
    from app.playlist import playlist_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(spotify_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(playlist_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500
    
    return app
