-- Migration 054: Hint Registry
-- Purpose: DMS-backed registry for hints with REQUIRED vs SUGGESTED semantics
-- Context: DMS Hint Registry Implementation Plan
-- Rule References: Rule 050 (OPS Contract), Rule 051 (Cursor Insight), Rule 026 (System Enforcement Bridge)
-- ADR: ADR-059 (Hint Registry Design)

BEGIN;

-- Create hint_registry table
CREATE TABLE IF NOT EXISTS control.hint_registry (
    hint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    logical_name TEXT NOT NULL UNIQUE,  -- e.g., "docs.dms_only", "status.local_gates_first"
    scope TEXT NOT NULL,               -- e.g., "handoff", "status_api", "agentpm", "biblescholar"
    applies_to JSONB NOT NULL,         -- selectors: {"flow": "handoff.generate", "rule": "050", "agent": "pm"}
    kind TEXT NOT NULL CHECK (kind IN ('REQUIRED', 'SUGGESTED', 'DEBUG')),
    injection_mode TEXT NOT NULL CHECK (injection_mode IN ('PRE_PROMPT', 'POST_PROMPT', 'TOOL_CALL', 'META_ONLY')),
    payload JSONB NOT NULL,            -- structured hint content
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 0, -- for ordering within same kind
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Ensure applies_to always has a 'flow' key
    CONSTRAINT hint_registry_flow_required CHECK ((applies_to ? 'flow'))
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_hint_registry_scope ON control.hint_registry (scope) WHERE enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_hint_registry_applies_to ON control.hint_registry USING GIN (applies_to) WHERE enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_hint_registry_kind ON control.hint_registry (kind, priority) WHERE enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_hint_registry_flow ON control.hint_registry ((applies_to->>'flow')) WHERE enabled = TRUE;

-- Comments
COMMENT ON TABLE control.hint_registry IS 'DMS-backed registry for hints with REQUIRED vs SUGGESTED semantics. Hints are embedded into envelopes (handoff, capability_session, reality_check, status) and enforced by guards.';
COMMENT ON COLUMN control.hint_registry.logical_name IS 'Unique identifier for the hint (e.g., "docs.dms_only", "status.local_gates_first")';
COMMENT ON COLUMN control.hint_registry.scope IS 'Scope category (e.g., "handoff", "status_api", "agentpm", "biblescholar")';
COMMENT ON COLUMN control.hint_registry.applies_to IS 'JSONB selectors: must include "flow" key, may include "rule", "agent", "scope" for filtering';
COMMENT ON COLUMN control.hint_registry.kind IS 'Hint kind: REQUIRED (contractual), SUGGESTED (advisory), DEBUG (development only)';
COMMENT ON COLUMN control.hint_registry.injection_mode IS 'Where hint is injected: PRE_PROMPT, POST_PROMPT, TOOL_CALL, META_ONLY';
COMMENT ON COLUMN control.hint_registry.payload IS 'Structured hint content: {"text": "...", "commands": [...], "constraints": {...}, "metadata": {...}}';
COMMENT ON COLUMN control.hint_registry.priority IS 'Ordering within same kind (lower = higher priority)';

COMMIT;

