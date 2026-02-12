"""
Supabase client initialization.
Provides both regular and service role clients.
"""

from typing import Optional
from supabase import Client, create_client
from app.core.config import settings


class SupabaseClient:
    """Singleton Supabase client manager."""

    _client: Optional[Client] = None
    _service_client: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Get the standard Supabase client (with anon key).
        Used for regular authenticated operations.
        """
        if cls._client is None:
            cls._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_anon_key,
            )
        return cls._client

    @classmethod
    def get_service_client(cls) -> Client:
        """
        Get the Supabase service role client.
        Used for admin operations that bypass RLS.
        """
        if cls._service_client is None:
            cls._service_client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_role_key,
            )
        return cls._service_client

    @classmethod
    def reset_clients(cls) -> None:
        """Reset clients (useful for testing)."""
        cls._client = None
        cls._service_client = None


# Convenience functions
def get_supabase() -> Client:
    """Get the standard Supabase client."""
    return SupabaseClient.get_client()


def get_supabase_service() -> Client:
    """Get the Supabase service role client."""
    return SupabaseClient.get_service_client()
