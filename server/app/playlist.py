from flask import Blueprint, jsonify, request, session
import requests
import os
import json
import base64
import logging
from .firestore_db import clear_selections_from_firestore, save_playlist_to_firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

playlist_bp = Blueprint('playlist', __name__)

# Path to the selections file
SELECTIONS_FILE = os.path.join(os.path.dirname(__file__), 'selections', 'all_selections.json')

# Function to clear all selections
def clear_selections():
    """Reset the selections file to an empty array and clear Firestore selections"""
    try:
        # Clear JSON file
        with open(SELECTIONS_FILE, 'w') as f:
            json.dump([], f, indent=2)

        # Clear Firestore
        firestore_result = clear_selections_from_firestore()
        if firestore_result:
            logger.info("Successfully cleared selections from Firestore")
        else:
            logger.warning("Failed to clear selections from Firestore, but JSON file was cleared")

        return True
    except Exception as e:
        logger.error(f"Error clearing selections: {e}")
        return False

@playlist_bp.route('/api/playlists/create', methods=['POST'])
def create_playlist():
    """Create a playlist from selected tracks and clear selections"""
    try:
        data = request.get_json()
        name = data.get('name', 'My Playlist')
        is_public = data.get('public', True)
        track_ids = data.get('tracks', [])
        artist_ids = data.get('artists', [])

        # Get Spotify access token from session
        access_token = session.get('access_token')
        if not access_token:
            # Use client credentials flow as fallback
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

            auth_response = requests.post(auth_url, data=auth_data, headers=auth_header)
            auth_response.raise_for_status()
            access_token = auth_response.json()['access_token']

        # Get user ID
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        user_response.raise_for_status()
        user_id = user_response.json()['id']

        # Create empty playlist
        playlist_data = {
            'name': name,
            'public': is_public,
            'description': 'Created with Music Recommender App'
        }

        playlist_response = requests.post(
            f'https://api.spotify.com/v1/users/{user_id}/playlists',
            headers={**headers, 'Content-Type': 'application/json'},
            json=playlist_data
        )
        playlist_response.raise_for_status()
        playlist = playlist_response.json()
        playlist_id = playlist['id']

        # Add tracks to playlist
        if track_ids:
            track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]

            # Add tracks in batches of 100 (Spotify API limit)
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i:i+100]
                add_tracks_response = requests.post(
                    f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                    headers={**headers, 'Content-Type': 'application/json'},
                    json={'uris': batch}
                )
                add_tracks_response.raise_for_status()

        # Get the current selections to save with the playlist
        try:
            with open(SELECTIONS_FILE, 'r') as f:
                selections = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            selections = []

        # Format the playlist data for Firestore
        playlist_data = {
            'name': name,
            'spotifyId': playlist_id,
            'spotifyUrl': playlist.get('external_urls', {}).get('spotify', ''),
            'isPublic': is_public,
            'createdAt': None,  # Will be set to server timestamp in Firestore
            'userId': user_id,
            'songs': []
        }

        # Add songs from selections
        for selection in selections:
            song_data = {
                'spotifyId': selection.get('spotifyId', ''),
                'name': selection.get('name', ''),
                'artistNames': selection.get('artistNames', 'Unknown Artist'),
                'imageUrl': selection.get('imageUrl', ''),
                'searchQuery': selection.get('searchQuery', ''),
                'type': selection.get('type', 'track')
            }
            playlist_data['songs'].append(song_data)

        # Save playlist to Firestore
        firestore_id = save_playlist_to_firestore(playlist_data)
        if firestore_id:
            logger.info(f"Playlist saved to Firestore with ID: {firestore_id}")
            # Add Firestore ID to response
            playlist['firestoreId'] = firestore_id
        else:
            logger.warning("Failed to save playlist to Firestore")

        # Clear selections after successful playlist creation
        clear_selections()

        return jsonify(playlist)

    except requests.exceptions.RequestException as e:
        error_details = {
            'error': str(e),
            'status_code': getattr(e.response, 'status_code', None),
            'response_text': getattr(e.response, 'text', None)
        }
        logger.error(f"Error creating playlist: {error_details}")
        return jsonify({'error': 'Failed to create playlist', 'details': error_details}), 500

    except Exception as e:
        logger.error(f"Error creating playlist: {e}")
        return jsonify({'error': str(e)}), 500