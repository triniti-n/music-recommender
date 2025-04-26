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
        playlist_id = playlist['id']
        
        # Process tracks and artists
        track_uris = []
        
        # Add direct track selections
        if data.get('tracks'):
            track_uris.extend([f"spotify:track:{track_id}" for track_id in data['tracks']])
        
        # Add tracks from selected artists
        if data.get('artists'):
            for artist_id in data['artists']:
                # Get artist's top tracks
                top_tracks_response = requests.get(
                    f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US",
                    headers=headers
                )
                top_tracks_response.raise_for_status()
                top_tracks = top_tracks_response.json().get('tracks', [])
                
                # Add up to 5 top tracks from each artist
                for track in top_tracks[:5]:
                    track_uris.append(track['uri'])
        
        # Add all tracks to the playlist
        if track_uris:
            # Spotify API has a limit of 100 tracks per request, so we need to batch
            batch_size = 100
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i+batch_size]
                r = requests.post(
                    f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                    headers=headers,
                    json={'uris': batch}
                )
                r.raise_for_status()
        
        return jsonify(playlist)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to create playlist', 'details': str(e)}), 500

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