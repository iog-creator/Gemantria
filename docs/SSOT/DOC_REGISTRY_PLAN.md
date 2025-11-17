# Postgres Doc Registry Plan — Eliminating Share Drift

## 0. Problem Statement

We have repeatedly hit **documentation drift** because:

- The `share/` directory is a **derived copy** of key docs (via `make share.sync`) but:

  - It can fall out of sync or be partially updated.

  - AI tools sometimes **treat `share/` as SSOT**, trusting timestamps or contents that are stale.

- Humans try to give AI the latest context via uploaded files from `share/`, but only some of those

  files are actually current.

- This creates a mismatch: the real SSOT is in **git + Postgres**, while AI is reading **cached

  copies**.

We need a **Postgres-backed documentation registry** so:

- The database knows which docs are canonical, their latest commit/time, and where they live.

- `share/` is **explicitly derived**, never treated as authoritative.

- AI tools (GPT/Cursor) can query the registry instead of guessing from `share/` timestamps.

This plan describes how to build that registry.

---

## 1. Goals

1. **Make Postgres the SSOT for docs metadata**

   - Track canonical docs (SSOT files) in control-plane tables.

   - Record paths, hashes, commit info, and last-sync times.

2. **Demote `share/` to a derived view**

   - `share/` becomes a **projection** of selected docs for tools/UI, not a source of truth.

   - All sync behavior is driven by the **doc registry**, not by ad-hoc file lists.

3. **Give AI a reliable way to know "what is fresh"**

   - Ability to ask: "What are the latest versions of AGENTS, MASTER_PLAN, RULES_INDEX, etc.?"

   - Ability to detect when uploaded files are stale vs. HEAD.

4. **Integrate with existing governance**

   - Reuse the `control` schema (Phase-7 governance).

   - Align with `GOVERNANCE_DB_SSOT.md` and the rules DB SSOT work (OPS-007/008).

---

## 2. Scope

### In Scope (Phase-1: Registry Metadata Only)

- New control-plane tables for doc metadata and sync state.

- Ingestion script to scan **canonical doc locations**:

  - `AGENTS.md`, `RULES_INDEX.md`, `MASTER_PLAN.md`, `GPT_REFERENCE_GUIDE.md`

  - `docs/SSOT/**`

  - `docs/runbooks/**`

- Tracking for:

  - File path (in repo)

  - Logical name/role (e.g. `AGENTS_ROOT`, `MASTER_PLAN`, `GOVERNANCE_DB_SSOT_RUNBOOK`)

  - Git commit / short SHA

  - SHA-256 content hash

  - Last-seen mod time

  - Whether it is **SSOT** vs **derived** (e.g. `share/` copies)

### Future Scope (Phase-2+)

- Attach tags (e.g. `phase7`, `governance`, `lm`, `bible_db`).

- Track cross-references (doc → rules, doc → migrations, doc → scripts).

- UI surfaces (Atlas dashboards, web pages) for doc health and drift.

---

## 3. Proposed Control-Plane Schema

All tables live in the existing `control` schema.

### 3.1 `control.doc_registry`

Tracks canonical and derived documents.

```sql

CREATE TABLE control.doc_registry (

    doc_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    logical_name  TEXT NOT NULL,         -- e.g. "AGENTS_ROOT", "MASTER_PLAN", "GOVERNANCE_DB_SSOT_RUNBOOK"

    role          TEXT NOT NULL,         -- e.g. "ssot", "runbook", "analysis", "derived"

    repo_path     TEXT NOT NULL,         -- e.g. "AGENTS.md", "docs/SSOT/MASTER_PLAN.md"

    share_path    TEXT,                  -- e.g. "share/AGENTS.md" (if derived)

    is_ssot       BOOLEAN NOT NULL,      -- TRUE for repo canonical docs, FALSE for derived views

    enabled       BOOLEAN NOT NULL DEFAULT TRUE,

    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

```

### 3.2 `control.doc_version`

Tracks specific versions of docs (per commit/hash).

```sql

CREATE TABLE control.doc_version (

    id           BIGSERIAL PRIMARY KEY,

    doc_id       UUID NOT NULL REFERENCES control.doc_registry(doc_id) ON DELETE CASCADE,

    git_commit   TEXT,                   -- short SHA or full SHA

    content_hash TEXT NOT NULL,          -- SHA-256 of the file contents

    size_bytes   BIGINT NOT NULL,

    recorded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

```

### 3.3 `control.doc_sync_state`

Tracks derived copies (like `share/`) and last sync status.

```sql

CREATE TABLE control.doc_sync_state (

    id             BIGSERIAL PRIMARY KEY,

    doc_id         UUID NOT NULL REFERENCES control.doc_registry(doc_id) ON DELETE CASCADE,

    target         TEXT NOT NULL,        -- e.g. "share", "atlas_export"

    last_synced_at TIMESTAMPTZ,

    last_hash      TEXT,                 -- content hash at last sync

    status         TEXT NOT NULL,        -- "ok", "stale", "error"

    message        TEXT,                 -- optional human-readable details

    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

```

---

## 4. Ingestion & Sync Flow

### 4.1 Ingestion Script

**File (planned)**: `scripts/governance/ingest_docs_to_db.py`

**Responsibilities:**

1. Walk a curated set of directories:

   * `AGENTS.md`, `RULES_INDEX.md`, `MASTER_PLAN.md`

   * `docs/SSOT/**`, `docs/runbooks/**`

