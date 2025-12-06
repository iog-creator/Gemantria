# SHARE_SURFACE_CONTRACT — v1

**Date:** 2025-12-04  
**Status:** Canonical  
**Governance:** Rule 051, Rule 052, Rule 053

---

## Purpose

The `share/` directory is the **cross-agent evidence surface** for:
- **Orchestrator** (human operator)
- **PM** (Project Manager AI agent)
- **OA** (Orchestrator Assistant AI agent)
- **External tools / UIs** (webui, dashboards, monitoring)

It must stay **small, curated, and predictable**.

---

## What Belongs in `share/`

### 1. Phase-Level Summary Artifacts

**Machine-readable summaries:**
- `share/PHASEXX_*_SUMMARY.json` — Status, results, evidence pointers

**Human-facing indexes (optional):**
- `share/PHASEXX_INDEX.md` — Narrative summary for PM/OA

**Example (Phase 18):**
- `share/PHASE18_AGENTS_SYNC_SUMMARY.json`
- `share/PHASE18_SHARE_EXPORTS_SUMMARY.json`
- `share/PHASE18_INDEX.md`

### 2. Global Surfaces

**Bootstrap and state:**
- `share/PM_BOOTSTRAP_STATE.json` — PM initialization state
- `share/SSOT_SURFACE_VXX.json` — SSOT snapshot baseline

**Registry snapshots:**
- `share/kb_registry.json` — Knowledge base registry

### 3. Canonical Exports for Other Systems

**Atlas control-plane health:**
- `share/atlas/control_plane/system_health.json`
- `share/atlas/control_plane/lm_indicator.json`

**Docs-control dashboard:**
- `share/exports/docs-control/*.json` (summary, canonical, archive-candidates, unreviewed-batch, orphans, archive-dryrun)

### 4. AGENTS and Documentation Surfaces

**For PM/OA discovery:**
- `share/AGENTS.md` — Root AGENTS documentation
- `share/scripts_AGENTS.md` — Scripts subsystem AGENTS
- Other key SSOT/runbook docs as required by PM bootstrap

---

## What Does NOT Belong in `share/`

The following belong elsewhere:

### Evidence Directory (`evidence/`)
- Raw logs (`*.log`, `*.txt`, `*.trace`, `*.ndjson`)
- Guard output files (`evidence/guard_*.json`)
- Per-command diagnostics
- `ls` outputs, command traces
- Reality check logs

**Rationale:** These are referenced via `evidence_paths` in phase summaries, not duplicated in share.

### Archive Directory (`archive/`)
- Historical artifacts no longer actively used
- Legacy phase outputs
- Old evidence snapshots

### Temporary/Working Directories
- `logs/` — Runtime logs
- `exports/` (non-share exports) — Working exports not meant for cross-agent consumption

---

## Evidence Pattern

Each phase summary in `share/`:
- Contains **compact status fields** (`phase`, `topic`, `status`, `missing_*` arrays)
- Includes `evidence_paths` array pointing into `evidence/reality/...`

**Example Structure:**
```json
{
  "phase": "18.2",
  "topic": "share_exports",
  "status": "COMPLETE",
  "required_atlas_exports": [...],
  "atlas_exports_present": {...},
  "missing_exports": [],
  "evidence_paths": [
    "evidence/reality/phase18.2_share_sync.make.log",
    "evidence/reality/phase18.2_share_atlas_final_ls.txt"
  ]
}
```

**PM/OA workflow:**
1. Read the summary in `share/`
2. Check status fields and high-level results
3. Follow `evidence_paths` **only if** deeper debugging is needed

**No spelunking required.**

---

## Naming Convention (Going Forward)

### For Each New Phase `NN`

**Required:**
- At least one JSON surface: `share/PHASENN_<topic>_SUMMARY.json`

**Optional:**
- Human index: `share/PHASENN_INDEX.md`

**JSON Schema (minimum):**
```jsonc
{
  "phase": "NN.x",
  "topic": "short_topic",
  "status": "COMPLETE|BLOCKED|PARTIAL",
  "missing_*": [],              // Arrays of missing items (if any)
  "evidence_paths": [...]       // Relative paths into evidence/
}
```

### Multi-Part Phases

For phases with sub-parts (e.g., 18.1, 18.2):
- Create separate JSON for each sub-phase
- Create single `PHASENN_INDEX.md` covering all sub-phases

---

## PM Bootstrap Integration

`share/PM_BOOTSTRAP_STATE.json` must reference major phase indexes in `surfaces` or `meta`:

```json
{
  "surfaces": {
    "ssot_surface": "share/SSOT_SURFACE_V17.json",
    "phase18_index": "share/PHASE18_INDEX.md"
  },
  "meta": {
    "current_phase": 18,
    "last_completed_phase": 17
  }
}
```

This ensures new PM instances can immediately find phase narratives.

---

## Share Hygiene (Periodic Cleanup)

**Trigger:** When `share/` grows beyond ~50 files or becomes cluttered

**Process:**
1. List all files in `share/`
2. Classify each as:
   - **Contract-approved surface** (keep)
   - **Obsolete** (delete or move to archive)
   - **Evidence** (migrate to `evidence/` or `archive/`)
3. Generate cleanup plan: `docs/SSOT/PHASENN_SHARE_CLEANUP_PLAN.md`
4. Apply moves and update bootstrap references

**Last cleanup:** Phase 16 (legacy purge)  
**Next planned:** Phase 19 (share/ hygiene pass)

---

## Related Documentation

- **PM Contract:** `docs/SSOT/PM_CONTRACT.md`
- **PM Bootstrap Protocol:** `docs/SSOT/PM_HANDOFF_PROTOCOL.md`
- **Evidence Guard:** `scripts/guards/guard_reality_green.py`
- **Share Sync:** `scripts/sync_share.py`

---

## Enforcement

**Guards:**
- `make reality.green` — Checks share/ exports presence
- `make share.sync` — Regenerates canonical share/ surfaces

**Rule References:**
- **Rule 051:** PM DMS-First Workflow
- **Rule 052:** Tool Registry Query Priority
- **Rule 053:** Control MCP Tool Catalog
- **Rule 070:** Gotchas Check (pre/post work)

---

## Version History

- **v1 (2025-12-04):** Initial contract definition (Phase 18.3)
