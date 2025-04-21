from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from datetime import datetime
import os
from .models import db

def create_app():
    app = Flask(__name__)

    # Load configuration
    from .config import Config
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "supports_credentials": True
        }
    })
    db.init_app(app)

    # Register blueprints
    from .spotify import spotify_bp
    from .playlist import playlist_bp
    from .search import search_bp
    from .auth import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(spotify_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(search_bp)

    # Error handlersfix
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)