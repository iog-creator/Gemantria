# Phase 20 — Orchestrator UI Model

## Three-Region Layout

### 1. Conversation Pane (Center)
- Primary chat interface
- Phase context display
- Active prompts from orchestrator/OA

### 2. Right Status Pane
**Tiles:**
- System Status (DB, LM health)
- Phase Governance (current phase, progress)
- Docs Registry (KB status)
- Orchestrator/OA Status

### 3. Left Nav Pane
**Modes:**
- Overview
- Docs
- Temporal
- Forecast
- Graph

## Data Sources

All data comes from `share/`:
- `SSOT_SURFACE_V17.json`
- `PM_BOOTSTRAP_STATE.json`
- `orchestrator/STATE.json`
- `orchestrator_assistant/STATE.json`
- `atlas/control_plane/*.json`
- `exports/docs-control/*.json`

## Schema Files

- `share/orchestrator/CONSOLE_SCHEMA.json` — Layout definition
- `share/orchestrator/VIEW_MODEL.json` — Data source bindings
