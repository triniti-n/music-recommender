from flask import Blueprint, jsonify, request, session
import requests
import os
from datetime import datetime, timedelta, timezone
import base64
import json
import os
import logging
from .firestore_db import save_selections_to_firestore, get_selections_from_firestore, clear_selections_from_firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)

# Path to the selections file
SELECTIONS_FILE = os.path.join(os.path.dirname(__file__), 'selections', 'all_selections.json')

# Function to update selections JSON file

def update_selections(action, selections, search_query):
    try:
        with open(SELECTIONS_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    if action == 'add':
        # Only add selections if there are actual selections
        if not selections:
            logger.info("No selections to add, skipping")
            return True

        # If this is a new search (no existing selections), reset the file
        if len(data) == 0:
            logger.info("Starting new search with empty selections file")
            # File is already empty, no need to clear

        # Clean up selection data to keep only necessary fields
        cleaned_selections = []
        for item in selections:
            cleaned_item = {
                'imageUrl': item.get('avatar', ''),  # Using avatar as it's the correct field from Spotify
                'name': item.get('display', ''),  # Using display as it's the correct field from Spotify
                'artistNames': item.get('artistNames', 'Unknown Artist'),  # Add artist names
                'searchQuery': search_query,
                'spotifyId': item.get('id', ''),  # Using id as it's the correct field from Spotify
                'type': item.get('type', ''),
                'selectedAt': datetime.now(timezone.utc).isoformat()
            }
            cleaned_selections.append(cleaned_item)

        # Add new selections
        data.extend(cleaned_selections)

        # Keep only the 10 most recent selections
        if len(data) > 10:
            # Sort by selectedAt in descending order (newest first)
            data.sort(key=lambda x: x.get('selectedAt', ''), reverse=True)
            # Keep only the first 10 items
            data = data[:10]
            logger.info(f"Limiting selections to 10 most recent items. Current count: {len(data)}")

        # Save to Firestore
        firestore_result = save_selections_to_firestore(cleaned_selections)
        if firestore_result:
            logger.info("Successfully saved selections to Firestore")
        else:
            logger.warning("Failed to save selections to Firestore, but JSON file was updated")

    elif action == 'remove':
        # Remove selections by ID
        for item in selections:
            # Match by spotifyId (stored in JSON) with id (from frontend)
            item_id = item.get('id')
            item_uri = item.get('uri')

            # First, find the search query associated with this selection
            search_query = None
            for entry in data:
                if (item_id and entry.get('spotifyId') == item_id) or \
                   (item_uri and entry.get('uri') == item_uri):
                    search_query = entry.get('searchQuery')
                    break

            # If we found a search query, remove all selections with that query
            if search_query:
                logger.info(f"Removing all selections with search query: {search_query}")
                data = [x for x in data if x.get('searchQuery') != search_query]
            # Otherwise, just remove the specific selection
            elif item_id:
                # If we have an ID, filter by spotifyId
                data = [x for x in data if x.get('spotifyId') != item_id]
            elif item_uri:
                # If we have a URI, filter by uri
                data = [x for x in data if x.get('uri') != item_uri]

        # If all selections have been removed, reset the file
        if len(data) == 0:
            logger.info("All selections removed, resetting file")
            # Also clear Firestore
            clear_selections_from_firestore()

    elif action == 'clear':
        # Reset the file to an empty array
        data = []
        logger.info("Cleared all selections")
        # Also clear Firestore
        clear_selections_from_firestore()

    elif action == 'new_search':
        # Reset the file to an empty array when starting a new search
        data = []
        logger.info("Starting new search, cleared all previous selections")
        # Also clear Firestore
        clear_selections_from_firestore()

    # Write back to file
    with open(SELECTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    return True

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

def save_search(query, search_type):
    # This function is a placeholder for search history functionality
    # Currently, we're just storing the session ID in the session
    session_id = session.get('session_id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    # Log the search for debugging purposes
    print(f"Search saved: query='{query}', type='{search_type}', session_id='{session_id}'")

    # In the future, this could be expanded to store search history in a database
    return session_id

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
    type_ = request.args.get('type', 'track')
    if not query:
        return jsonify({'error': 'Missing search query'}), 400

    # Update the last search query in session, but don't clear selections
    last_query = session.get('last_search_query')
    if last_query != query:
        print(f"New search query detected: '{query}' (previous: '{last_query}')")
        # Store the new query in session
        session['last_search_query'] = query
        # No longer clearing selections for new search

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

    # Update the last search query in session, but don't clear selections
    last_query = session.get('last_search_query')
    if last_query != query:
        print(f"New search query detected: '{query}' (previous: '{last_query}')")
        # Store the new query in session
        session['last_search_query'] = query
        # No longer clearing selections for new search

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

    # Update the last search query in session, but don't clear selections
    last_query = session.get('last_search_query')
    if last_query != query:
        print(f"New search query detected: '{query}' (previous: '{last_query}')")
        # Store the new query in session
        session['last_search_query'] = query
        # No longer clearing selections for new search

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

@search_bp.route('/api/search/selections', methods=['POST'])
def update_selections_endpoint():
    try:
        data = request.get_json()
        action = data.get('action')
        selections = data.get('selections', [])
        search_query = data.get('searchQuery')

        if not action or action not in ['add', 'remove', 'clear']:
            return jsonify({'error': 'Invalid action'}), 400

        # For clear action, we don't need selections or search_query
        if action == 'clear':
            success = update_selections('clear', [], None)
            if success:
                return jsonify({'message': 'All selections cleared successfully'}), 200
            else:
                return jsonify({'error': 'Failed to clear selections'}), 500

        # For add and remove actions, we need selections
        if not selections and action != 'clear':
            # If no selections and action is 'add', clear the file
            if action == 'add':
                success = update_selections('clear', [], None)
                if success:
                    return jsonify({'message': 'No selections provided, cleared all selections'}), 200
                else:
                    return jsonify({'error': 'Failed to clear selections'}), 500
            else:
                return jsonify({'error': 'No selections provided'}), 400

        # For add action, we need search_query
        if action == 'add' and not search_query:
            return jsonify({'error': 'Search query is required for adding selections'}), 400

        success = update_selections(action, selections, search_query)
        if success:
            return jsonify({'message': f'Selections {action}ed successfully'}), 200
        else:
            return jsonify({'error': f'Failed to {action} selections'}), 500
    except Exception as e:
        print('Error in update_selections_endpoint:', str(e))
        return jsonify({'error': str(e)}), 500

@search_bp.route('/api/search/selections/<selection_id>', methods=['DELETE'])
def delete_selection(selection_id):
    selections_file = os.path.join(os.path.dirname(__file__), 'selections', 'all_selections.json')
    try:
        with open(selections_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    # Remove selection by spotifyId or uri
    new_data = [x for x in data if str(x.get('spotifyId')) != selection_id and str(x.get('uri', '')) != selection_id]

    # Write back to file
    with open(selections_file, 'w') as f:
        json.dump(new_data, f, indent=2)
    return jsonify({'message': 'Selection deleted successfully'}), 200

# Keep the old endpoint for backward compatibility
@search_bp.route('/api/selections', methods=['POST'])
def update_selections_endpoint_legacy():
    return update_selections_endpoint()

@search_bp.route('/api/search/selections/clear', methods=['POST'])
def clear_selections_endpoint():
    """Clear all selections"""
    try:
        success = clear_selections()
        if success:
            return jsonify({'message': 'All selections cleared successfully'}), 200
        else:
            return jsonify({'error': 'Failed to clear selections'}), 500
    except Exception as e:
        print('Error in clear_selections_endpoint:', str(e))
        return jsonify({'error': str(e)}), 500

@search_bp.route('/api/search/selections', methods=['GET'])
def get_selections():
    """Get all current selections from both JSON file and Firestore"""
    try:
        # Get selections from JSON file
        try:
            with open(SELECTIONS_FILE, 'r') as f:
                json_selections = json.load(f)
            logger.info(f"Retrieved {len(json_selections)} selections from JSON file")
        except FileNotFoundError:
            json_selections = []
            logger.warning("Selections JSON file not found, using empty list")
        except json.JSONDecodeError:
            json_selections = []
            logger.warning("Invalid JSON in selections file, using empty list")

        # Get selections from Firestore
        firestore_selections = get_selections_from_firestore(limit=10)
        logger.info(f"Retrieved {len(firestore_selections)} selections from Firestore")

        # Use Firestore selections if available, otherwise fall back to JSON
        if firestore_selections:
            selections = firestore_selections
            logger.info("Using selections from Firestore")
        else:
            selections = json_selections
            logger.info("Using selections from JSON file")

        # Sort selections by selectedAt in descending order (newest first)
        selections.sort(key=lambda x: x.get('selectedAt', ''), reverse=True)

        # Limit to 10 most recent selections
        selections = selections[:10]

        # Format selections for the music player
        formatted_selections = []
        for selection in selections:
            formatted_selection = {
                'id': selection.get('spotifyId'),
                'title': selection.get('name'),
                'artist': selection.get('artistNames', 'Unknown Artist'),
                'cover': selection.get('imageUrl'),
                'duration': '3:30',  # Default duration as it's not stored in selections
                'url': f"https://open.spotify.com/track/{selection.get('spotifyId')}"
            }
            formatted_selections.append(formatted_selection)

        return jsonify({
            'songs': formatted_selections,
            'name': 'My Selected Songs',
            'count': len(formatted_selections),
            'source': 'firestore' if firestore_selections else 'json'
        }), 200
    except Exception as e:
        logger.error(f'Error getting selections: {str(e)}')
        return jsonify({'error': str(e)}), 500

@search_bp.route('/api/search/new', methods=['POST'])
def new_search():
    """Start a new search, optionally keeping previous selections"""
    try:
        # Get the search query from the request
        data = request.get_json()
        query = data.get('query', '')
        keep_selections = data.get('keepSelections', False)

        if keep_selections:
            # Keep selections, just log the new search
            print(f"Starting new search with query: {query} (keeping selections)")
            return jsonify({'message': 'New search started, keeping previous selections'}), 200
        else:
            # Clear all previous selections
            success = update_selections('new_search', [], None)
            if success:
                # Log the new search
                print(f"Starting new search with query: {query} (cleared selections)")
                return jsonify({'message': 'New search started, all previous selections cleared'}), 200
            else:
                return jsonify({'error': 'Failed to start new search'}), 500
    except Exception as e:
        print('Error starting new search:', str(e))
        return jsonify({'error': str(e)}), 500

@search_bp.route('/api/search', methods=['GET'])
def public_search():
    query = request.args.get('q')
    type_ = request.args.get('type', 'track')
    if not query:
        return jsonify({'error': 'Missing search query'}), 400

    # Update the last search query in session, but don't clear selections
    last_query = session.get('last_search_query')
    if last_query != query:
        print(f"New search query detected: '{query}' (previous: '{last_query}')")
        # Store the new query in session
        session['last_search_query'] = query
        # No longer clearing selections for new search

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
