# Ingest Envelope (Local-Only Stub)

Build a minimal ingestion envelope from a snapshot using the Phase-9 mappers.

Hermetic: no DB/network; CI guards print HINT and exit 0.

## Usage

```bash
# from repo root
make ingest.local.envelope
# Output path printed (default): /tmp/p9-ingest-envelope.json
```

### Env knobs

* `SNAPSHOT_FILE=docs/phase9/snapshots/<file>.json`
* `P9_SEED=42`
* `OUT_FILE=/tmp/p9-ingest-envelope.json`

### CI behavior

Targets `ci.ingest.envelope.check` and `ingest.local.envelope` are guarded in CI and do not perform IO.

### Provenance

- `meta.created_at` is included by the builder.
- For deterministic local runs, set `P9_CREATED_AT=YYYY-MM-DDTHH:MM:SS` before building.
