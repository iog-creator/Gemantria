# DOC_STRATEGY.md — Gemantria Documentation & DMS Hierarchy

This document defines how Gemantria organizes, governs, and cleans its documentation surfaces.
It is the SSOT for how AGENTS.md, the DMS, and the filesystem interact.

## 1. Layered Truth Model

Gemantria uses a layered model for truth:

1. **Orchestrator (human)** — product decisions, governance intent.

2. **Contracts / SSOT docs** — PM/OPS contracts, PHASE docs, SHARE_SURFACE_CONTRACT, etc.

3. **AGENTS surfaces (`AGENTS.md`)** — human/AI-readable maps of agents, tools, and key doc surfaces.

4. **DMS registry (`control.doc_registry`)** — structured inventory and lifecycle metadata:

   - `repo_path`, `share_path`

   - `enabled` (live vs archived)

   - `importance` (critical/high/medium/low/unknown)

   - `tags` (e.g., `ssot`, `runbook`, `agent_framework`, `pdf`)

   - `owner_component` (e.g., `root`, `pmagent`, `docs`)

5. **Filesystem layout** — where files actually live; must match the registry.

## 2. AGENTS.md Rules

- Root `AGENTS.md` has role `CANONICAL_GLOBAL` and is always:

  - `importance = 'critical'`

  - `enabled = true`

  - `repo_path` is a live, non-archive location

  - `tags` includes `ssot`, `agent_framework`, and `agent_framework_index`

- Subsystem-level `AGENTS.md` files (e.g., in `pmagent/`, `docs/`, `tests/`) are:

  - `importance >= 'high'` (typically `high`)

  - `enabled = true`

  - tagged with `ssot` and `agent_framework` (at minimum)

  - never placed under `archive/` or other retired dirs.

- No automated process (cleanup, archive, migrations) may:

  - set `enabled = false` for an AGENTS row,

  - set `importance` below `high`,

  - move an AGENTS file under `archive/`.

Any plan or script that proposes such a change is considered a **bug**, not a policy.

## 3. DMS Lifecycle Rules

- The DMS is the SSOT for:

  - doc existence and paths,

  - lifecycle (enabled vs archived),

  - importance tiers,

  - tags and ownership for analytics and automation.

- Housekeeping ingestion (`scripts/governance/ingest_docs_to_db.py`) operates in **Hybrid mode**:

  - It **fills in** `importance`, `tags`, and `owner_component` for new or unknown docs.

  - It **respects manual overrides**: it does not downgrade existing `importance` or strip tags.

- Special heuristics (baked into ingestion):

  - Root `AGENTS.md` → `critical`, tags `['ssot', 'agent_framework', 'agent_framework_index']`.

  - Other `AGENTS.md` → `high`, tags include `['ssot', 'agent_framework']`.

  - `docs/SSOT/**` → `critical`, tags `['ssot']`.

  - `docs/runbooks/**` → `high`, tags `['runbook']`.

  - PDFs → `medium`, tags include `['documentation', 'pdf']`.

## 4. Archive & Cleanup Policy

- Archival is driven by the DMS:

  - Candidates: docs with `importance = 'low'` and `enabled = true`.

  - Archive moves: into `archive/docs_legacy/` (or appropriate archive namespace).

  - After move: `enabled = false` and `repo_path` updated in `control.doc_registry`.

- **AGENTS.md is explicitly excluded** from archival:

  - No row with `repo_path` ending in `AGENTS.md` should ever have `importance = 'low'` or `enabled = false`.

  - Any such state must be treated as a critical bug.

## 5. Enforcement & Guards

- `scripts/guards/guard_reality_green.py` is responsible for checking:

  - AGENTS–DMS alignment,

  - DMS lifecycle invariants,

  - that there are no `importance = 'low' AND enabled = true` leftovers after cleanup.

- Reality Green should fail in STRICT mode if:

  - any AGENTS row is misclassified (importance too low, disabled, archived),

  - DMS and filesystem disagree on AGENTS presence.

This strategy is the contract OA, PM, and Cursor must follow when evolving the documentation system.
