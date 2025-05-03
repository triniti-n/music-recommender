import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the service account file
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), 'serviceAccount.json')

try:
    # Use a service account
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    app = firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK initialized successfully")

    # Get Firestore client
    db = firestore.client()

    # Example: Add a test document
    doc_ref = db.collection('test').document('test_doc')
    doc_ref.set({
        'message': 'Firestore connection test successful',
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    logger.info("Test document added to Firestore")

    # Example: Read the test document
    doc = doc_ref.get()
    if doc.exists:
        logger.info(f"Test document data: {doc.to_dict()}")
    else:
        logger.warning("Test document not found")

except Exception as e:
    logger.error(f"Error initializing Firestore: {e}")
    raise