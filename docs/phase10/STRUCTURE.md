# Phase-10 UI Structure (Plan)

**Hermetic Policy:** No Node/npm in CI. Local dev only. All UI work lives under `ui/`.

## Proposed Layout

* `ui/public/` static assets
* `ui/src/app/` app entry & routes
* `ui/src/components/` reusable views (graph, metrics, temporal)
* `ui/src/lib/` helpers (envelope loader)
* `ui/src/types/` TypeScript models (Envelope types)

## Local Dev Steps (operator)

1. Build envelope locally: `make ingest.local.envelope`
2. Bootstrap Vite in `ui/` (see `ui/README_UI.md`)
3. Load `/tmp/p9-ingest-envelope.json` for views

## CI Stance

* No Node jobs added.
* A `ui.dev.help` Make target will print local instructions and HINT in CI.

## Next Slices

* **P10-B**: JSON loader + minimal graph view
* **P10-C**: temporal strip proto
* **P10-D**: metrics panel (counts/density)
