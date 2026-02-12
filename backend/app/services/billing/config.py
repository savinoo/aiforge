"""
Billing configuration and pricing tiers for AIForge.
"""

from typing import Dict, List, TypedDict


class PricingTierConfig(TypedDict):
    """Pricing tier configuration."""
    name: str
    price: int
    currency: str
    features: List[str]


# Pricing tiers for AIForge boilerplate
PRICING_TIERS: Dict[str, PricingTierConfig] = {
    "starter": {
        "name": "Starter",
        "price": 99,
        "currency": "USD",
        "features": [
            "FastAPI + Next.js boilerplate",
            "Supabase auth & DB",
            "Basic RAG pipeline",
            "Email support",
            "6 months updates",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 199,
        "currency": "USD",
        "features": [
            "Everything in Starter",
            "Full RAG with citations",
            "AI agent framework",
            "WhatsApp integration",
            "Multi-tenancy",
            "1 year updates",
            "Discord community",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 299,
        "currency": "USD",
        "features": [
            "Everything in Pro",
            "Priority support",
            "Custom integrations",
            "Lifetime updates",
            "1-on-1 onboarding call",
            "Source code license",
        ],
    },
}


def get_tier_config(tier: str) -> PricingTierConfig:
    """
    Get pricing tier configuration.

    Args:
        tier: Tier name (starter, pro, enterprise)

    Returns:
        Pricing tier configuration

    Raises:
        ValueError: If tier is invalid
    """
    if tier not in PRICING_TIERS:
        raise ValueError(f"Invalid tier: {tier}. Must be one of {list(PRICING_TIERS.keys())}")
    return PRICING_TIERS[tier]
