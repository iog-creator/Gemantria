# SHARE Folder Analysis — Canonical SSOT

> SSOT description of the layout, generation rules, and semantics of `share/`

## 1. Purpose

The `share/` folder is the **materialized view** of all operator-facing surfaces produced by:

- DMS registry  
- Phase machinery  
- pmagent scripts  
- reality.green  
- bootstrap generation  
- handoff kernel system  

Its purpose is to provide a **single place** where human- and agent-readable surfaces exist.

`share/` is **not** the Source of Truth.  
The Source of Truth is the **DMS + SSOT docs**.  
`share/` is a **generated and synchronized surface**.

---

## 2. High-Level Layout

```
share/
  PM_BOOTSTRAP_STATE.json
  HANDOFF_KERNEL.json
  REALITY_GREEN_SUMMARY.json
  SSOT_SURFACE_V17.json
  PHASENN_* (Phase surfaces 18–24)
  pm_boot/  — PM/OA boot capsule (kernel + bootstrap + contracts + logs)
  orchestrator/
  orchestrator_assistant/
  atlas/
  exports/
```

### **Generated Surfaces**

- `PM_BOOTSTRAP_STATE.json` (phase summary, metadata)
- `HANDOFF_KERNEL.json` (seed for new PM/OA)
- `REALITY_GREEN_SUMMARY.json` (guard evaluations)
- `SSOT_SURFACE_V17.json` (registry + alignment metadata)
- All *phase summary docs* (PHASE18–PHASE24)

### **Stateful Subdirs**

- `share/orchestrator/`  
- `share/orchestrator_assistant/`  

These are not DMS-managed but represent “working surfaces” for live agents.

### **Atlas + Exports**

- `share/atlas/` — control plane snapshot exports  
- `share/exports/` — governance and document exports

---

## 3. Relationship to DMS (The Actual SSOT)

DMS controls:

- Which documents exist  
- Metadata for documents  
- Canonical `share_path` for all managed surfaces  
- Hints, envelopes, registry state

Thus:

### **Rule:**  
**If DMS and share disagree → DMS is correct.**

Phase 24 introduced:

- `guard_dms_share_alignment.py`
- DMS-driven share sync policy
- SSOT_SURFACE generator including alignment metadata

These enforce:

- Every managed doc in DMS must exist in share/  
- No extra or unknown managed docs may appear in share/  
- share/ regenerates safely from DMS without risk of deletion

---

## 4. Relationship to the Handoff Kernel

The kernel uses `share/` as its input namespace.  
Specifically, it requires:

- `share/PM_BOOTSTRAP_STATE.json`
- `share/SSOT_SURFACE_V17.json`
- `share/REALITY_GREEN_SUMMARY.json`

And it emits:

- `share/HANDOFF_KERNEL.json`

The kernel is valid *iff*:

- Share is aligned  
- Bootstrap is consistent  
- All required surfaces exist  
- All guards pass in STRICT mode  

Thus:

### **Rule:**  
**A new PM chat must treat share/ as the authoritative materialized state of the system**,  
derived from DMS and validated by guards.

* The Handoff Kernel (`share/handoff/PM_KERNEL.json` + `share/handoff/PM_SUMMARY.md`) is the **only** supported entrypoint for new PM/OA/OPS sessions. This is enforced by DMS hints:
  * `pm.boot.kernel_first`
  * `oa.boot.kernel_first`
  * `ops.preflight.kernel_health`.

Phase 27.H introduces `share/pm_boot/` as the PM/OA boot capsule. It contains copies of kernel, bootstrap, REALITY_GREEN_SUMMARY, phase indexes, and core governance contracts. The pm_boot capsule is validated by `guard.pm_boot.surface` and checked via `make ops.kernel.check`.

---

## 5. Generation vs Manual Edits

| Surface | Generated? | Notes |
|--------|-----------|-------|
| PM_BOOTSTRAP_STATE.json | Yes | From pmagent script |
| HANDOFF_KERNEL.json | Yes | From generator |
| SSOT_SURFACE_V17.json | Yes | From generator |
| REALITY_GREEN_SUMMARY.json | Yes | Written by reality.green |
| PHASENN docs | Yes | From DMS + scripts |
| orchestrator/, OA/ | Partially | State folders (not governed by DMS) |

Manual edits should **never** occur in share/ (except orchestrator/OA state dirs).

Everything else must be generated or synchronized from DMS or scripts.

---

## 6. Safety Guarantees

Phase 24 introduced three guarantees:

1. **Backup Guard:** destructive operations blocked unless recent backup exists  
2. **Share Sync Policy Guard:** no unknown files in managed namespaces  
3. **DMS Alignment Guard:** share/ must match registry

These guarantees make `share/` safe to use as the agent-facing FS view.

This document is SSOT and must remain consistent with guard behavior.

---

## 5. Root Surface Policy (Phase 27.G)

The repository root is **code + top-level config only**. All temporary artifacts, logs, and generated files belong in designated directories:

### **Allowed in Root:**
- Source code files (`.py`, `.ts`, `.tsx`, etc.)
- Configuration files (`.toml`, `.ini`, `.json`, `.yaml`, `.yml`)
- Documentation files (`.md`, `.txt`)
- Build system files (`Makefile`, `package.json`, `pyproject.toml`)
- Git metadata (`.gitignore`, `.github/`, `.githooks/`)
- Environment files (`.env.example`, `.env.local` - git-ignored)

### **Not Allowed in Root:**
- Log files (`reality_green_*.log` → `var/log/pm/`)
- PR summaries (`pr_summary.md` → `share/handoff/pr/PR-{N}.md`)
- Test files (`test_*.py`, `conftest.py` → `tests/` or `tests/integration/`)
- Temporary artifacts (→ `evidence/`, `share/exports/`, or `var/`)

### **Enforcement:**
- **Allowlist**: `docs/SSOT/ROOT_SURFACE_ALLOWLIST.txt` (canonical list of allowed root files)
- **Guard**: `scripts/guards/guard_root_surface_policy.py` validates root against allowlist
- **Integration**: `make guard.root.surface` (standalone) + `make reality.green` (included)
- **Mode**: STRICT (fails on violations) or HINT (warns only)

### **Git Ignore:**
- `var/log/pm/` is git-ignored (ephemeral logs)
- `.env.local`, `.server.pid` are git-ignored (local-only files)

This policy prevents root drift and ensures repository hygiene is automatically enforced.