2. For each file:

   * Compute `content_hash` (SHA-256).

   * Record size.

   * Optionally capture git commit (via `git rev-parse HEAD` and/or `git log`).

3. Upsert into:

   * `control.doc_registry` (logical_name + repo_path).

   * `control.doc_version` (new row per unique hash).

**Important**: Uses existing **DSN loaders and engines** (no raw `os.getenv`), mirroring `ingest_rules_to_db.py`.

### 4.2 Sync Integration (Share)

**File (existing)**: `scripts/sync_share.py`

**Planned extension**:

* Read from `control.doc_registry` (where `role = 'ssot'` and `share_path IS NOT NULL`).

* Use `control.doc_sync_state` to:

  * Decide what needs copying.

  * Mark `status` as `"ok"` or `"stale"` depending on hashes.

* This ensures `share/` is always **explicitly** labelled as derived, with an audit trail.

---

## 5. Governance & Modes

### 5.1 HINT vs STRICT

* **HINT**:

  * Missing doc_registry entries or stale `share/` entries are **warnings**, not hard failures.

  * Used for PRs and local development.

* **STRICT**:

  * Used on tags/releases.

  * If a doc marked `is_ssot = TRUE` is missing or mismatched, CI fails.

  * If `share/` is stale for a required doc, CI can fail or emit a strong warning.

### 5.2 Guard (Future)

**File (planned)**: `scripts/guards/guard_docs_db_ssot.py`

* Validates:

  * All required logical docs are present (AGENTS, MASTER_PLAN, RULES_INDEX, etc.).

  * `is_ssot` docs have at least one recent `doc_version`.

  * `share/` entries that exist are in sync (hash matches latest version).

---

## 6. Integration with Existing Systems

* Reuses `control` schema and existing governance SSOT work:

  * `GOVERNANCE_DB_SSOT.md`

  * `ingest_rules_to_db.py`

  * `guard_rules_db_ssot.py`

* Interacts with:

  * `scripts/sync_share.py` (Rule-030).

  * `make housekeeping` (Rule-058) as an additional guard/step.

* Provides a future API for:

  * `pmagent` commands like `pmagent docs.status` or `pmagent docs.list`.

---

## 7. Phasing

### Phase-8A — Schema + Ingestion

* Add migrations for `control.doc_registry`, `control.doc_version`, `control.doc_sync_state`.

* Implement `scripts/governance/ingest_docs_to_db.py`.

* Add Makefile targets:

  * `governance.ingest.docs`

  * `governance.ingest.docs.dryrun`

### Phase-8B — Guard + Share Integration

* Implement `scripts/guards/guard_docs_db_ssot.py`.

* Wire into `make guards.all` / CI in HINT mode.

* Extend `scripts/sync_share.py` to consume the registry and update `doc_sync_state`.

### Phase-8C — UI & Atlas

* Add Atlas dashboards and/or API endpoints to visualize doc health.

* Optionally add `pmagent docs.status`.

---

## 8. Non-Goals (For Now)

* Storing full document contents in Postgres (we track metadata and hashes only).

* Rewriting share/ structure or semantics beyond "derived, not SSOT".

* Heavy-weight content diffing; basic hashes and timestamps are enough for v1.

---

## 9. Key Principle

> **Postgres + repo docs are the only SSOT.

> `share/` is a cached view, never the authority.**

All AI agents (GPT, Cursor, etc.) should:

* Prefer `docs/SSOT/**`, `AGENTS.md`, `MASTER_PLAN.md`, and the **doc registry** as truth.

* Treat `share/` as a **convenience mirror** only.

---

## Phase-8B — Registry-driven `share.sync`

With `scripts/sync_share.py` now consulting `control.doc_registry`:

- When the DB is available and the registry has `share_path` entries:

  - `share/` is synced from the registry (repo_path → share_path).

  - `SHARE_MANIFEST.json` becomes a legacy fallback only.

- When the DB is unavailable or empty:

  - `share.sync` falls back to the manifest-based behavior (if present).

  - This preserves existing pipelines while we roll out the registry.

Key principle:

> The registry defines **which docs** should be mirrored into `share/`.

> The manifest is a compatibility fallback, not the SSOT.

---

## AGENTS.md Framework — Tier-0 Registry Docs

The AGENTS.md system is not just a single file; it is a **documentation framework**

for all agents and modules:

- Root `AGENTS.md` — global index and contract for the agent ecosystem.

- Module- and directory-level `AGENTS.md` / `*_AGENTS.md` — local contracts

  describing responsibilities, invariants, and commands for each slice of the system.

Registry rules:

- **All** `AGENTS*.md` files under the repo (excluding `share/` and virtualenvs)

  MUST be tracked in `control.doc_registry` as SSOT docs.

- Root `AGENTS.md` is registered as:

  - `logical_name = "AGENTS_ROOT"`

  - `role = "agent_framework_index"`

- All other AGENTS docs are registered as:

  - `logical_name = "AGENTS::<relative_path>"`

  - `role = "agent_framework"`

These docs are Tier-0:

- They MUST have `is_ssot = TRUE`.

- They MUST be `enabled = TRUE` while the module is active.

- Guards may treat missing AGENTS entries as STRICT failures in DB-on verification

  runs (similar to rules and core SSOT docs).

