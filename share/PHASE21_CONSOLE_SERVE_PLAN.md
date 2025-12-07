# Phase 21 — Console Serve Plan

**Status:** COMPLETE  
**Date:** 2025-12-05

## Purpose

Establish the local development and serving workflow for Orchestrator Console v2.

## Dev Server

```bash
# Start dev server
cd webui/orchestrator-console-v2
npm run dev
```

Default URL: `http://localhost:5173`

## Make Target

```bash
make console.v2.serve
```

## CI Check

```bash
python scripts/pm/check_console_v2.py --skip-build
```

This validates:
1. `share/orchestrator/CONSOLE_SCHEMA.json` exists and is valid JSON
2. `share/orchestrator/VIEW_MODEL.json` exists with version=2
3. All `data_sources` paths in VIEW_MODEL exist under `share/`

## Build (Production)

```bash
cd webui/orchestrator-console-v2
npm run build
```

Output: `webui/orchestrator-console-v2/dist/`

## Key Files

- `webui/orchestrator-console-v2/package.json` — npm config
- `webui/orchestrator-console-v2/vite.config.ts` — Vite bundler config
- `scripts/pm/check_console_v2.py` — CI validation script
- `scripts/dev/serve_console_v2.py` — Dev server wrapper (if applicable)
