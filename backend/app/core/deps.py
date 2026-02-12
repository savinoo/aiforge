"""
FastAPI dependency injection.
Provides common dependencies like database access and authentication.
"""

from typing import Annotated, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from supabase import Client

from app.core.config import settings
from app.db.supabase import get_supabase

# Security scheme for JWT bearer tokens
security = HTTPBearer()


async def get_db() -> Client:
    """
    Get Supabase client dependency.

    Returns:
        Supabase client instance
    """
    return get_supabase()


async def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode Supabase JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Client, Depends(get_db)],
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP bearer credentials
        db: Supabase client

    Returns:
        User data from Supabase

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    # Verify JWT token
    payload = await verify_jwt_token(token)

    # Extract user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user data from Supabase
    try:
        response = db.auth.get_user(token)
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return response.user.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate user",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: Annotated[Client, Depends(get_db)] = None,
) -> Dict[str, Any] | None:
    """
    Get current user if authenticated, None otherwise.
    Useful for endpoints that work both authenticated and unauthenticated.

    Args:
        credentials: Optional HTTP bearer credentials
        db: Supabase client

    Returns:
        User data if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# Type aliases for cleaner endpoint signatures
CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user)]
OptionalUser = Annotated[Dict[str, Any] | None, Depends(get_optional_user)]
DatabaseDep = Annotated[Client, Depends(get_db)]
