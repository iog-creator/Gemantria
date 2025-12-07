# PHASE 24 — SSOT Alignment, Bootstrap Unpinning, Share Sync Reform, Backup Rotation

**Status:** PLANNING  
**Owner:** PM (Gemantria)  
**Depends on:** Phase 23 COMPLETE, Reconstruction Verified, Backup Policy Enforced  
**Surface Class:** Reliability / Governance / SSOT Integrity

---

## 24.0 Executive Summary

Phase 24 resolves structural liabilities identified in Phase 23’s Rule 070 analysis.  
These issues directly affect SSOT alignment, handoff correctness, share/ stability, and long-term system safety.

Phase 24 contains four required workstreams:

- **24.A — Bootstrap Unpinning**
- **24.B — DMS Alignment (Registry/Filesystem Reconciliation)**
- **24.C — Share Sync Policy Reform (Whitelist Removal)**
- **24.D — Backup Retention & Rotation**

Additionally, Phase 24 introduces the **Handoff Kernel**, a deterministic surface enabling consistent PM/OA/Cursor initialization.

---

## 24.A — Bootstrap Unpinning & Phase-Agnostic Generation

### Problem
`generate_pm_bootstrap_state.py` is pinned to Phase 23, creating stale or misleading bootstrap output.

### Objectives
1. Make bootstrap generation fully **phase-agnostic**:
   - Derive `current_phase` and `last_completed_phase` from DMS and SSOT surfaces.
2. Ensure the `"phases"` map reflects all discovered phases, not only docs in `/docs/SSOT`.
3. Fail hard (not warn) if:
   - DMS alignment is broken
   - PHASENN_INDEX.md is missing or unreadable
   - Bootstrap state does not match orchestrator phase

### Deliverables
- Updated `generate_pm_bootstrap_state.py`
- New guard: `guard_bootstrap_consistency.py`
- Updated bootstrap tests

---

## 24.B — DMS Alignment: Registry ↔ Filesystem Reconciliation

### Problem
Restored share/ content from Phase 18–23 is not guaranteed to match DMS state.  
`kb_registry.json` is a restored snapshot, not an authoritative export.

### Objectives
1. Implement automated ingestion:
   - `make governance.ingest.docs`
   - OR `pmagent dms ingest-share`
2. Create `guard_dms_share_alignment.py` verifying:
   - Every tracked doc exists in share/
   - Every share/ doc expected by DMS has a registry entry
   - No mismatches allowed in STRICT mode
3. Update SSOT_SURFACE to include:
   - `dms_share_alignment: OK | BROKEN`

### Deliverables
- Ingestion command
- Alignment guard
- Updated SSOT_SURFACE generator

---

## 24.C — Share Sync Policy Reform (Whitelist Removal)

### Problem
`sync_share.py` uses a hardcoded whitelist for Phase 18–23 docs; untracked docs may be deleted silently.

### Objectives
1. Replace static whitelist with a **DMS-driven allowlist**:
   - If a doc appears in DMS → KEEP  
   - If generated export → KEEP  
   - Otherwise:
     - STRICT: ERROR  
     - DEV: WARN
2. Add formal namespaces:
   - `share/orchestrator/`
   - `share/orchestrator_assistant/`
   - `share/atlas/...`
   - `share/exports/...`
3. Update sync behavior:
   - Never delete unregistered docs silently
   - Emit actionable error messages

### Deliverables
- Rewritten `sync_share.py`
- Guard: `guard_share_sync_policy.py`
- Updated AGENTS.md and hint/envelope entries

---

## 24.D — Backup Retention & Rotation

### Problem
`make backup.surfaces` accumulates unlimited timestamped backups.

### Objectives
1. Implement rotation rules:
   - Keep last **10** backups  
   - Keep **1 per day for 7 days**  
   - Remove others safely
2. Add:
   - `make backup.rotate`
   - Integration with housekeeping + backup guard
3. Add guard for:
   - Disk threshold warnings
   - Corrupted backups

### Deliverables
- Rotation tool
- Updated housekeeping pipeline
- Retention policy documentation

---

## 24.E — Handoff Kernel Integration

### Purpose
Enable deterministic PM/OA/Cursor startup.

### Objectives
1. Create `share/HANDOFF_KERNEL.json` containing:
   - `current_phase`
   - `last_completed_phase`
   - `required_surfaces`
   - `health` (reality.green, stress.smoke)
   - `notes` (mismatches, alignment state)
2. Implement:
   - `pmagent handoff kernel`
   - Guard: `guard_handoff_kernel.py`

### Deliverables
- Kernel generator
- Kernel guard
- Integration in bootstrap pipeline

---

## 24.F — Phase-DONE Checklist Additions

To close Phase 24, all must be true:

- Bootstrap unpinned and verified
- DMS-share alignment: OK
- Share sync policy updated (no static whitelist)
- Backup rotation enforced
- Handoff Kernel valid and passing guard
- reality.green: GREEN or formally justified
- stress.smoke: PASS
- All new surfaces registered in DMS
- Hints + envelopes updated
- All guards report OK in STRICT mode

---

## 24.G — Acceptance Criteria

Phase 24 is complete when:

1. System can rebuild from scratch → bootstrap → kernel → console with no drift.  
2. All guards pass in STRICT mode.  
3. No static whitelist remains.  
4. Backups rotate and pass validation.  
5. DMS is authoritative, share/ is aligned, kernel is deterministic.
