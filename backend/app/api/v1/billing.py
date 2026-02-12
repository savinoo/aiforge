"""
Billing API endpoints.
Handles checkout, webhooks, subscriptions, and license validation.
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from supabase import Client

from app.core.deps import CurrentUser, DatabaseDep
from app.services.billing import PRICING_TIERS, LemonSqueezyClient, handle_webhook_event
from app.services.billing.config import get_tier_config
from app.services.billing.models import (
    CheckoutRequest,
    CheckoutResponse,
    PricingResponse,
    PricingTierResponse,
    SubscriptionStatus,
    WebhookEvent,
    WebhookResponse,
    LicenseValidationRequest,
    LicenseValidationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/pricing", response_model=PricingResponse)
async def get_pricing():
    """
    Get all pricing tiers.
    Public endpoint - no authentication required.

    Returns:
        All available pricing tiers
    """
    tiers = [
        PricingTierResponse(
            id=tier_id,
            name=tier["name"],
            price=tier["price"],
            currency=tier["currency"],
            features=tier["features"],
        )
        for tier_id, tier in PRICING_TIERS.items()
    ]
    return PricingResponse(tiers=tiers)


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    current_user: CurrentUser,
    db: DatabaseDep,
):
    """
    Create a checkout session for purchasing a tier.
    Requires authentication.

    Args:
        request: Checkout request with tier selection
        current_user: Authenticated user
        db: Database client

    Returns:
        Checkout URL to redirect user to

    Raises:
        HTTPException: If LemonSqueezy is not configured or checkout creation fails
    """
    client = LemonSqueezyClient()

    if not client.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing is not configured. Please contact support.",
        )

    # Get tier configuration
    try:
        tier_config = get_tier_config(request.tier)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    # Get user details
    user_id = current_user.get("id")
    user_email = current_user.get("email")

    if not user_id or not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID or email not found",
        )

    # For demo purposes, we'll use placeholder product/variant IDs
    # In production, you would map tiers to actual LemonSqueezy product/variant IDs
    # TODO: Replace with actual LemonSqueezy product/variant IDs
    product_id = "YOUR_PRODUCT_ID"
    variant_id = f"YOUR_VARIANT_ID_{request.tier.upper()}"

    try:
        # Create custom data to pass through to webhooks
        custom_data = {
            "tier": request.tier,
            **(request.custom_data or {}),
        }

        # Create checkout session
        checkout_data = await client.create_checkout(
            product_id=product_id,
            variant_id=variant_id,
            user_email=user_email,
            user_id=user_id,
            custom_data=custom_data,
        )

        # Extract checkout URL from response
        checkout_url = checkout_data.get("data", {}).get("attributes", {}).get("url")

        if not checkout_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create checkout session",
            )

        logger.info(f"Created checkout for user {user_id}, tier {request.tier}")

        return CheckoutResponse(
            checkout_url=checkout_url,
            tier=request.tier,
        )

    except Exception as e:
        logger.error(f"Error creating checkout: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout: {str(e)}",
        ) from e


@router.post("/webhook", response_model=WebhookResponse)
async def handle_webhook(
    request: Request,
    db: DatabaseDep,
    x_signature: Annotated[str | None, Header()] = None,
):
    """
    Handle LemonSqueezy webhook events.
    No authentication required - uses signature verification.

    Args:
        request: Raw request with webhook payload
        db: Database client
        x_signature: Webhook signature from header

    Returns:
        Processing status

    Raises:
        HTTPException: If signature verification fails
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify webhook signature
    client = LemonSqueezyClient()
    if client.webhook_secret and x_signature:
        is_valid = client.verify_webhook_signature(
            payload=body,
            signature=x_signature,
            secret=client.webhook_secret,
        )
        if not is_valid:
            logger.warning("Invalid webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

    # Parse webhook event
    try:
        event_data = await request.json()
        event = WebhookEvent(**event_data)
    except Exception as e:
        logger.error(f"Error parsing webhook event: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload",
        ) from e

    # Handle the event
    result = await handle_webhook_event(event, db)

    return WebhookResponse(
        status=result["status"],
        message=result["message"],
    )


@router.get("/subscription", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: CurrentUser,
    db: DatabaseDep,
):
    """
    Get current user's subscription status.
    Requires authentication.

    Args:
        current_user: Authenticated user
        db: Database client

    Returns:
        Subscription status
    """
    user_id = current_user.get("id")

    # Check for active subscription
    try:
        subscription_response = (
            db.table("subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if subscription_response.data and len(subscription_response.data) > 0:
            sub = subscription_response.data[0]
            return SubscriptionStatus(
                active=True,
                tier=sub["tier"],
                subscription_id=sub["subscription_id"],
                status=sub["status"],
                current_period_start=sub.get("current_period_start"),
                current_period_end=sub.get("current_period_end"),
                cancel_at=sub.get("cancel_at"),
            )

        # Check for one-time purchase
        purchase_response = (
            db.table("purchases")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .order("purchased_at", desc=True)
            .limit(1)
            .execute()
        )

        if purchase_response.data and len(purchase_response.data) > 0:
            purchase = purchase_response.data[0]
            return SubscriptionStatus(
                active=True,
                tier=purchase["tier"],
                subscription_id=None,
                status="active",
            )

        # No active subscription or purchase
        return SubscriptionStatus(active=False)

    except Exception as e:
        logger.error(f"Error fetching subscription status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription status",
        ) from e


@router.post("/verify-license", response_model=LicenseValidationResponse)
async def verify_license(request: LicenseValidationRequest, db: DatabaseDep):
    """
    Verify a license key.
    Public endpoint - no authentication required.

    Args:
        request: License validation request
        db: Database client

    Returns:
        License validation result
    """
    try:
        # Check in our database first
        purchase_response = (
            db.table("purchases")
            .select("*")
            .eq("license_key", request.license_key)
            .limit(1)
            .execute()
        )

        if purchase_response.data and len(purchase_response.data) > 0:
            purchase = purchase_response.data[0]
            return LicenseValidationResponse(
                valid=True,
                tier=purchase["tier"],
                purchased_at=purchase.get("purchased_at"),
                expires_at=purchase.get("expires_at"),
                status=purchase["status"],
            )

        # If not found in DB, try LemonSqueezy API
        client = LemonSqueezyClient()
        if client.is_configured():
            try:
                validation_result = await client.validate_license_key(request.license_key)
                if validation_result.get("valid"):
                    return LicenseValidationResponse(
                        valid=True,
                        tier="unknown",
                        status="active",
                    )
            except Exception as e:
                logger.error(f"Error validating license with LemonSqueezy: {e}")

        # License not found or invalid
        return LicenseValidationResponse(valid=False)

    except Exception as e:
        logger.error(f"Error verifying license: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify license",
        ) from e
