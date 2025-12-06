# Phase 23 — Stress & Reliability Epoch Plan

**Status:** IN PROGRESS  
**Goal:** Stress-test the Orchestrator Console v2 and governance subsystems to ensure
they fail loudly, recover cleanly, and provide clear signals to PM/OPS.

---

## Systems Under Test

1. **Orchestrator Console v2** — `webui/orchestrator-console-v2/`
2. **PM Bootstrap State** — `share/PM_BOOTSTRAP_STATE.json`
3. **SSOT Surface** — `share/SSOT_SURFACE_V17.json`
4. **Reality Green** — `make reality.green`
5. **Share Sync** — `scripts/sync_share.py`

---

## Phase 23 Subphases

| Subphase | Description | Status |
|----------|-------------|--------|
| 23.0a | Baseline Checkpoint | ✅ COMPLETE |
| 23.0b | Bootstrap Generator Hardening | ✅ COMPLETE |
| 23.1 | Stress Smoke Integration | ✅ COMPLETE |
| 23.2 | Failure Injection | ✅ COMPLETE |
| 23.3 | Phase-DONE Checklist Guard | ✅ COMPLETE |

---

## Key Targets

- `make stress.smoke` — integrated stress harness
- `make pm.bootstrap.state` — safe bootstrap regeneration
- `make phase.done.check` — Phase-DONE artifact verification
- `make reality.green` — system truth gate

---

## Evidence Locations

- `evidence/stress/baseline/` — baseline checkpoint artifacts
- `evidence/stress/smoke/` — stress smoke run logs
- `evidence/stress/failure_injection/` — failure scenario evidence
- `evidence/stress/phase_done_*.log` — Phase-DONE guard output

---

## Auto-Fix vs PM Escalation

| Condition | Action |
|-----------|--------|
| Missing file in expected path | Auto-fix if template exists |
| AGENTS.md sync drift | Auto-fix via `make housekeeping` |
| Console schema version mismatch | PM escalation |
| SSOT surface missing/corrupt | PM escalation |
| Bootstrap state corrupt | Auto-fix via `make pm.bootstrap.state` |
