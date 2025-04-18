# api/spotify.py
from flask import Blueprint, session, jsonify, request
import requests

spotify_bp = Blueprint('spotify', __name__)

@spotify_bp.route('/api/spotify/me')
def get_profile():
    access_token = session.get('access_token')
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return jsonify(r.json())