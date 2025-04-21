from flask import Blueprint, jsonify, request, session
import requests
import os
from datetime import datetime, timedelta

spotify_bp = Blueprint('spotify', __name__)

def get_headers():
    access_token = session.get('access_token')
    expires_at = session.get('expires_at')
    
    # Check if token is missing
    if not access_token:
        return None
    
    # Check if token is expired or about to expire (within 5 minutes)
    if expires_at:
        # Convert string to datetime if needed
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                return None
        
        # Ensure both datetimes are naive (no timezone)
        current_time = datetime.now()
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
        
        if current_time > expires_at - timedelta(minutes=5):
            refresh_token = session.get('refresh_token')
            if not refresh_token:
                return None
                
            # Refresh the token
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
                "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
            }
            
            try:
                response = requests.post("https://accounts.spotify.com/api/token", data=payload)
                if response.status_code != 200:
                    return None
                    
                tokens = response.json()
                session['access_token'] = tokens.get('access_token')
                # Store as naive datetime
                session['expires_at'] = datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600))
                
                # If a new refresh token was provided, update it
                if 'refresh_token' in tokens:
                    session['refresh_token'] = tokens['refresh_token']
                    
                access_token = tokens.get('access_token')
            except Exception as e:
                return None
    
    return {"Authorization": f"Bearer {access_token}"}

@spotify_bp.route('/api/spotify/me')
def get_profile():
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return jsonify(r.json())

@spotify_bp.route('/api/spotify/search')
def search():
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    query = request.args.get('q')
    types = request.args.get('type', 'track,artist')
    
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    params = {
        'q': query,
        'type': types,
        'limit': 5
    }
    
    r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    return jsonify(r.json())

@spotify_bp.route('/api/spotify/refresh-token', methods=['POST'])
def refresh_token():
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'No refresh token'}), 401
    
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
    }
    
    r = requests.post("https://accounts.spotify.com/api/token", data=payload)
    tokens = r.json()
    
    session['access_token'] = tokens.get('access_token')
    session['expires_at'] = datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600))
    
    return jsonify(tokens)
