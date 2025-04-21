from flask import Blueprint, jsonify, request, session
import requests
import os
from .models import db, SearchHistory

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

# Helper to get the access token from session
def get_headers():
    access_token = session.get('access_token')
    if not access_token:
        print('Error: Access token not found in session')
        return None
    return {"Authorization": f"Bearer {access_token}"}

def no_header():
    print('Error: Not authenticated')
    return jsonify({'error': 'Not authenticated'}), 401

@search_bp.route('/api/spotify/search', methods=['GET'])
def search():
    headers = get_headers()
    if not headers:
        return no_header()
    query = request.args.get('q')
    type_ = request.args.get('type', 'track,artist')
    if not query:
        return jsonify({'error': 'Missing search query'}), 400
    # Save the search query and type
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
        return no_header()
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
        return no_header()
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
