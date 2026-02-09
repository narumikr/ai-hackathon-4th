"""Firebase Admin SDK initialization"""

import json
import logging
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials

logger = logging.getLogger(__name__)

_app: Optional[firebase_admin.App] = None


def initialize_firebase_admin(
    project_id: str,
    client_email: str,
    private_key: str,
) -> firebase_admin.App:
    """Initialize Firebase Admin SDK with service account credentials.
    
    Args:
        project_id: Firebase project ID
        client_email: Service account client email
        private_key: Service account private key (PEM format)
        
    Returns:
        Firebase app instance
    """
    global _app
    
    if _app is not None:
        logger.debug("Firebase Admin already initialized")
        return _app
    
    try:
        # Build service account dict
        service_account_dict = {
            "type": "service_account",
            "project_id": project_id,
            "client_email": client_email,
            "private_key": private_key,
            "private_key_id": "",
            "client_id": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        # Create credential
        cred = credentials.Certificate(service_account_dict)
        
        # Initialize app
        _app = firebase_admin.initialize_app(cred)
        logger.info(f"Firebase Admin initialized for project: {project_id}")
        return _app
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin: {e}")
        raise


def get_firebase_app() -> firebase_admin.App:
    """Get Firebase app instance. Ensure initialize_firebase_admin is called first."""
    if _app is None:
        raise RuntimeError("Firebase Admin not initialized. Call initialize_firebase_admin() first.")
    return _app


def verify_id_token(token: str) -> dict:
    """Verify Firebase ID token.
    
    Args:
        token: ID token to verify
        
    Returns:
        Decoded token claims
        
    Raises:
        ValueError: If token is invalid or expired
    """
    if _app is None:
        raise RuntimeError("Firebase Admin not initialized")
    try:
        return auth.verify_id_token(token)
    except Exception as e:
        logger.debug(f"Token verification failed: {e}")
        raise ValueError(f"Invalid or expired token: {e}")
