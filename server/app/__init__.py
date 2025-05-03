from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from datetime import timedelta
import os

# Initialize extensions
limiter = Limiter(key_func=lambda: "global")

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')
    app.config['CACHE_TYPE'] = 'SimpleCache'  # Use in-memory cache instead of file cache

    # Create session directory if it doesn't exist
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

    # Initialize extensions
    CORS(app)
    limiter.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.spotify import spotify_bp
    from app.playlist import playlist_bp
    from app.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(spotify_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(search_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500

    return app
