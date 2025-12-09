# Phase-9 — Snapshot Preparation & Rotation (Local-Only)

**Purpose**: Provide deterministic, local snapshots for ingestion/validation.

**CI policy**: No DB/network; CI never consumes real snapshots (guards print HINT).

## Directory

- `docs/phase9/snapshots/` — local snapshots (gitignored)
- `docs/phase9/example_snapshot.json` — committed example for tooling sanity

## Naming

`YYYYMMDD_label_seed<SEED>.json` (or `.ndjson`)

Examples: `20251102_demo_seed42.json`, `20251102_psalms_seed13.ndjson`

## Minimal JSON structure

```json
{
  "meta": {"version": "0.1.0", "seed": 42},
  "nodes": [{"id": "n1", "label": "example"}],
  "edges": []
}
```

## Local use

```bash
SNAPSHOT_FILE=docs/phase9/snapshots/20251102_demo_seed42.json make ingest.local.validate
SNAPSHOT_FILE=docs/phase9/snapshots/20251102_demo_seed42.json make ingest.local.validate.schema
```

## Rotation policy (local)

* Keep last **3** snapshots per label/seed.
* Prefer stable seeds (e.g., 42) for comparability.
* Do **not** commit real snapshots; only commit `example_snapshot.json`.

## Notes

* Envelope fields validated: `meta.version|source|snapshot_path|seed` and `metrics.nodes|edges|density`.
* CI targets `ci.ingest.*` are guarded and exit 0 with HINT lines.
