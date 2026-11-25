CREATE TABLE IF NOT EXISTS pricing_engine_activity (
    id BIGSERIAL PRIMARY KEY,
    actor_role VARCHAR(32) NOT NULL DEFAULT 'ANONYMOUS',
    actor_id BIGINT NULL,
    action VARCHAR(80) NOT NULL,
    module VARCHAR(80) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS',
    duration_ms INTEGER NULL CHECK (duration_ms IS NULL OR duration_ms >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pricing_engine_activity_created_at
    ON pricing_engine_activity (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_pricing_engine_activity_module_action
    ON pricing_engine_activity (module, action);

CREATE INDEX IF NOT EXISTS idx_pricing_engine_activity_actor
    ON pricing_engine_activity (actor_role, actor_id);
