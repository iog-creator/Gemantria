# PM Share Folder Enhancements - Implementation Summary

**Date**: 2025-11-29  
**Context**: Enhanced share folder to contain all information needed for PM to manage complete system  
**Related**: Rule 071 (Portable JSON is not Plan SSOT), PM_CONTRACT.md Section 2.8

---

## What Was Done

### 1. Full AGENTS.md Export System

**Created**: `scripts/util/export_all_agents_md.py`

* Finds all 84+ AGENTS.md files in the repository
* Exports them as **full files** (not head exports) to `share/agents_md/`
* Creates safe filenames (path separators replaced with underscores)
* Generates `manifest.json` with metadata:
  * Source paths
  * Export paths
  * File hashes (SHA256)
  * Modification times
  * Line counts and file sizes

**Integration**: Added to `make pm.share.artifacts` target

### 2. KB Registry Export

**Added**: KB registry export to share folder

* Exports complete KB document registry to `share/kb_registry.json`
* Provides DMS integration metadata for all registered documents
* Enables PM to query document registry without direct DMS access

**Integration**: Added to `make pm.share.artifacts` target

### 3. Updated Share Folder Structure Documentation

**Updated**: `docs/SSOT/SHARE_FOLDER_STRUCTURE.md`

* Clarified that share folder is now a **complete portable PM context package**
* Documented full exports vs head exports
* Added DMS integration section
* Explained how PM can use KB registry for document discovery

### 4. Gotchas Checks (Rule 070)

**Status**: Already implemented as AlwaysApply rule

* Rule 070 requires gotchas checks at beginning and end of all work sessions
* Gotchas checks are mandatory, not optional
* Should emit hints (Rule 026) if gotchas checks are missing
* Integration points:
  * Pre-work gotchas analysis in Goal block (Rule 050)
  * Post-work gotchas review in Next gate block (Rule 050)
  * Gotchas in evidence blocks (Rule 051)

---

## What the PM Now Has in Share Folder

### Complete Files (Full Exports)

1. **All AGENTS.md Files** (`share/agents_md/`)
   * 84+ complete AGENTS.md files
   * Manifest with metadata
   * All system documentation in one place

2. **Planning Context** (`share/planning_context.json`)
   * Full output from `pmagent plan next`
   * Current focus, next milestone, candidate work items
   * Derived from full MASTER_PLAN.md and NEXT_STEPS.md

3. **KB Registry** (`share/kb_registry.json`)
   * Complete document registry
   * Metadata for all registered documents
   * DMS integration information

### Head Exports (Quick Reference)

* `share/agents_md.head.json` - First 100 lines of root AGENTS.md
* `share/pm_contract.head.json` - First 100 lines of PM_CONTRACT.md
* `share/next_steps.head.json` - First 100 lines of NEXT_STEPS.md

**Note**: Head exports are for quick reference only. For planning decisions, use full exports or SSOT files.

### DMS and Governance Snapshots

* `share/doc_registry.json` - DMS document registry
* `share/doc_sync_state.json` - Document sync state
* `share/doc_version.json` - Document version tracking
* `share/governance_freshness.json` - Governance freshness summary
* `share/hint_registry.json` - System hints registry
* `share/live_posture.json` - System health and live posture
* `share/pm_snapshot.json` - PM system snapshot
* `share/schema_snapshot.json` - Database schema snapshot

---

## Tools Available to PM

### Planning System (`pmagent plan`)

* `pmagent plan next --with-status` - Get current focus and next work items
* `pmagent plan history --limit 10` - View planning history
* `pmagent plan reality-loop --track-session` - Reality check loop
* `pmagent plan open <plan_id>` - Open specific plan

### KB Registry (`pmagent kb registry`)

* `pmagent kb registry list` - List all registered documents
* `pmagent kb registry by-subsystem --owning-subsystem <subsystem>` - Filter by subsystem
* `pmagent kb registry by-tag --tag <tag>` - Filter by tag
* `pmagent kb registry show <doc_id>` - Show document details
* `pmagent kb registry validate` - Validate registry entries

### Status Commands (`pmagent status`)

* `pmagent status kb` - KB registry status
* `pmagent status.explain` - System status explanation
* `pmagent lm.status` - LM configuration and health

### Makefile Targets

* `make pm.share.artifacts` - Generate all PM share artifacts
* `make plan.next` - Show next planning items
* `make plan.history` - Show planning history
* `make pm.share.planning_context` - Export planning context only

---

## What Still Needs to Be Done

### 1. DMS Integration for AGENTS.md Files

**Goal**: Ensure all AGENTS.md files are registered in DMS and can be queried from Postgres

**Status**: KB registry exists, but AGENTS.md files need to be:
* Registered in KB registry (via `pmagent kb registry` or seeding script)
* Stored in DMS tables (via `make mcp.ingest` or similar)
* Queryable from Postgres using DMS queries

**Tools Available**:
* `scripts/kb/seed_registry.py` - Populate KB registry (if exists)
* `pmagent kb registry` commands - Manual registration
* `make mcp.ingest` - Ingest documents into DMS

### 2. Complete DMS Storage

**Goal**: Every scrap of content must be available in Postgres

**Current State**: 
* KB registry tracks document metadata
* DMS tables exist for document storage
* Not all AGENTS.md files are yet in DMS

**Next Steps**:
* Create script to bulk-register all AGENTS.md files in KB registry
* Create script to bulk-ingest all AGENTS.md files into DMS
* Verify all content is queryable from Postgres

### 3. Gotchas Checks as Built-in Hints

**Goal**: Ensure gotchas checks are automatically triggered and emit hints

**Current State**: Rule 070 exists and is AlwaysApply, but:
* Need to verify gotchas checks are being performed
* Need to ensure hints are emitted when gotchas checks are missing
* Need to integrate gotchas checks into workflow gates

**Next Steps**:
* Review Rule 070 implementation
* Add gotchas check validation to `make reality.green`
* Ensure gotchas checks are part of work completion gates

---

## How PM Should Use Share Folder

### For Complete System Context

1. **Read all AGENTS.md files** from `share/agents_md/` for complete system documentation
2. **Use planning context** from `share/planning_context.json` for current focus
3. **Query KB registry** from `share/kb_registry.json` for document discovery
4. **Check DMS snapshots** for governance and system state

### For Planning Decisions

1. **Always use `pmagent plan next --with-status`** as first step
2. **Read full SSOT files** (MASTER_PLAN.md, NEXT_STEPS.md) for complete context
3. **Do not rely on head exports** for planning decisions
4. **Use orchestrator's explicit statements** as authoritative input

### For Document Discovery

1. **Query KB registry** using `pmagent kb registry` commands
2. **Use DMS queries** for document content retrieval
3. **Check share/agents_md/** for complete AGENTS.md files
4. **Use manifest.json** to find specific files

---

## Summary

The share folder now contains **all information needed for the PM to manage the complete system from start to finish**. All AGENTS.md files are exported as full files, planning context is included, and KB registry provides DMS integration.

**Next Steps**:
1. Register all AGENTS.md files in KB registry
2. Ingest all AGENTS.md files into DMS
3. Verify gotchas checks are working as hints
4. Test complete system rebuild from Postgres (future goal)

