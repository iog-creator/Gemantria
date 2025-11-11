# DSN Secrets for Release Tags (STRICT)

**Purpose:** On *release tags* (e.g., `v0.0.1`), CI regenerates the PM Snapshot with real DSNs so the STRICT guard passes.

RC tags (like `v0.0.1-rc.1`) remain **lenient** and may omit DSNs.

## Required GitHub Variables (Repository → Settings → Secrets and variables → Actions → Variables → *New repository variable*)

- `ATLAS_DSN` — **read-only** PostgreSQL DSN for Atlas UI proof. Example:

  `postgresql://postgres@/gematria?host=/var/run/postgresql`

  **Used in:** `tagproof.yml` (release tags) — **REQUIRED** for STRICT proof step

## Required GitHub Secrets (Repository → Settings → Secrets and variables → Actions → Secrets → *New repository secret*)

- `BIBLE_DB_DSN` — **read-only** PostgreSQL DSN (Bible DB). Example:

  `postgresql://postgres@/bible_db?host=/var/run/postgresql`

  **Used in:** `pm-snapshot.yml` (release tags), `tagproof.yml` (release tags)

- `GEMATRIA_DSN` — **read-write** PostgreSQL DSN (Gemantria app DB). Example:

  `postgresql://mccoy@/gematria?host=/var/run/postgresql`

  **Used in:** `pm-snapshot.yml` (release tags), `tagproof.yml` (release tags)

> CI uses these secrets only on **release tags** and regenerates `share/pm.snapshot.md`

> with DSNs redacted to `scheme://<REDACTED>/<dbname>`.

## What STRICT checks enforce

- PM Snapshot exists in `share/pm.snapshot.md`

- Share manifest has exactly **25** files

- On release tags, DSNs are **not** `(unset)` in the snapshot

## Test procedure (after adding variables and secrets)

1. Set all required variables and secrets in GitHub UI:
   - **Variable:** `ATLAS_DSN` (Settings → Secrets and variables → Actions → Variables)
   - **Secret:** `BIBLE_DB_DSN` (Settings → Secrets and variables → Actions → Secrets)
   - **Secret:** `GEMATRIA_DSN` (Settings → Secrets and variables → Actions → Secrets)

2. Push a release tag: `git tag v0.0.2 && git push origin v0.0.2`

3. Confirm Actions jobs **tagproof** and **pm-snapshot** are green.

4. Open artifacts and verify DSN redaction lines are present (DSNs masked in outputs).
