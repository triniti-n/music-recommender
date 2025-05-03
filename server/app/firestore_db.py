import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the service account file
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), 'serviceAccount.json')

# Initialize Firebase Admin SDK
try:
    # Check if already initialized
    firebase_admin.get_app()
    logger.info("Firebase Admin SDK already initialized")
except ValueError:
    # Initialize with service account
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK: {e}")

# Get Firestore client
db = firestore.client()

def save_selections_to_firestore(selections):
    """
    Save user selections to Firestore
    
    Args:
        selections (list): List of selection objects
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a batch to perform multiple operations
        batch = db.batch()
        
        # Reference to the selections collection
        selections_ref = db.collection('userSelections')
        
        # Add each selection to the batch
        for selection in selections:
            # Create a new document with auto-generated ID
            doc_ref = selections_ref.document()
            
            # Add timestamp if not present
            if 'selectedAt' not in selection:
                selection['selectedAt'] = firestore.SERVER_TIMESTAMP
                
            # Add the selection to the batch
            batch.set(doc_ref, selection)
        
        # Commit the batch
        batch.commit()
        logger.info(f"Successfully saved {len(selections)} selections to Firestore")
        return True
    except Exception as e:
        logger.error(f"Error saving selections to Firestore: {e}")
        return False

def get_selections_from_firestore(limit=10):
    """
    Get user selections from Firestore
    
    Args:
        limit (int): Maximum number of selections to retrieve
    
    Returns:
        list: List of selection objects
    """
    try:
        # Query the selections collection, ordered by selectedAt in descending order
        query = db.collection('userSelections').order_by('selectedAt', direction=firestore.Query.DESCENDING).limit(limit)
        
        # Execute the query
        docs = query.stream()
        
        # Convert to list of dictionaries
        selections = []
        for doc in docs:
            selection_data = doc.to_dict()
            selection_data['id'] = doc.id  # Add the document ID
            selections.append(selection_data)
        
        logger.info(f"Retrieved {len(selections)} selections from Firestore")
        return selections
    except Exception as e:
        logger.error(f"Error getting selections from Firestore: {e}")
        return []

def clear_selections_from_firestore():
    """
    Clear all selections from Firestore
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get all documents in the selections collection
        docs = db.collection('userSelections').stream()
        
        # Create a batch to delete all documents
        batch = db.batch()
        
        # Add each document to the batch for deletion
        for doc in docs:
            batch.delete(doc.reference)
        
        # Commit the batch
        batch.commit()
        logger.info("Successfully cleared all selections from Firestore")
        return True
    except Exception as e:
        logger.error(f"Error clearing selections from Firestore: {e}")
        return False

def save_playlist_to_firestore(playlist_data):
    """
    Save a playlist to Firestore
    
    Args:
        playlist_data (dict): Playlist data including name and songs
    
    Returns:
        str: Document ID of the saved playlist, or None if failed
    """
    try:
        # Add timestamp if not present
        if 'createdAt' not in playlist_data:
            playlist_data['createdAt'] = firestore.SERVER_TIMESTAMP
        
        # Add the playlist to Firestore
        doc_ref = db.collection('playlists').document()
        doc_ref.set(playlist_data)
        
        logger.info(f"Successfully saved playlist '{playlist_data.get('name')}' to Firestore with ID: {doc_ref.id}")
        return doc_ref.id
    except Exception as e:
        logger.error(f"Error saving playlist to Firestore: {e}")
        return None
