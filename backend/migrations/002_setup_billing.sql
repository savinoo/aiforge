-- Billing tables for LemonSqueezy integration
-- Supports both one-time purchases and subscriptions

-- ============================================================================
-- PURCHASES TABLE
-- ============================================================================
-- Stores one-time purchases of AIForge boilerplate tiers
CREATE TABLE IF NOT EXISTS purchases (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL CHECK (tier IN ('starter', 'pro', 'enterprise')),
    order_id VARCHAR(100) UNIQUE,
    license_key VARCHAR(100),
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'refunded')),
    purchased_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user lookup
CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);

-- Index for order lookup from webhooks
CREATE INDEX IF NOT EXISTS idx_purchases_order_id ON purchases(order_id);

-- Index for license key validation
CREATE INDEX IF NOT EXISTS idx_purchases_license_key ON purchases(license_key);

-- Index for active purchases
CREATE INDEX IF NOT EXISTS idx_purchases_status ON purchases(status);


-- ============================================================================
-- SUBSCRIPTIONS TABLE
-- ============================================================================
-- Stores recurring subscriptions (if using subscription model)
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id VARCHAR(100) UNIQUE NOT NULL,
    tier VARCHAR(50) NOT NULL CHECK (tier IN ('starter', 'pro', 'enterprise')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'paused')),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user lookup
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);

-- Index for subscription lookup from webhooks
CREATE INDEX IF NOT EXISTS idx_subscriptions_subscription_id ON subscriptions(subscription_id);

-- Index for active subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);


-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Enable RLS to ensure users can only see their own billing data
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own purchases" ON purchases;
DROP POLICY IF EXISTS "Users can view own subscriptions" ON subscriptions;
DROP POLICY IF EXISTS "Service role can manage purchases" ON purchases;
DROP POLICY IF EXISTS "Service role can manage subscriptions" ON subscriptions;

-- Users can view their own purchases
CREATE POLICY "Users can view own purchases"
    ON purchases
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can view their own subscriptions
CREATE POLICY "Users can view own subscriptions"
    ON subscriptions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can manage all purchases (for webhooks)
CREATE POLICY "Service role can manage purchases"
    ON purchases
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Service role can manage all subscriptions (for webhooks)
CREATE POLICY "Service role can manage subscriptions"
    ON subscriptions
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- ============================================================================
-- UPDATED_AT TRIGGER
-- ============================================================================
-- Automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS update_purchases_updated_at ON purchases;
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;

-- Create triggers for both tables
CREATE TRIGGER update_purchases_updated_at
    BEFORE UPDATE ON purchases
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE purchases IS 'One-time purchases of AIForge boilerplate tiers';
COMMENT ON TABLE subscriptions IS 'Recurring subscriptions (if using subscription model)';

COMMENT ON COLUMN purchases.tier IS 'Pricing tier: starter, pro, or enterprise';
COMMENT ON COLUMN purchases.order_id IS 'LemonSqueezy order ID';
COMMENT ON COLUMN purchases.license_key IS 'License key for boilerplate access';
COMMENT ON COLUMN purchases.amount_cents IS 'Purchase amount in cents';
COMMENT ON COLUMN purchases.metadata IS 'Additional data from LemonSqueezy (order_number, customer_id, etc.)';

COMMENT ON COLUMN subscriptions.subscription_id IS 'LemonSqueezy subscription ID';
COMMENT ON COLUMN subscriptions.current_period_start IS 'Start of current billing period';
COMMENT ON COLUMN subscriptions.current_period_end IS 'End of current billing period';
COMMENT ON COLUMN subscriptions.cancel_at IS 'Scheduled cancellation date (maintains access until this date)';
