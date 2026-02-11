"""Firebase Admin SDK initialization

Supports two authentication methods:
1. ADC (Application Default Credentials) - recommended for GCP environments
   - Cloud Run: automatic via attached service account
   - Local: `gcloud auth application-default login`
2. Explicit service account credentials via environment variables (fallback)
"""

import logging

import firebase_admin
from firebase_admin import auth, credentials

logger = logging.getLogger(__name__)

_app: firebase_admin.App | None = None


def initialize_firebase_admin(
    project_id: str | None = None,
    client_email: str | None = None,
    private_key: str | None = None,
) -> firebase_admin.App:
    """Initialize Firebase Admin SDK.

    Uses explicit credentials if all three parameters are provided,
    otherwise falls back to Application Default Credentials (ADC).

    Args:
        project_id: Firebase project ID (used for both explicit and ADC modes)
        client_email: Service account client email (explicit mode only)
        private_key: Service account private key in PEM format (explicit mode only)

    Returns:
        Firebase app instance
    """
    global _app

    if _app is not None:
        logger.debug("Firebase Admin already initialized")
        return _app

    try:
        if all([client_email, private_key]):
            _app = _initialize_with_credentials(project_id, client_email, private_key)  # type: ignore[arg-type]
        else:
            _app = _initialize_with_adc(project_id)
        return _app
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin: {e}")
        raise


def _initialize_with_credentials(
    project_id: str | None,
    client_email: str,
    private_key: str,
) -> firebase_admin.App:
    """Initialize with explicit service account credentials."""
    normalized_private_key = private_key.replace("\\n", "\n")

    service_account_dict = {
        "type": "service_account",
        "project_id": project_id or "",
        "client_email": client_email,
        "private_key": normalized_private_key,
        "private_key_id": "",
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    cred = credentials.Certificate(service_account_dict)
    app = firebase_admin.initialize_app(cred)
    logger.info(f"Firebase Admin initialized with explicit credentials (project: {project_id})")
    return app


def _initialize_with_adc(project_id: str | None = None) -> firebase_admin.App:
    """Initialize with Application Default Credentials (ADC)."""
    options: dict[str, str] = {}
    if project_id:
        options["projectId"] = project_id

    app = firebase_admin.initialize_app(options=options if options else None)
    logger.info(f"Firebase Admin initialized with ADC (project: {project_id})")
    return app


def get_firebase_app() -> firebase_admin.App:
    """Get Firebase app instance. Ensure initialize_firebase_admin is called first."""
    if _app is None:
        raise RuntimeError(
            "Firebase Admin not initialized. Call initialize_firebase_admin() first."
        )
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
        raise ValueError(f"Invalid or expired token: {e}") from e
