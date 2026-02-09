"""Authentication middleware and dependencies"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from app.infrastructure.firebase_admin import verify_id_token

logger = logging.getLogger(__name__)


class UserContext:
    """User context extracted from Firebase ID token"""
    
    def __init__(self, uid: str, email: Optional[str] = None, name: Optional[str] = None, provider: Optional[str] = None):
        self.uid = uid
        self.email = email
        self.name = name
        self.provider = provider


def extract_token_from_header(request: Request) -> Optional[str]:
    """Extract Bearer token from Authorization header.
    
    Returns:
        Token string or None if not present
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


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
    except ValueError as e:
        logger.debug(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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


def optional_auth(request: Request) -> Optional[UserContext]:
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
    except ValueError as e:
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
