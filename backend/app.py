from flask import Flask, redirect, url_for
from flask_limiter import Limiter
import os
from datetime import timedelta
from auth.routes import auth_bp
from api.spotify import spotify_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Set session TTL
app.permanent_session_lifetime = timedelta(hours=1)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPES = "user-read-private user-read-email user-top-read"
SHOW_DIALOG = "true"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(spotify_bp)

@app.route('/')
def home():
    # Optionally, render a landing page or redirect to frontend
    return "Backend is running."

@app.route('/signin')
def signin():
    # Start the Spotify OAuth flow (handled by auth.login) and after auth, redirect to dashboard
    return redirect(url_for('auth.login'))

@app.route('/spotify-connect')
def spotify_connect():
    # Start the Spotify OAuth flow (handled by auth.login) and after auth, redirect to dashboard
    return redirect(url_for('auth.login'))

@app.route('/callback')
def callback():
    # Handle the callback from Spotify
    return redirect("http://localhost:3000/dashboard")

@app.after_request
def after_request(response):
    # Security headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/api/spotify/refresh-token', methods=['POST'])
def refresh_token():
    # Handle token refresh logic here
    return "Token refreshed successfully", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)