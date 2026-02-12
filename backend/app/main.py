"""
AIForge FastAPI Application.
Main entry point for the backend API.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API documentation available at: /docs")

    # TODO: Initialize resources here (database connections, caches, etc.)
    # Example:
    # await init_database()
    # await init_redis()

    yield

    # Shutdown
    logger.info("Shutting down application")
    # TODO: Cleanup resources here
    # Example:
    # await close_database()
    # await close_redis()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered SaaS boilerplate with RAG, Agents, and WhatsApp integration",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    Logs the error and returns a generic error response.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    if settings.is_production:
        # Don't expose internal errors in production
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    else:
        # Show detailed error in development
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": f"{settings.api_v1_prefix}/docs" if settings.debug else "disabled",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
