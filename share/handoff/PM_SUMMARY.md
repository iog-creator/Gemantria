# PM Handoff Summary
Generated at: 2025-12-07T17:50:51.450265+00:00
Version: pmagent.handoff.kernel.v1

## Where we really are
- **Phase**: 24
- **Last Completed**: 23
- **Branch**: `feat/phase27i-doc-hygiene-batch1`

## What’s green / proven
- **Kernel Integrity**: Generated and consistent with bootstrap.
- **Guard Policy**: Enforced (`reality.green`, `stress.smoke`, `phase.done.check`).

## Known gotchas / sharp edges
- **Backup**: True (Destructive ops require fresh backup).
- Always verify `reality.green` before merging.

## Next actions for Cursor
- Run kernel check (make kernel.check)
- Verify guard status (make reality.green)
- Review Phase 24 objectives

## How to regenerate this kernel
```bash
pmagent handoff-kernel
```

## Ground Truth Surfaces
- `docs/SSOT/PHASE24_INDEX.md`
- `docs/SSOT/PHASE25_INDEX.md`
- `share/PHASE18_INDEX.md`
- `share/PHASE20_INDEX.md`
- `share/PHASE21_INDEX.md`
- `share/PHASE22_INDEX.md`
- `share/PHASE23_INDEX.md`
- `share/PM_BOOTSTRAP_STATE.json`
- `share/SSOT_SURFACE_V17.json`
- `share/orchestrator/STATE.json`
- `share/orchestrator_assistant/STATE.json`
