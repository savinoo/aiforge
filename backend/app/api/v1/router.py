"""
Main API v1 router.
Includes all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import health, auth

# Create main v1 router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router)
api_router.include_router(auth.router)

# TODO: Add more routers as you build out the API
# from app.api.v1 import rag, agents, whatsapp, payments
# api_router.include_router(rag.router)
# api_router.include_router(agents.router)
# api_router.include_router(whatsapp.router)
# api_router.include_router(payments.router)
