# Ingestion Envelope — Fields (Plan Only)

Linked scope: see Issue #160 (approved P9-H).

## Meta

- `version` (string) — semantic; default "0.1.0"

- `source` (string) — "p9-envelope-local" or descriptive

- `snapshot_path` (string) — local path used to build envelope

- `seed` (integer) — deterministic seed

- `created_at` (string, ISO8601) — optional (may be added later)

## Nodes

- `id` (string) — required; canonical identifier

- `label` (string, ≤120) — normalized (spaces collapsed)

- `type` (string, ≤40) — normalized; optional

- `attrs` (object) — optional, bounded keys/values (TBD caps)

## Edges

- `src` (string) — required; node id

- `dst` (string) — required; node id

- `rel_type` (string, ≤40) — normalized relation label

- `weight` (number [0..1]) — optional; clamped

## Constraints & Notes

- No external network/DB in CI; local-only build paths.

- Deterministic: fixed seed; stable normalization.

- Future: provenance `prov` block (TBD), audit trail IDs (TBD).
