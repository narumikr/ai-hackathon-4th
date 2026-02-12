"""Authentication middleware and dependencies"""

import logging

from fastapi import HTTPException, Request, status

from app.infrastructure.firebase_admin import verify_id_token

logger = logging.getLogger(__name__)


class UserContext:
    """User context extracted from Firebase ID token"""

    def __init__(
        self,
        uid: str,
        email: str | None = None,
        name: str | None = None,
        provider: str | None = None,
    ):
        self.uid = uid
        self.email = email
        self.name = name
        self.provider = provider


def extract_token_from_header(request: Request) -> str | None:
    """Extract Bearer token from request headers.

    In production, the frontend proxy overwrites the Authorization header
    with a GCP OIDC token for Cloud Run service-to-service authentication,
    and forwards the original Firebase ID token via X-Forwarded-Authorization.

    Priority:
        1. X-Forwarded-Authorization (forwarded from frontend proxy)
        2. Authorization (direct access / local development)

    Returns:
        Token string or None if not present
    """
    forwarded_auth = request.headers.get("X-Forwarded-Authorization")
    standard_auth = request.headers.get("Authorization")

    logger.warning(
        "Auth header debug: X-Forwarded-Authorization=%s, Authorization=%s",
        "present" if forwarded_auth else "absent",
        "present" if standard_auth else "absent",
    )

    auth_header = forwarded_auth or standard_auth
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]
    source = "X-Forwarded-Authorization" if forwarded_auth else "Authorization"
    logger.warning("Token extracted from %s (first 20 chars: %s...)", source, token[:20])

    return token


def require_auth(request: Request) -> UserContext:
    """Dependency to extract and validate Firebase ID token.

    Args:
        request: FastAPI request

    Returns:
        UserContext with verified uid and optional email/name

    Raises:
        HTTPException: 401 if token missing/invalid, 403 if not allowed
    """
    token = extract_token_from_header(request)
    if not token:
        logger.debug("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = verify_id_token(token)
    except RuntimeError as e:
        logger.error(f"Firebase Admin not initialized: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable",
        ) from e
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Extract user info from claims
    uid = claims.get("uid")
    email = claims.get("email")
    name = claims.get("name")
    provider = claims.get("firebase", {}).get("sign_in_provider")

    if not uid:
        logger.error("Token claims missing uid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )

    user_context = UserContext(uid=uid, email=email, name=name, provider=provider)
    request.state.user = user_context

    logger.debug(f"User authenticated: uid={uid}")
    return user_context


def optional_auth(request: Request) -> UserContext | None:
    """Optional authentication dependency. Returns None if token not present.

    Args:
        request: FastAPI request

    Returns:
        UserContext if token present and valid, None otherwise
    """
    token = extract_token_from_header(request)
    if not token:
        return None

    try:
        claims = verify_id_token(token)
    except (RuntimeError, ValueError) as e:
        logger.debug(f"Token verification failed in optional auth: {e}")
        return None

    uid = claims.get("uid")
    if not uid:
        return None

    email = claims.get("email")
    name = claims.get("name")
    provider = claims.get("firebase", {}).get("sign_in_provider")

    user_context = UserContext(uid=uid, email=email, name=name, provider=provider)
    request.state.user = user_context

    logger.debug(f"Optional user authenticated: uid={uid}")
    return user_context
