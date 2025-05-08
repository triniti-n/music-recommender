from flask import Flask, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_session import Session
from datetime import datetime
import os
import logging

def create_app():
    app = Flask(__name__)

    # Load configuration
    from .config import Config
    app.config.from_object(Config)

    # Create and set session directory
    session_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache', 'sessions')
    os.makedirs(session_dir, exist_ok=True)
    app.config['SESSION_FILE_DIR'] = session_dir

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Make sessions non-permanent by default (browser session only)
    @app.before_request
    def make_session_non_permanent():
        session.permanent = False

    # Initialize extensions
    CORS(app, resources={
        r"/*": {  # Allow all routes, not just /api/*
            "origins": ["http://localhost:3000"],
            "supports_credentials": True,
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize Flask-Session with error handling
    try:
        Session(app)
        logging.info(f"Session initialized with directory: {app.config['SESSION_FILE_DIR']}")
    except Exception as e:
        logging.error(f"Error initializing session: {str(e)}")
        # Fallback to in-memory session if filesystem session fails
        app.config['SESSION_TYPE'] = 'null'
        Session(app)
        logging.info("Fallback to null session type")

    # Debug route to check session
    @app.route('/debug-session')
    def debug_session():
        return {
            'session_keys': list(session.keys()),
            'has_access_token': 'access_token' in session,
            'session_id': session.get('_id', 'No ID')
        }

    # Register blueprints
    from .spotify import spotify_bp
    from .search import search_bp
    from .auth import auth_bp
    from .playlist import playlist_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(spotify_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(playlist_bp)

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