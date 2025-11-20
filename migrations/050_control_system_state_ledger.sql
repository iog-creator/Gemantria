-- Migration 050: System State Ledger
-- Purpose: Track hashes of SSOT artifacts (AGENTS.md, SSOT docs, share exports)
-- Rule References: Rule 006 (AGENTS.md Governance), Rule 027 (Docs Sync Gate), Rule 030 (Share Sync)

CREATE TABLE IF NOT EXISTS control.system_state_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    source_of_truth TEXT NOT NULL,
    hash TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    verified_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'unknown'
);

-- Index for efficient lookups by name
CREATE INDEX IF NOT EXISTS idx_system_state_ledger_name ON control.system_state_ledger(name);

-- Index for efficient lookups by source_of_truth
CREATE INDEX IF NOT EXISTS idx_system_state_ledger_source ON control.system_state_ledger(source_of_truth);

-- Index for efficient lookups by status
CREATE INDEX IF NOT EXISTS idx_system_state_ledger_status ON control.system_state_ledger(status);

COMMENT ON TABLE control.system_state_ledger IS 'Tracks current hashes of SSOT artifacts (AGENTS.md, SSOT docs, share exports) for consistency verification';
COMMENT ON COLUMN control.system_state_ledger.name IS 'Artifact name (e.g., "AGENTS.md", "MASTER_PLAN.md")';
COMMENT ON COLUMN control.system_state_ledger.source_of_truth IS 'Source location (e.g., "root", "docs/SSOT", "share/exports")';
COMMENT ON COLUMN control.system_state_ledger.hash IS 'SHA256 hash of artifact content';
COMMENT ON COLUMN control.system_state_ledger.generated_at IS 'When this ledger entry was created';
COMMENT ON COLUMN control.system_state_ledger.verified_at IS 'When this ledger entry was last verified';
COMMENT ON COLUMN control.system_state_ledger.status IS 'Status: unknown, current, stale, missing';

