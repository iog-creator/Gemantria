# UI Workspace (Phase-10)

Local-only dashboard to visualize Phase-9 envelopes.

**No CI wiring. No network. Deterministic inputs.**

## Data Source

- `/tmp/p9-ingest-envelope.json` (built via `make ingest.local.envelope`)

## Proposed Stack (local dev)

- React + Vite (TypeScript)
- Visx/React Flow for graph and metrics
- No analytics, no telemetry

## Bootstrapping (operator-only; do NOT commit lockfiles)

```bash
# choose one (examples)

npm create vite@latest ui -- --template react-ts

# or

pnpm create vite ui -- --template react-ts
```

## Minimal File Layout (target)

ui/
public/
src/
app/
components/
lib/
types/
index.html
vite.config.ts
package.json (local only)
tsconfig.json (local only)

## Loading Data

* Read `/tmp/p9-ingest-envelope.json`
* Render: graph overview, temporal strip (meta.created_at), metrics panel

> Keep everything local. Do not wire Node to CI. Do not commit large artifacts.
