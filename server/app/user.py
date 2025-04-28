from flask import Blueprint, jsonify, session
import requests
import os

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user', methods=['GET'])
def get_username():
    headers = get_headers()
    if not headers:
        return jsonify({'error': 'Not authenticated'}), 401
    
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return jsonify(r.json())