from flask import Blueprint, redirect, request, session, url_for, jsonify, make_response
import os, requests
from urllib.parse import urlencode
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPES = "user-read-private user-read-email user-top-read"

@auth_bp.route('/login')
def login():
    auth_url = (
        "https://accounts.spotify.com/authorize"
        "?client_id={client_id}"
        "&response_type=code"
        "&redirect_uri={redirect_uri}"
        "&scope={scopes}"
    ).format(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scopes="user-read-private user-read-email user-top-read"
    )
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI'),
        'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
        'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET')
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to obtain token"}, 400

    data = response.json()
    session['access_token'] = data['access_token']
    session['refresh_token'] = data.get('refresh_token')
    
    # Store token expiration time as naive datetime
    expires_in = data.get('expires_in', 3600)
    session['expires_at'] = datetime.now() + timedelta(seconds=expires_in)
    
    return redirect("http://localhost:3000/search")

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear all session data
    session.clear()
    
    # Create a response with redirect
    response = make_response(redirect("http://localhost:3000/home"))
    
    # Set security headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Clear any cookies
    response.delete_cookie('session')
    
    return response

@auth_bp.route('/auth-status')
def auth_status():
    """Debug endpoint to check authentication status"""
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    expires_at = session.get('expires_at')
    
    # Handle datetime comparison safely
    token_expired = False
    if expires_at:
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
        
        token_expired = datetime.now() > expires_at
    
    status = {
        'authenticated': bool(access_token),
        'has_refresh_token': bool(refresh_token),
        'token_expires_at': str(expires_at) if expires_at else None,
        'token_expired': token_expired
    }
    
    return jsonify(status)
