# Phase 23.0b — Bootstrap Generator Hardening

**Status:** COMPLETE  
**Date:** 2025-12-05

## Purpose

Ensure PM Bootstrap State can be safely regenerated without losing console v2 registration.

## Problem Solved

When `generate_pm_bootstrap_state.py` runs, it overwrites `PM_BOOTSTRAP_STATE.json`.
If the `webui.console_v2` section was manually added, it would be lost.

## Solution Implemented

Created `scripts/pm/patch_pm_bootstrap_webui.py` that:
1. Backs up existing `webui.console_v2` section if present
2. Runs `generate_pm_bootstrap_state.py` to regenerate state
3. Restores the `webui.console_v2` section

## Safe Command

```bash
make pm.bootstrap.state
```

This target:
- Runs the patch script
- Preserves console v2 registration
- Outputs status: `PRESERVED`, `ADDED`, or `SKIPPED`

## Evidence

- `evidence/stress/bootstrap/webui_console_v2_snippet.json` — preserved section
- `evidence/stress/bootstrap/pm_bootstrap_regenerated.log` — regeneration output
