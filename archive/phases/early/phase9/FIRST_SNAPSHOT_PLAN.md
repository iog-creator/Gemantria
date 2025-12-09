# Phase-9 — First Real Snapshot Plan (Local-Only)

Linked scope: Issue #160 (**approved P9-H**).

## Inputs

- Scope: Psalms/Proverbs subset as approved (Issue #160)
- Redaction: remove non-project identifiers, normalize refs, cap fields
- Filename: `YYYYMMDD_label_seed<SEED>.json|.ndjson` (keep last 3)

## Local Procedure (nothing committed)

1) Produce the snapshot locally (outside repo)
2) Run:

   ```bash
   SNAPSHOT_FILE=/abs/path/to/snap.json make ingest.local.envelope
   SNAPSHOT_FILE=/abs/path/to/snap.json make ingest.local.envelope.schema
   ```

3. Expect:

   * Envelope JSON written to `/tmp/p9-ingest-envelope.json`
   * `SCHEMA_OK` from the schema validator

## Acceptance

* Envelope builds successfully with approved seed & naming
* Local schema validation returns `SCHEMA_OK`
* No network/DB, no share/ writes, nothing added to git
