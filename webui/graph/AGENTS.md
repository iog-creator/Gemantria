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

## Status UI Integration (AgentPM-First:M3 + M4)

**WebUI Status Pages** (`src/services/api_server.py`):
- `/status` — System status page (DB + LM health, status explanation, **Documentation Health card (KB-Reg:M5)**)
- `/dashboard` — System dashboard (overview of health + LM insights)
- `/lm-insights` — LM indicator insights with charts (advisory analytics)
- `/db-insights` — DB health timeline with charts (advisory analytics)

**Documentation Health Card (KB-Reg:M5)**:
- Displays KB registry status (total docs, subsystem breakdown)
- Shows hints badge if WARN-level KB hints are present
- Lists key documents (SSOT, ADRs, root AGENTS.md) with links
- Populated from `/api/status/explain` endpoint's `documentation` field
- Advisory-only; does not affect system health indicators

**API Endpoints** (aligned with pm.snapshot SSOT):
- `/api/status/system` — System status (DB + LM health, AI tracking, share manifest, eval insights)
- `/api/status/explain` — Status explanation (plain-language summary)
- `/api/lm/indicator` — LM indicator snapshot (from Phase-4C exports, advisory only)
- `/api/db/health_timeline` — DB health timeline (from pm.snapshot exports, advisory only)
- `/api/eval/edges` — Edge class counts (from Phase-10 exports, advisory only)

**SSOT Contract:**
- All status APIs use `agentpm.status.snapshot.get_system_snapshot()` for consistency with `pm.snapshot`
- Eval export APIs use `agentpm.status.eval_exports` helpers (hermetic, tolerant of missing files)
- WebUI pages are thin views over these APIs (no independent logic)
- **Eval data is advisory only**: Core health posture comes from `/api/status/system`; eval charts are clearly labeled as "advisory analytics" and do not override health gates
- DB-off/LM-off modes degrade gracefully (hermetic behavior for CI/testing)
- See `agentpm/AGENTS.md` for pm.snapshot integration details

## Notes

- This directory is now primarily a provider of graph UI components and static exports.
- The Orchestrator Shell is the preferred entrypoint for orchestrator-facing workflows.
- Status UI pages consume pm.snapshot SSOT via unified snapshot helper (AgentPM-First:M3 + M4).
- Eval exports (Phase-8/10) are surfaced as advisory analytics; system health is determined by core health components, not eval metrics.
