# SHARE Folder Structure & Limitations

## Purpose

The `share/` directory is a **complete portable PM context package** that contains
all information needed for the PM to manage the system from start to finish. It
is **auto-generated** during `make housekeeping` via the `pm.share.artifacts` target.

**Current State (2025-11-30):**
* **All files are Markdown format** (`.md`) - JSON files are automatically converted to Markdown
* **Flat directory structure** - no subdirectories
* **35 total files** - 14 core PM artifacts + 21 documentation files
* **Auto-generated** - no manual file management required

## Core PM Artifacts (14 files)

These are the essential governance/PM artifacts, all in Markdown format:

* `pm_snapshot.md` - System health snapshot
* `planning_context.md` - Full planning output from `pmagent plan next`
* `kb_registry.md` - KB document registry (for DMS integration)
* `doc_registry.md` - DMS document registry snapshot
* `doc_sync_state.md` - Document sync state
* `doc_version.md` - Document version tracking
* `governance_freshness.md` - Document freshness tracking
* `hint_registry.md` - System hints and warnings
* `live_posture.md` - System health posture
* `schema_snapshot.md` - Database schema snapshot
* `planning_lane_status.md` - Planning lane status
* `agents_md.head.md` - AGENTS.md head export (first 100 lines)
* `pm_contract.head.md` - PM contract head export (first 100 lines)
* `next_steps.head.md` - Next steps head export (first 100 lines)

## Head Exports (`*.head.md`)

Some files in `share/` are generated as **head exports** via
`scripts/util/export_head_json.py` and then converted to Markdown. These files
contain only the **first 100 lines** of their source documents. Examples:

* `next_steps.head.md` ← first 100 lines of `NEXT_STEPS.md` (converted from JSON)
* `pm_contract.head.md` ← first 100 lines of `PM_CONTRACT.md` (converted from JSON)
* `agents_md.head.md` ← first 100 lines of `AGENTS.md` (converted from JSON)

These head exports are:

* Incomplete by construction (they do not include the full document)
* Potentially stale (they are updated only when housekeeping runs)

They **must not** be used to infer:

* The currently active Phase/PLAN
* The true "Next Gate / Next Steps" section
* The current focus of the project

## Planning vs Status

* **Allowed from share/**:

  * Governance/status checks
  * DMS/hint registry posture
  * Control-plane export inspection
  * PM posture snapshots

* **Not allowed from share/**:

  * Choosing the active Phase/PLAN
  * Deciding "what to work on next" for development

## Full Exports (Complete Files)

The following are **full exports** (complete files, not head exports), all in Markdown format:

* `share/planning_context.md` - Full planning output from `pmagent plan next` (converted from JSON)
* `share/kb_registry.md` - Complete KB document registry (converted from JSON)
* `share/pm_snapshot.md` - Complete system snapshot (converted from JSON)
* `share/doc_registry.md` - Complete DMS document registry (converted from JSON)
* All other core PM artifacts are full exports (not head exports)

These full exports provide complete context for PM decision-making.

## JSON to Markdown Conversion

**All JSON files are automatically converted to Markdown** during `make housekeeping`:

1. JSON files are exported to `share/` as normal
2. `scripts/util/json_to_markdown.py` converts each JSON file to Markdown
3. Original JSON files are removed (only `.md` files remain)
4. This ensures all files in `share/` are human-readable Markdown format

The conversion preserves all data structure and content, making it easier for PM agents to read and understand the system state.

## DMS Integration

All AGENTS.md files and other critical documents are tracked in:
* **KB Registry** (`share/kb_registry.md`) - Document metadata and registry (converted from JSON)
* **DMS Tables** (`share/doc_registry.md`, etc.) - Full DMS table dumps (converted from JSON)

The PM can query DMS using:
* `pmagent kb registry list` - List all registered documents
* `pmagent kb registry by-subsystem --owning-subsystem <subsystem>` - Filter by subsystem
* `pmagent kb registry show <doc_id>` - Show document details

For planning decisions, see:

* `PM_CONTRACT.md` Sections 2.7 and 2.8
* `PM_CONTRACT_STRICT_SSOT_DMS.md` "Planning Context vs Portable Snapshots"
* The `pmagent plan` commands (`pmagent plan next --with-status`, etc.)

## SHARE_MANIFEST.json Deprecation

**Status**: `SHARE_MANIFEST.json` is **deprecated** and no longer reflects the current `share/` structure.

**Reason**: The `share/` directory is now **auto-generated** via `make pm.share.artifacts` during housekeeping. The manifest was designed for manual file synchronization, which is no longer needed.

**Current State**:
* `share/` contains 35 Markdown files (14 core PM artifacts + 21 documentation files)
* All files are auto-generated during `make housekeeping`
* DMS is the SSOT for document tracking
* No manual file management required

**Action**: The manifest is kept for historical reference but should not be used for validation or synchronization. The `share.manifest.verify` Makefile target may produce warnings about missing files - these can be ignored as the manifest is outdated.

