"""
Authentication endpoints.
Proxies to Supabase Auth for user management.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.core.deps import DatabaseDep, CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response models
class SignUpRequest(BaseModel):
    """User signup request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: str | None = Field(None, description="User's full name")


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
    summary="Sign Up",
    description="Register a new user account",
)
async def signup(
    request: SignUpRequest,
    db: DatabaseDep,
) -> Dict[str, Any]:
    """
    Create a new user account.

    Args:
        request: Signup request data
        db: Supabase client

    Returns:
        Authentication tokens and user data

    Raises:
        HTTPException: If signup fails
    """
    try:
        # Create user with Supabase Auth
        response = db.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name,
                }
            } if request.full_name else {}
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account",
            )

        return {
            "access_token": response.session.access_token if response.session else "",
            "refresh_token": response.session.refresh_token if response.session else "",
            "token_type": "bearer",
            "expires_in": response.session.expires_in if response.session else 3600,
            "user": response.user.model_dump(),
        }

    except Exception as e:
        # Handle specific Supabase errors
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {error_message}",
        )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
    summary="Login",
    description="Authenticate user and get access token",
)
async def login(
    request: LoginRequest,
    db: DatabaseDep,
) -> Dict[str, Any]:
    """
    Authenticate user with email and password.

    Args:
        request: Login credentials
        db: Supabase client

    Returns:
        Authentication tokens and user data

    Raises:
        HTTPException: If login fails
    """
    try:
        response = db.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "expires_in": response.session.expires_in,
            "user": response.user.model_dump(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from e


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
    summary="Refresh Token",
    description="Get a new access token using refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DatabaseDep,
) -> Dict[str, Any]:
    """
    Refresh access token.

    Args:
        request: Refresh token request
        db: Supabase client

    Returns:
        New authentication tokens

    Raises:
        HTTPException: If refresh fails
    """
    try:
        response = db.auth.refresh_session(request.refresh_token)

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "expires_in": response.session.expires_in,
            "user": response.user.model_dump() if response.user else {},
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from e


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Get Current User",
    description="Get currently authenticated user's information",
)
async def get_me(
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """
    Get current user information.

    Args:
        current_user: Authenticated user from dependency

    Returns:
        User data
    """
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout current user",
)
async def logout(
    db: DatabaseDep,
    current_user: CurrentUser,
) -> Dict[str, str]:
    """
    Logout current user (invalidate token).

    Args:
        db: Supabase client
        current_user: Authenticated user

    Returns:
        Success message
    """
    try:
        db.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        # Even if Supabase sign_out fails, we return success
        # as the client should discard the token anyway
        return {"message": "Successfully logged out"}
