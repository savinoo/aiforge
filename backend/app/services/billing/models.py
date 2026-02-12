"""
Pydantic models for billing operations.
"""

from datetime import datetime
from typing import Dict, List, Literal, Optional, Any
from pydantic import BaseModel, Field


# Request/Response Models
class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    tier: Literal["starter", "pro", "enterprise"] = Field(
        ...,
        description="Pricing tier to purchase"
    )
    custom_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional custom data to attach to the checkout"
    )


class CheckoutResponse(BaseModel):
    """Response containing checkout URL."""
    checkout_url: str = Field(..., description="URL to redirect user to for checkout")
    tier: str = Field(..., description="Tier being purchased")


class PricingTierResponse(BaseModel):
    """Pricing tier information."""
    id: str = Field(..., description="Tier identifier")
    name: str = Field(..., description="Display name")
    price: int = Field(..., description="Price in USD")
    currency: str = Field(..., description="Currency code")
    features: List[str] = Field(..., description="List of features included")


class PricingResponse(BaseModel):
    """Response containing all pricing tiers."""
    tiers: List[PricingTierResponse]


# Webhook Models
class WebhookEvent(BaseModel):
    """LemonSqueezy webhook event."""
    meta: Dict[str, Any] = Field(..., description="Metadata about the event")
    data: Dict[str, Any] = Field(..., description="Event data")


class WebhookResponse(BaseModel):
    """Response from webhook processing."""
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")


# Subscription Models
class SubscriptionStatus(BaseModel):
    """User subscription status."""
    active: bool = Field(..., description="Whether user has an active subscription")
    tier: Optional[str] = Field(None, description="Current tier if active")
    subscription_id: Optional[str] = Field(None, description="LemonSqueezy subscription ID")
    status: Optional[str] = Field(None, description="Subscription status")
    current_period_start: Optional[datetime] = Field(None, description="Current billing period start")
    current_period_end: Optional[datetime] = Field(None, description="Current billing period end")
    cancel_at: Optional[datetime] = Field(None, description="Cancellation date if scheduled")


# Purchase Models
class Purchase(BaseModel):
    """Purchase record."""
    id: str
    user_id: str
    tier: str
    order_id: Optional[str]
    license_key: Optional[str]
    amount_cents: int
    currency: str
    status: str
    purchased_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]


# License Validation Models
class LicenseValidationRequest(BaseModel):
    """Request to validate a license key."""
    license_key: str = Field(..., description="License key to validate")


class LicenseValidationResponse(BaseModel):
    """Response from license validation."""
    valid: bool = Field(..., description="Whether the license is valid")
    tier: Optional[str] = Field(None, description="Tier associated with the license")
    purchased_at: Optional[datetime] = Field(None, description="Purchase date")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    status: Optional[str] = Field(None, description="License status")
