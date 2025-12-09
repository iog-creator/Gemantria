# Real-Data Ingestion Plan (Phase-9, reuse-first)

## Sources (reuse, no new code in CI)

- `bible_db` (read-only) vs `gematria` (RW) — DSNs from environment.
- **DSN Access**: All DSN access must go through centralized loaders (`scripts.config.env` preferred, `src.gemantria.dsn` legacy). Never use `os.getenv("GEMATRIA_DSN")` directly - enforced by `guard.dsn.centralized`.

## Minimal knobs (already in repo)

- `BIBLE_DSN`, `GEMATRIA_DSN`, `PIPELINE_SEED`, `EDGE_STRONG`, `EDGE_WEAK`, `CANDIDATE_POLICY`.

## Steps (outside CI; dev/operator only)

1) Verify DSNs locally (use centralized loader: `python3 -c "from scripts.config.env import get_bible_db_dsn; print(get_bible_db_dsn())"` or `psql $(python3 -c "from scripts.config.env import get_bible_db_dsn; print(get_bible_db_dsn())") -c '\dt'`).

2) Run `make db.migrate` then pipeline on a tiny sample (no CI network).

3) Export + bundle: `make exports.write && make webui.smoke`.

## CI behavior

- CI must remain hermetic: no network/DB. `ci.ingest.check` only validates env presence and prints guidance.
