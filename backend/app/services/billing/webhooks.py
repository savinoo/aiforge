"""
LemonSqueezy webhook event handlers.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from supabase import Client

from app.services.billing.models import WebhookEvent

logger = logging.getLogger(__name__)


async def handle_webhook_event(event: WebhookEvent, db: Client) -> Dict[str, str]:
    """
    Handle LemonSqueezy webhook event.

    Args:
        event: Webhook event data
        db: Supabase client

    Returns:
        Status dict with processing result
    """
    event_name = event.meta.get("event_name")
    logger.info(f"Processing webhook event: {event_name}")

    handlers = {
        "order_created": handle_order_created,
        "subscription_created": handle_subscription_created,
        "subscription_updated": handle_subscription_updated,
        "subscription_cancelled": handle_subscription_cancelled,
        "license_key_created": handle_license_key_created,
    }

    handler = handlers.get(event_name)
    if not handler:
        logger.warning(f"No handler for event: {event_name}")
        return {"status": "ignored", "message": f"No handler for event: {event_name}"}

    try:
        await handler(event, db)
        return {"status": "success", "message": f"Processed {event_name}"}
    except Exception as e:
        logger.error(f"Error handling {event_name}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def handle_order_created(event: WebhookEvent, db: Client) -> None:
    """
    Handle order_created event.
    Records the purchase and grants access to the user.

    Args:
        event: Webhook event
        db: Supabase client
    """
    data = event.data
    attributes = data.get("attributes", {})
    custom_data = attributes.get("custom_data", {})

    user_id = custom_data.get("user_id")
    if not user_id:
        logger.warning("No user_id in order custom_data, skipping")
        return

    # Extract order details
    order_id = str(data.get("id"))
    tier = custom_data.get("tier", "starter")
    amount = attributes.get("total", 0)
    currency = attributes.get("currency", "USD")

    # Create purchase record
    purchase_data = {
        "user_id": user_id,
        "tier": tier,
        "order_id": order_id,
        "amount_cents": amount,
        "currency": currency,
        "status": "active",
        "purchased_at": datetime.utcnow().isoformat(),
        "metadata": {
            "order_number": attributes.get("order_number"),
            "customer_id": attributes.get("customer_id"),
        },
    }

    db.table("purchases").insert(purchase_data).execute()
    logger.info(f"Created purchase record for user {user_id}, tier {tier}")


async def handle_subscription_created(event: WebhookEvent, db: Client) -> None:
    """
    Handle subscription_created event.
    Activates a subscription for the user.

    Args:
        event: Webhook event
        db: Supabase client
    """
    data = event.data
    attributes = data.get("attributes", {})
    custom_data = attributes.get("custom_data", {})

    user_id = custom_data.get("user_id")
    if not user_id:
        logger.warning("No user_id in subscription custom_data, skipping")
        return

    subscription_id = str(data.get("id"))
    tier = custom_data.get("tier", "pro")

    # Create subscription record
    subscription_data = {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "tier": tier,
        "status": attributes.get("status", "active"),
        "current_period_start": attributes.get("renews_at"),
        "current_period_end": attributes.get("ends_at"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    db.table("subscriptions").upsert(subscription_data, on_conflict="subscription_id").execute()
    logger.info(f"Created subscription {subscription_id} for user {user_id}")


async def handle_subscription_updated(event: WebhookEvent, db: Client) -> None:
    """
    Handle subscription_updated event.
    Updates subscription status and billing period.

    Args:
        event: Webhook event
        db: Supabase client
    """
    data = event.data
    attributes = data.get("attributes", {})
    subscription_id = str(data.get("id"))

    # Update subscription record
    update_data = {
        "status": attributes.get("status"),
        "current_period_start": attributes.get("renews_at"),
        "current_period_end": attributes.get("ends_at"),
        "updated_at": datetime.utcnow().isoformat(),
    }

    db.table("subscriptions").update(update_data).eq("subscription_id", subscription_id).execute()
    logger.info(f"Updated subscription {subscription_id}")


async def handle_subscription_cancelled(event: WebhookEvent, db: Client) -> None:
    """
    Handle subscription_cancelled event.
    Marks subscription as cancelled but maintains access until end of period.

    Args:
        event: Webhook event
        db: Supabase client
    """
    data = event.data
    attributes = data.get("attributes", {})
    subscription_id = str(data.get("id"))

    # Update subscription with cancellation date
    update_data = {
        "status": "cancelled",
        "cancel_at": attributes.get("ends_at"),
        "updated_at": datetime.utcnow().isoformat(),
    }

    db.table("subscriptions").update(update_data).eq("subscription_id", subscription_id).execute()
    logger.info(f"Cancelled subscription {subscription_id}, access until {attributes.get('ends_at')}")


async def handle_license_key_created(event: WebhookEvent, db: Client) -> None:
    """
    Handle license_key_created event.
    Stores the license key with the purchase.

    Args:
        event: Webhook event
        db: Supabase client
    """
    data = event.data
    attributes = data.get("attributes", {})

    license_key = attributes.get("key")
    order_id = str(attributes.get("order_id"))

    if not license_key or not order_id:
        logger.warning("Missing license_key or order_id in event")
        return

    # Update purchase with license key
    db.table("purchases").update({"license_key": license_key}).eq("order_id", order_id).execute()
    logger.info(f"Added license key to order {order_id}")
