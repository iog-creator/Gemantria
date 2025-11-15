-- Migration 041: Control LM Usage Budget
-- Purpose: Create control.lm_usage_budget table for Phase-6 6B (LM usage budgets & rate-tracking)
-- Related: Phase-6 Plan (6B), ADR-066 (LM Studio Control-Plane Integration)

CREATE TABLE IF NOT EXISTS control.lm_usage_budget (
    app_name text PRIMARY KEY,
    window_days integer NOT NULL DEFAULT 7,
    max_requests integer NOT NULL,
    max_tokens integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lm_usage_budget_window ON control.lm_usage_budget (window_days);

COMMENT ON TABLE control.lm_usage_budget IS 'Phase-6 6B: LM Studio usage budgets per app_name';
COMMENT ON COLUMN control.lm_usage_budget.app_name IS 'Application identifier (e.g., "gemantria.runtime", "storymaker", "biblescholar")';
COMMENT ON COLUMN control.lm_usage_budget.window_days IS 'Budget window in days (default: 7)';
COMMENT ON COLUMN control.lm_usage_budget.max_requests IS 'Maximum number of requests allowed in the window';
COMMENT ON COLUMN control.lm_usage_budget.max_tokens IS 'Maximum tokens (prompt + completion) allowed in the window';

