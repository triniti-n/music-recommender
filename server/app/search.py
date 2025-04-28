from flask import Blueprint, jsonify, request, session
import requests
import os
from datetime import datetime, timedelta
import base64

search_bp = Blueprint('search', __name__)

def save_search(query, search_type):
    session_id = session.get('session_id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    new_search = SearchHistory(
        session_id=session_id,
        query=query,
        search_type=search_type
    )
    db.session.add(new_search)
    db.session.commit()

# Helper to get the access token from session and refresh if needed
def get_headers():
    access_token = session.get('access_token')
    expires_at = session.get('expires_at')
    
    # Debug logging
    print('Session data:', {
        'access_token': 'present' if access_token else 'missing',
        'expires_at': expires_at,
        'session_id': session.get('session_id')
    })
    
    # Check if token is missing
    if not access_token:
        print('Error: Access token not found in session')
        return None
    
    # Check if token is expired or about to expire (within 5 minutes)
    if expires_at:
        # Convert string to datetime if needed
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                print('Error: Invalid expires_at format')
                return None
        
        # Ensure both datetimes are naive (no timezone)
        current_time = datetime.now()
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
        
        if current_time > expires_at - timedelta(minutes=5):
            print('Token expired or about to expire, refreshing...')
            refresh_token = session.get('refresh_token')
            if not refresh_token:
                print('Error: Refresh token not found in session')
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
                    print(f'Error refreshing token: {response.status_code}')
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
                print(f'Exception refreshing token: {e}')
                return None
    
    return {"Authorization": f"Bearer {access_token}"}

def not_header():
    print('Error: Not authenticated')
    return jsonify({'error': 'Not authenticated'}), 401

@search_bp.route('/api/spotify/search', methods=['GET'])
def search():
    print('Search request received:', {
        'headers': dict(request.headers),
        'cookies': dict(request.cookies),
        'args': dict(request.args)
    })
    
    headers = get_headers()
    if not headers:
        return not_header()
    query = request.args.get('q')
    type_ = request.args.get('type', 'track,artist')
    if not query:
        return jsonify({'error': 'Missing search query'}), 400
    save_search(query, type_)
    params = {
        'q': query,
        'type': type_,
        'limit': 10
    }
    try:
        r = requests.get(
            'https://api.spotify.com/v1/search',
            headers=headers,
            params=params
        )
        r.raise_for_status()
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        print('Spotify search error:', e)
        return jsonify({'error': 'Failed to search Spotify'}), 500

@search_bp.route('/api/spotify/search/tracks', methods=['GET'])
def search_tracks():
    headers = get_headers()
    if not headers:
        return not_header()
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing search query'}), 400
    save_search(query, 'track')
    params = {
        'q': query,
        'type': 'track',
        'limit': 10
    }
    try:
        r = requests.get(
            'https://api.spotify.com/v1/search',
            headers=headers,
            params=params
        )
        r.raise_for_status()
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        print('Spotify search error:', e)
        return jsonify({'error': 'Failed to search Spotify'}), 500

@search_bp.route('/api/spotify/search/artists', methods=['GET'])
def search_artists():
    headers = get_headers()
    if not headers:
        return not_header()
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing search query'}), 400
    save_search(query, 'artist')
    params = {
        'q': query,
        'type': 'artist',
        'limit': 10
    }
    try:
        r = requests.get(
            'https://api.spotify.com/v1/search',
            headers=headers,
            params=params
        )
        r.raise_for_status()
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        print('Spotify search error:', e)
        return jsonify({'error': 'Failed to search Spotify'}), 500

@search_bp.route('/api/search', methods=['GET'])
def public_search():
    query = request.args.get('q')
    type_ = request.args.get('type', 'track,artist')
    if not query:
        return jsonify({'error': 'Missing search query'}), 400
    
    # Get Spotify access token from environment variables
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return jsonify({'error': 'Spotify credentials not configured'}), 500
    
    # Get access token using client credentials flow
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_data = {
        'grant_type': 'client_credentials'
    }
    auth_header = {
        'Authorization': 'Basic ' + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Get access token
        print("Attempting to get access token...")
        auth_response = requests.post(auth_url, data=auth_data, headers=auth_header)
        print(f"Auth response status: {auth_response.status_code}")
        print(f"Auth response: {auth_response.text}")
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']
        
        # Search Spotify
        search_url = 'https://api.spotify.com/v1/search'
        search_params = {
            'q': query,
            'type': type_,
            'limit': 10
        }
        search_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("Attempting to search Spotify...")
        search_response = requests.get(search_url, params=search_params, headers=search_headers)
        print(f"Search response status: {search_response.status_code}")
        print(f"Search response: {search_response.text}")
        search_response.raise_for_status()
        
        return jsonify(search_response.json())
        
    except requests.exceptions.RequestException as e:
        error_details = {
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None),
            'response_text': getattr(e.response, 'text', None)
        }
        print(f"Error searching Spotify: {error_details}")
        return jsonify({'error': 'Failed to search Spotify', 'details': error_details}), 500
