"""
LemonSqueezy API client for billing operations.
"""

import hmac
import hashlib
import logging
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LemonSqueezyClient:
    """Client for interacting with LemonSqueezy API."""

    BASE_URL = "https://api.lemonsqueezy.com/v1"

    def __init__(self):
        """Initialize LemonSqueezy client."""
        self.api_key = settings.lemonsqueezy_api_key
        self.store_id = settings.lemonsqueezy_store_id
        self.webhook_secret = settings.lemonsqueezy_webhook_secret

    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def is_configured(self) -> bool:
        """Check if LemonSqueezy is configured."""
        return bool(self.api_key and self.store_id)

    async def create_checkout(
        self,
        product_id: str,
        variant_id: str,
        user_email: str,
        user_id: str,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a checkout session.

        Args:
            product_id: LemonSqueezy product ID
            variant_id: LemonSqueezy variant ID
            user_email: Customer email
            user_id: User ID to associate with purchase
            custom_data: Additional custom data

        Returns:
            Checkout session data including URL

        Raises:
            ValueError: If LemonSqueezy is not configured
            httpx.HTTPError: If API request fails
        """
        if not self.is_configured():
            raise ValueError("LemonSqueezy is not configured. Set API key and store ID.")

        checkout_data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": user_email,
                        "custom": {
                            "user_id": user_id,
                            **(custom_data or {}),
                        },
                    },
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": self.store_id,
                        }
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": variant_id,
                        }
                    },
                },
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/checkouts",
                headers=self.headers,
                json=checkout_data,
            )
            response.raise_for_status()
            return response.json()

    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details.

        Args:
            subscription_id: LemonSqueezy subscription ID

        Returns:
            Subscription data

        Raises:
            ValueError: If LemonSqueezy is not configured
            httpx.HTTPError: If API request fails
        """
        if not self.is_configured():
            raise ValueError("LemonSqueezy is not configured. Set API key and store ID.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/subscriptions/{subscription_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_license_key(self, license_key_id: str) -> Dict[str, Any]:
        """
        Get license key details.

        Args:
            license_key_id: LemonSqueezy license key ID

        Returns:
            License key data

        Raises:
            ValueError: If LemonSqueezy is not configured
            httpx.HTTPError: If API request fails
        """
        if not self.is_configured():
            raise ValueError("LemonSqueezy is not configured. Set API key and store ID.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/license-keys/{license_key_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def validate_license_key(self, license_key: str) -> Dict[str, Any]:
        """
        Validate a license key.

        Args:
            license_key: License key to validate

        Returns:
            Validation result

        Raises:
            ValueError: If LemonSqueezy is not configured
            httpx.HTTPError: If API request fails
        """
        if not self.is_configured():
            raise ValueError("LemonSqueezy is not configured. Set API key and store ID.")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/licenses/validate",
                headers=self.headers,
                json={
                    "license_key": license_key,
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify LemonSqueezy webhook signature using HMAC SHA256.

        Args:
            payload: Raw webhook payload bytes
            signature: Signature from X-Signature header
            secret: Webhook secret

        Returns:
            True if signature is valid, False otherwise
        """
        if not secret:
            logger.warning("Webhook secret not configured, skipping signature verification")
            return True  # Allow webhooks if secret is not set (development mode)

        try:
            # LemonSqueezy uses HMAC SHA256
            expected_signature = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
