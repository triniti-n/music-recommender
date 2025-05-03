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
# Check if file exists
if not os.path.exists(SERVICE_ACCOUNT_PATH):
    # Try alternative path
    alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'serviceAccount.json')
    if os.path.exists(alt_path):
        SERVICE_ACCOUNT_PATH = alt_path
        logger.info(f"Using alternative service account path: {SERVICE_ACCOUNT_PATH}")
    else:
        logger.error(f"Service account file not found at {SERVICE_ACCOUNT_PATH} or {alt_path}")
else:
    logger.info(f"Using service account path: {SERVICE_ACCOUNT_PATH}")

# Initialize Firebase Admin SDK
try:
    # Check if already initialized
    app = firebase_admin.get_app()
    logger.info("Firebase Admin SDK already initialized")
except ValueError:
    # Initialize with service account
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK: {e}")
        # Create a dummy app for development/testing
        logger.warning("Creating a dummy Firebase app for development/testing")
        app = firebase_admin.initialize_app()

# Get Firestore client
try:
    db = firestore.client()
    logger.info("Firestore client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Firestore client: {e}")
    # Create a dummy db object for development/testing
    class DummyDB:
        def collection(self, name):
            return DummyCollection(name)

        def batch(self):
            return DummyBatch()

    class DummyCollection:
        def __init__(self, name):
            self.name = name

        def document(self, doc_id=None):
            return DummyDocument(doc_id)

        def order_by(self, field, direction=None):
            return self

        def limit(self, count):
            return self

        def stream(self):
            return []

    class DummyDocument:
        def __init__(self, doc_id=None):
            self.id = doc_id or "dummy_id"
            self.reference = self

        def set(self, data):
            logger.info(f"DummyDocument.set called with data: {data}")
            return True

        def get(self):
            return self

        def to_dict(self):
            return {"dummy": True}

        @property
        def exists(self):
            return True

    class DummyBatch:
        def set(self, doc_ref, data):
            logger.info(f"DummyBatch.set called with data: {data}")
            return self

        def delete(self, doc_ref):
            logger.info(f"DummyBatch.delete called")
            return self

        def commit(self):
            logger.info("DummyBatch.commit called")
            return []

    db = DummyDB()

    # Create a dummy SERVER_TIMESTAMP for development/testing
    if not hasattr(firestore, 'SERVER_TIMESTAMP'):
        firestore.SERVER_TIMESTAMP = datetime.now()

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
