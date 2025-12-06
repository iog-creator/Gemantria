# Phase 22 — Operator Workflow

**Status:** COMPLETE  
**Date:** 2025-12-05

## Purpose

Document the end-to-end operator workflow for building, serving, and smoke-testing
Orchestrator Console v2.

---

## 1. Prerequisites

- Node.js 18+ installed
- Python virtual environment activated (`.venv`)
- Database running (Postgres)

---

## 2. Build Console v2

```bash
cd webui/orchestrator-console-v2
npm install
npm run build
```

Build artifacts go to `dist/`.

---

## 3. Serve Locally (Development)

```bash
cd webui/orchestrator-console-v2
npm run dev
```

Open `http://localhost:5173` in browser.

---

## 4. Smoke Test

```bash
# Just console check
python scripts/pm/check_console_v2.py --skip-build

# Full stress harness
make stress.smoke
```

---

## 5. Surfaces Consumed

Console v2 reads from `share/` only (never talks to DB directly):

| Surface | Path |
|---------|------|
| SSOT Surface | `share/SSOT_SURFACE_V17.json` |
| PM Bootstrap | `share/PM_BOOTSTRAP_STATE.json` |
| Phase Index | `share/PHASE23_INDEX.md` |
| Orchestrator State | `share/orchestrator/STATE.json` |
| Orchestrator Prompts | `share/orchestrator/ACTIVE_PROMPTS.md` |
| OA State | `share/orchestrator_assistant/STATE.json` |
| OA Prompts | `share/orchestrator_assistant/ACTIVE_PROMPTS.md` |
| KB Registry | `share/kb_registry.json` |
| Control-Plane Exports | `share/atlas/control_plane/` |
| Docs-Control Exports | `share/exports/docs-control/` |

---

## 6. Governance Files

| File | Purpose |
|------|---------|
| `share/orchestrator/CONSOLE_SCHEMA.json` | Region/mode/tile definitions |
| `share/orchestrator/VIEW_MODEL.json` | Data source bindings (version=2) |
| `docs/SSOT/PHASE22_HINTS_CONSOLE_V2.md` | DMS hint posture for console v2 |

---

## 7. Troubleshooting

| Issue | Fix |
|-------|-----|
| "Missing CONSOLE_SCHEMA.json" | Run `make stress.smoke` to verify; recreate if needed |
| "VIEW_MODEL.version != 2" | Update VIEW_MODEL.json version field |
| "Data source path does not exist" | Create missing file or remove from VIEW_MODEL |
