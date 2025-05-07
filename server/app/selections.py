from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime

selections_bp = Blueprint('selections', __name__)

# Path to the selections file
SELECTIONS_FILE = os.path.join(os.path.dirname(__file__), 'selections', 'all_selections.json')

# Helper function to load selections
def load_selections():
    try:
        with open(SELECTIONS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Helper function to save selections
def save_selections(selections):
    with open(SELECTIONS_FILE, 'w') as f:
        json.dump(selections, f, indent=2)

@selections_bp.route('/api/selections', methods=['GET'])
def get_selections():
    """Get all selections"""
    selections = load_selections()
    return jsonify(selections)

@selections_bp.route('/api/selections', methods=['POST'])
def add_selection():
    """Add a new selection"""
    data = request.get_json()
    
    if not data or not all(key in data for key in ['name', 'artistNames', 'spotifyId', 'type', 'imageUrl', 'searchQuery']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Add timestamp
    data['selectedAt'] = datetime.utcnow().isoformat()
    
    # Load existing selections
    selections = load_selections()
    
    # Add new selection
    selections.insert(0, data)  # Add to beginning to keep most recent first
    
    # Save updated selections
    save_selections(selections)
    
    return jsonify({'message': 'Selection added successfully', 'selection': data})

@selections_bp.route('/api/selections/<spotify_id>', methods=['DELETE'])
def delete_selection(spotify_id):
    """Delete a selection by spotify ID"""
    # Load existing selections
    selections = load_selections()
    
    # Find and remove the selection
    selections = [s for s in selections if s['spotifyId'] != spotify_id]
    
    # Save updated selections
    save_selections(selections)
    
    return jsonify({'message': 'Selection removed successfully'})

@selections_bp.route('/api/selections/latest', methods=['GET'])
def get_latest_selections():
    """Get the latest 10 selections for playlist creation"""
    selections = load_selections()
    latest_selections = selections[:10]  # Get first 10 items (most recent)
    return jsonify(latest_selections)
