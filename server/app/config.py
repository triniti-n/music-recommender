import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///music_recommender.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
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