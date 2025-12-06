# Phase 23.1 — Stress Smoke Integration

**Status:** COMPLETE  
**Date:** 2025-12-05

## Purpose

Create an integrated stress harness that exercises console v2, reality.green, and pmagent
in a single `make stress.smoke` target.

## Target Behavior

```bash
make stress.smoke
```

Runs:
1. `python scripts/pm/check_console_v2.py --skip-build` — validates console schema
2. `make reality.green STRICT=1` — system truth gate
3. Basic pmagent commands (if available)

## Exit Codes

- **Exit 0:** All checks pass
- **Exit 1:** Console v2 check failed
- **Exit 2 (ignored):** Reality.green has issues (non-blocking for stress epoch)

## Evidence

- `evidence/stress/smoke/stress_smoke.log` — full run output
- `evidence/stress/smoke/console_check.log` — console v2 validation
