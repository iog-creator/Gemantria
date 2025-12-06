# Gemantria UI (Phase-10 Dashboard)

## Setup
- cd ui && npm install (or pnpm/yarn)
- npm run dev (localhost:5173)

## Core Views
- **Statistics**: Envelope stats + node/edge counts (from unified_envelope.json)
- **Graph View**: Minimal force-directed graph render (nodes/edges from envelope)
- **Temporal Analytics**: Rolling windows + forecasts (from temporal_patterns.json + pattern_forecast.json)

## Temporal Analytics Section

### Generate Artifacts
Run the pipeline to produce temporal data:
```bash
export BOOK=Genesis
make orchestrator.full  # Full pipeline (includes temporal)
# Or just temporal:
make phase8.temporal
```
- Outputs: `share/exports/temporal_patterns.json` (rolling stats/trends) and `share/exports/pattern_forecast.json` (Prophet forecasts).
- Schema: Validated against `docs/SSOT/temporal-patterns.schema.json` and `pattern-forecast.schema.json` (empty OK for smoke).

### Mirror to UI
Copy artifacts for frontend loading:
```bash
make ui.mirror.temporal
```
- Lands in: `ui/out/temporal_patterns.json` and `ui/out/pattern_forecast.json` (from share/exports/).
- Smoke: `make ui.smoke.temporal` (validates JSON parse).
- Build: `make ui.build` (npm ci + npm run build; skips if ui/ incomplete).

### View the Page
- Load an envelope via FileLoader (or auto from /out/).
- Click "Temporal Analytics" tab in the dashboard.
- Renders: `<TemporalStrip />` component (Recharts line chart for rolling gematria trends + forecast bands).
- Handles empty data gracefully (shows stub chart; extend for real metrics like mean_gematria over positions).

### Notes
- Dummies: If files missing, create minimal JSONs in share/exports/ matching schemas (see scripts/export_stats.py for structure).
- Tests: `pytest tests/ui/test_temporal_mirror.py` (robust to missing files in dev).
- Sync: After pipeline changes, run `make share.sync` to propagate to share/ (Rule-058).
