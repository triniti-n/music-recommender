from flask import Blueprint, jsonify, request, session
import requests

playlist_bp = Blueprint('playlist', __name__)

def get_headers():
    access_token = session.get('access_token')
    if not access_token:
        return None
    return {"Authorization": f"Bearer {access_token}"}

@playlist_bp.route('/api/playlists/create', methods=['POST'])
def create_playlist():
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing playlist name'}), 400
    
    try:
        # Get user ID
        user_id = requests.get(
            "https://api.spotify.com/v1/me",
            headers=headers
        ).json()['id']
        
        # Create playlist
        r = requests.post(
            f"https://api.spotify.com/v1/users/{user_id}/playlists",
            headers=headers,
            json={
                'name': data['name'],
                'public': data.get('public', True)
            }
        )
        r.raise_for_status()
        playlist = r.json()
        
        # Add tracks if provided
        if data.get('tracks'):
            playlist_id = playlist['id']
            uris = [f"spotify:track:{track_id}" for track_id in data['tracks']]
            
            r = requests.post(
                f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                headers=headers,
                json={'uris': uris}
            )
            r.raise_for_status()
        
        return jsonify(playlist)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to create playlist'}), 500

@playlist_bp.route('/api/playlists/<playlist_id>')
def get_playlist(playlist_id):
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        r = requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}",
            headers=headers
        )
        r.raise_for_status()
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to get playlist'}), 500

@playlist_bp.route('/api/playlists/<playlist_id>/tracks', methods=['PUT'])
def add_tracks_to_playlist(playlist_id):
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    if not data or not data.get('tracks'):
        return jsonify({'error': 'Missing tracks'}), 400
    
    try:
        uris = [f"spotify:track:{track_id}" for track_id in data['tracks']]
        
        r = requests.post(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            headers=headers,
            json={'uris': uris}
        )
        r.raise_for_status()
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to add tracks'}), 500