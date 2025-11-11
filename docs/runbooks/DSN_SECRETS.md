# DSN Secrets for Release Tags (STRICT)

**Purpose:** On *release tags* (e.g., `v0.0.1`), CI regenerates the PM Snapshot with real DSNs so the STRICT guard passes.

RC tags (like `v0.0.1-rc.1`) remain **lenient** and may omit DSNs.

## Required GitHub Secrets (Repository → Settings → Secrets and variables → Actions → *New repository secret*)

- `BIBLE_DB_DSN` — **read-only** PostgreSQL DSN (Bible DB). Example:

  `postgresql://postgres@/bible_db?host=/var/run/postgresql`

- `GEMATRIA_DSN` — **read-write** PostgreSQL DSN (Gemantria app DB). Example:

  `postgresql://mccoy@/gematria?host=/var/run/postgresql`

> CI uses these secrets only on **release tags** and regenerates `share/pm.snapshot.md`

> with DSNs redacted to `scheme://<REDACTED>/<dbname>`.

## What STRICT checks enforce

- PM Snapshot exists in `share/pm.snapshot.md`

- Share manifest has exactly **25** files

- On release tags, DSNs are **not** `(unset)` in the snapshot

## Test procedure (after adding secrets)

1. Push a release tag: `git tag v0.0.1 && git push origin v0.0.1`

2. Confirm Actions job **pm-snapshot** is green.

3. Open artifact `pm.snapshot` and verify DSN redaction lines are present.
