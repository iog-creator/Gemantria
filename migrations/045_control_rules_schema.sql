-- Migration: control.rules_schema
-- Purpose: Add rule_definition, rule_source, and guard_definition tables
-- Context: Phase-7 Governance DB SSOT (see docs/analysis/phase7_governance/GEMANTRIA_SYSTEM_COMPREHENSIVE_REPORT.md)
-- Notes:
--   - Control schema already exists from migration 040; CREATE SCHEMA here is idempotent.
--   - No data migration is performed in this file; ingestion is handled by scripts.

BEGIN;

CREATE SCHEMA IF NOT EXISTS control;

CREATE TABLE IF NOT EXISTS control.rule_definition (
    rule_id      TEXT PRIMARY KEY,            -- e.g. "000", "050", "068"
    name         TEXT NOT NULL,               -- short name, e.g. "ops-contract"
    status       TEXT NOT NULL,               -- "active", "deprecated", "reserved"
    description  TEXT,                        -- longer human-readable description
    severity     TEXT NOT NULL,               -- "HINT", "STRICT", "INFO"
    docs_path    TEXT,                        -- e.g. ".cursor/rules/050-ops-contract.mdc"
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS control.rule_source (
    id           BIGSERIAL PRIMARY KEY,
    rule_id      TEXT NOT NULL REFERENCES control.rule_definition(rule_id) ON DELETE CASCADE,
    source_type  TEXT NOT NULL,               -- "cursor_rules", "rules_index", "agents_md", etc.
    path         TEXT NOT NULL,               -- file path or logical source
    content_hash TEXT NOT NULL,               -- SHA-256 of the rule content
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS control.guard_definition (
    guard_id       TEXT PRIMARY KEY,          -- e.g. "guard_rules_db_ssot"
    name           TEXT NOT NULL,             -- human-readable name
    description    TEXT,                      -- free-form description
    rule_ids       TEXT[] NOT NULL DEFAULT '{}', -- rules enforced, e.g. '{"050","051"}'
    strict_default BOOLEAN NOT NULL DEFAULT FALSE,
    script_path    TEXT,                      -- e.g. "scripts/guards/guard_rules_db_ssot.py"
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
