# AGENTS.md — webui/graph

## Purpose

This directory contains the legacy Graph Dashboard web UI and related assets.

In the Orchestrator Shell v1, the Graph experience is now primarily surfaced via:
- `webui/graph/src/pages/GraphDashboard.tsx` (embedded in the Shell)
- Static exports under `webui/graph/public/exports/` and `webui/graph/dist/exports/`

This AGENTS.md documents the current UI entrypoints for the graph tooling.

## UI Entry Points

- `src/App.tsx` — top-level SPA router for the legacy graph app
- `src/pages/GraphDashboard.tsx` — main graph dashboard page
- `src/lib/temporalExports.ts` — helpers for temporal + forecast exports
- `dist/` — built assets for the standalone graph app
- `public/exports/` — static JSON exports consumed by the Orchestrator Shell

## Agent Responsibilities

- Render the Graph Dashboard for:
  - graph insights
  - temporal and forecast visualizations (when embedded)

- Consume static JSON exports from:
  - `public/exports/graph_latest.json`
  - `public/exports/docs-control/*.json`
  - `public/exports/control-plane/*.json` (when present)

## Notes

- This directory is now primarily a provider of graph UI components and static exports.
- The Orchestrator Shell is the preferred entrypoint for orchestrator-facing workflows.
