# Share/ Folder Analysis & Purpose

**Date:** 2025-12-01  
**Status:** Active documentation

## Purpose Change

The `share/` folder has evolved from a simple export directory to a **first-class part of the codebase** that should be:

1. **Indexed by AI agents** (Cursor, PM agents, etc.)
2. **Tracked in DMS** (`control.doc_registry` with `share_path`)
3. **Synced from DMS** (not manually managed)
4. **Converted to Markdown** (all JSON exports become MD for readability)

## Current Structure (42 MD files)

### File Sources

#### 1. DMS-Synced Files (27 files)
Files copied from `control.doc_registry` where `share_path IS NOT NULL` and `enabled = TRUE`:

- SSOT documents (`docs/SSOT/*.md`)
- Runbooks (`docs/runbooks/*.md`)
- Planning documents (`MASTER_PLAN.md`, `NEXT_STEPS.md`)
- Agent documentation (`AGENTS.md`, `scripts_AGENTS.md`)
- All other documents explicitly registered with `share_path`

**Sync mechanism:** `scripts/sync_share.py` (runs during `make housekeeping`)

#### 2. JSON-to-MD Converted Files (15 files)
JSON exports generated during `pm.share.artifacts` and converted to Markdown:

**DMS Table Exports:**
- `doc_registry.md` - Full DMS document registry
- `doc_version.md` - Document version tracking
- `doc_sync_state.md` - Sync state tracking

**Governance Exports:**
- `governance_freshness.md` - Governance artifact freshness
- `hint_registry.md` - Runtime hints registry
- `kb_registry.md` - Knowledge base registry

**PM Exports:**
- `pm_snapshot.md` - System snapshot (from JSON export)
- `live_posture.md` - Live system posture
- `planning_context.md` - Planning context
- `planning_lane_status.md` - Planning lane status
- `schema_snapshot.md` - Schema snapshot

**Head Exports (partial):**
- `next_steps.head.md` - Head of NEXT_STEPS.md
- `pm_contract.head.md` - Head of PM_CONTRACT.md
- `agents_md.head.md` - Head of AGENTS.md

**Conversion mechanism:** `scripts/util/json_to_markdown.py` (runs during `make housekeeping`)

### Duplicates & Consolidation Opportunities

#### Known Duplicates:
1. **`pm.snapshot.md` vs `pm_snapshot.md`**
   - `pm.snapshot.md`: DMS-synced from repo (canonical)
   - `pm_snapshot.md`: JSON export converted to MD (generated)
   - **Action:** Consider consolidating or documenting the difference

#### Head Exports:
- Head exports are intentionally partial (first N lines)
- They are marked as "incomplete by construction" per `SHARE_FOLDER_STRUCTURE.md`
- **Purpose:** Quick reference without full context

## File Count Growth (21 → 42)

### Why the increase?

1. **More DMS-registered documents** with `share_path` set
2. **New JSON export pipeline** (`pm.share.artifacts`) generates:
   - DMS table dumps
   - Governance exports
   - PM snapshots
   - Planning context
3. **Automatic JSON-to-MD conversion** during housekeeping

### Is this expected?

**Yes.** The growth reflects:
- More comprehensive DMS integration
- Better observability (table dumps, governance tracking)
- PM tooling needs (planning context, snapshots)

## Embedding Files Exclusion

Large embedding files are **correctly excluded** from `share/`:

- `code_fragments_embedded.json` (91MB if converted to MD)
- `json_to_markdown.py` skips:
  - Files with "embedding" or "embedded" in name
  - Files larger than 1MB

**Rationale:** These files are too large for markdown conversion and not useful for PM consumption.

## Access & Indexing

The `share/` folder is now:

1. **Part of the codebase** (not just exports)
2. **DMS-managed** (single source of truth)
3. **AI-indexable** (all MD format, human-readable)
4. **Self-healing** (housekeeping syncs from DMS)

**For AI agents:**
- All files are Markdown (readable)
- Structure is flat (no subdirectories)
- Content is current (synced from DMS on housekeeping)
- Purpose is documented (this file + `SHARE_FOLDER_STRUCTURE.md`)

## Maintenance

### Adding Files to Share/

1. **Register in DMS:**
   ```sql
   UPDATE control.doc_registry 
   SET share_path = 'FILENAME.md' 
   WHERE logical_name = 'DOC_NAME';
   ```

2. **Run housekeeping:**
   ```bash
   make housekeeping
   ```

3. **File will be synced automatically**

### Removing Files from Share/

1. **Disable in DMS:**
   ```sql
   UPDATE control.doc_registry 
   SET share_path = NULL 
   WHERE logical_name = 'DOC_NAME';
   ```

2. **Or disable the document:**
   ```sql
   UPDATE control.doc_registry 
   SET enabled = FALSE 
   WHERE logical_name = 'DOC_NAME';
   ```

3. **Run housekeeping** (stale files will be removed)

## Related Documentation

- `docs/SSOT/SHARE_FOLDER_STRUCTURE.md` - Structure and usage rules
- `scripts/sync_share.py` - DMS sync implementation
- `scripts/util/json_to_markdown.py` - JSON conversion logic
- `Makefile` (target: `pm.share.artifacts`) - Export generation

