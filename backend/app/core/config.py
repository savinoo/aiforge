"""
Application configuration using Pydantic Settings.
All environment variables are validated and typed here.
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="AIForge", description="Application name")
    environment: str = Field(default="development", description="Environment (development, production)")
    debug: bool = Field(default=False, description="Debug mode")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    secret_key: str = Field(..., description="Secret key for JWT encoding")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed origins"
    )

    @field_validator("allowed_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Supabase
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_anon_key: str = Field(..., description="Supabase anonymous key")
    supabase_service_role_key: str = Field(..., description="Supabase service role key")
    supabase_jwt_secret: str = Field(..., description="Supabase JWT secret")

    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Anthropic (optional)
    anthropic_api_key: str = Field(default="", description="Anthropic API key")

    # LemonSqueezy (optional until billing is set up)
    lemonsqueezy_api_key: str = Field(default="", description="LemonSqueezy API key")
    lemonsqueezy_store_id: str = Field(default="", description="LemonSqueezy store ID")
    lemonsqueezy_webhook_secret: str = Field(default="", description="LemonSqueezy webhook secret")

    # WhatsApp (optional until WhatsApp integration is set up)
    whatsapp_phone_number_id: str = Field(default="", description="WhatsApp phone number ID")
    whatsapp_access_token: str = Field(default="", description="WhatsApp access token")
    whatsapp_verify_token: str = Field(default="", description="WhatsApp verify token")
    whatsapp_business_account_id: str = Field(default="", description="WhatsApp business account ID")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
