import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-music-recommender-secret-key-change-in-prod')
    if SECRET_KEY == 'your-secret-key':
        print('Warning: Using default insecure SECRET_KEY. Set a secure key via environment variable.')

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # Short session lifetime
    SESSION_COOKIE_SECURE = False  # Set to False for local development; enable in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protect against CSRF
    SESSION_REFRESH_EACH_REQUEST = True  # Refresh session on each request
    SESSION_TYPE = 'filesystem'  # Store sessions in the filesystem
    # Note: SESSION_FILE_DIR is set in main.py to ensure directory exists
    SESSION_FILE_THRESHOLD = 500  # Limit number of session files
    SESSION_USE_SIGNER = True  # Sign the session cookie for security
    SESSION_PERMANENT = False  # Make sessions non-permanent by default (browser session only)

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_HEADERS_ENABLED = True

    # Spotify
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')
    SPOTIFY_SCOPES = 'user-read-private user-read-email user-top-read'

    # Frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    # CORS
    CORS_HEADERS = 'Content-Type'

    # Debug
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'