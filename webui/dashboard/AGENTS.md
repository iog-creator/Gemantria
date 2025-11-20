# AGENTS.md — webui/dashboard

## Purpose

This directory contains the main dashboard UI for the Orchestrator Shell, including:
- Doc Control Panel
- Temporal Explorer
- Forecast Dashboard
- Shared utilities for static export-driven views

It is the primary home for orchestrator-facing dashboards that are embedded into the Shell.

## UI Entry Points

- `ForecastDashboard.tsx` — forecast view backed by temporal exports
- `src/components/TemporalExplorer.tsx` — temporal explorer component
- `src/components/DocControlPanel.tsx` — Doc Control Panel implementation
- `src/utils/docsControlData.ts` — data access helpers for docs-control exports
- `src/utils/modelsData.ts` — data access helpers for LM-related exports
- `src/utils/dbData.ts` — data access helpers for DB/system health exports

## Integration with Orchestrator Shell

These components are embedded via:
- `webui/orchestrator-shell/MainCanvas.tsx`
- `webui/orchestrator-shell/LeftRail.tsx`

Tools exposed in the Shell that depend on this directory:

- **Docs** — Doc Control Panel
- **Temporal** — Temporal Explorer
- **Forecast** — Forecast Dashboard
- **Models** — Models panel (LM indicator + metrics, via modelsData)
- **DB** — DB panel (via dbData/system health exports)

## Data Contracts

All panels are hermetic and consume static JSON exports only, including:
- `webui/graph/public/exports/docs-control/*.json`
- `webui/graph/public/exports/control-plane/system_health.json`
- `webui/graph/public/exports/control-plane/lm_indicator.json`

No direct DB/LM calls are made from this directory.

