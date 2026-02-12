"""
Health check endpoints.
Used for monitoring and readiness probes.
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, status

from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Health Check",
    description="Check if the API is running and healthy",
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Service status and metadata
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Readiness Check",
    description="Check if the API is ready to handle requests",
)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe for Kubernetes/Docker deployments.
    Can be extended to check database connections, external services, etc.

    Returns:
        Readiness status
    """
    # TODO: Add actual dependency checks (database, external APIs, etc.)
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Liveness Check",
    description="Check if the API process is alive",
)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness probe for Kubernetes/Docker deployments.

    Returns:
        Liveness status
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
    }
