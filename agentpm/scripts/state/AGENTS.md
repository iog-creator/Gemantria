# AGENTS.md - State Management Scripts

## Purpose

This directory contains scripts for managing and verifying the system state ledger, which tracks critical artifacts (AGENTS.md files, SSOT docs, exports) to ensure consistency across the codebase.

## Components

### `ledger_sync.py`

Synchronizes file hashes to the `control.system_state_ledger` table.

**Usage:**
```bash
python -m agentpm.scripts.state.ledger_sync
pmagent state sync
make state.sync
```

**Functionality:**
- Computes SHA256 hashes for tracked artifacts
- Writes/updates ledger entries in Postgres
- Ensures all critical files are tracked

### `ledger_verify.py`

Verifies system state ledger against current file hashes, with LLM-powered intelligent analysis.

**Usage:**
```bash
python -m agentpm.scripts.state.ledger_verify
pmagent state verify
make state.verify
```

**Functionality:**
- Compares current file hashes against ledger
- Identifies stale (out of sync) and missing artifacts
- Uses Granite 4.0 for intelligent, actionable analysis
- Provides specific next steps (e.g., "Run 'make state.sync' to update ledger for AGENTS.md")
- Explains impact (e.g., "This blocks reality.green from passing")

**LLM Integration:**
- Uses Granite 4.0 explicitly for reasoning (not routing through local_agent slot)
- Falls back gracefully to rule-based messages if LM unavailable
- Temperature: 0.6 for reasoning (per Granite best practices)

## Rule References

- **Rule 006**: AGENTS.md Governance
- **Rule 027**: Docs Sync Gate
- **Rule 030**: Share Sync
- **Rule 069**: Reality Green

## Tracked Artifacts

The ledger tracks:
- Root `AGENTS.md`
- SSOT docs (`MASTER_PLAN.md`, `RULES_INDEX.md`, etc.)
- Control-plane exports (`system_health.json`, `lm_indicator.json`)
- Docs-control exports (`canonical.json`, `summary.json`)

## Integration

These scripts are called by:
- `make reality.green` - Full system truth gate
- `make state.sync` - Update ledger after changes
- `make state.verify` - Verify ledger consistency

