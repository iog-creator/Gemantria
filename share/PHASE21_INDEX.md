# Phase 21 — Console v2 Serving & CI Index

## Status
COMPLETE

## Overview
Phase 21 established the dev/prod serving strategy and CI checks for Orchestrator Console v2.

## Deliverables

### 21.0 Console Serve Plan
- Documented dev/prod serving strategy
- See `share/PHASE21_CONSOLE_SERVE_PLAN.md`

### 21.1 Dev Server
- Implemented `scripts/dev/serve_console_v2.py`
- Serves `/console-v2/` and `/share/` on port 8080

### 21.2 CI Check
- Implemented `scripts/pm/check_console_v2.py`
- Validates VIEW_MODEL paths under share/
- Runs `npm run build` as smoke test
