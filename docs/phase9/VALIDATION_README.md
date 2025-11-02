# Phase-9 Local Validation (Hermetic)

Status: local-only helpers; CI no-ops by design.

## Targets

- `make ingest.local.validate` — build a metrics envelope from a snapshot
- `make ingest.local.validate.schema` — build envelope, then validate schema

## Environment (optional)

- `SNAPSHOT_FILE=docs/phase9/example_snapshot.json` — choose snapshot
- `P9_SEED=42` — deterministic seed for envelope meta

## Notes

- CI uses guards and prints HINT lines; no DB/network and no share/ writes.
- Envelope fields: meta.version, meta.source, meta.snapshot_path, meta.seed; metrics.nodes, metrics.edges, metrics.density.
