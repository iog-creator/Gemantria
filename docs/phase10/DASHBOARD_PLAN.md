# Phase-10 — Dashboard Plan (Docs-only; Hermetic)

## Goals

- Visualize local ingestion envelopes (Phase-9) without network/DB.
- Views: (1) Graph overview (nodes/edges) (2) Temporal heat strip (uses created_at) (3) Metrics summary (counts/density).

## Data

- Input: /tmp/p9-ingest-envelope.json (built locally via `make ingest.local.envelope`).
- No data committed; local-only workflow.

## Tech (proposal)

- React + Vite (local dev only; not wired to CI).
- Graph: React Flow or D3/Visx; tiny JSON loader.
- No external analytics; deterministic sample drives.

## PR-by-PR slices

- P10-A: scaffold docs + file layout for a `ui/` folder (no build yet).
- P10-B: JSON loader + minimal graph view reading envelope nodes/edges.
- P10-C: temporal strip proto (uses meta.created_at; dummy).
- P10-D: metrics panel (nodes/edges/density).

## Acceptance for P10-A

- `docs/phase10/STRUCTURE.md` describing `ui/` layout and dev run.
- No CI changes; no npm in CI; hermetic preserved.
