# MCP Knowledge DB — Bring-up & Proof (RFC-078)

**Goal:** Use Postgres as the Knowledge MCP source (catalog-as-a-service).

- **STRICT (tags):** Read-only DSN; no writes; prove `mcp.v_catalog` exists.

- **HINT (dev/PR):** Optional local DB; guards skip network probes by default.

## Apply Schema (dev/local)

```bash
# Uses your RO/RW DSN; be careful on prod.
psql "$GEMATRIA_DSN" -f db/sql/078_mcp_knowledge.sql
```

## Guard (STRICT lane)

```bash
# Skip by default; enable only where DSNs are wired (e.g., tagproof)
make guard.mcp.db.ro STRICT_DB_PROBE=1
```

## Evidence

* `evidence/guard_mcp_db_ro.final.json` — includes `view_count` and `ok`.

* Atlas webproof should show MCP endpoints panel; screenshots under `share/releases/.../webproof/`.

## DSN Redaction

All DSNs must be redacted in artifacts per governance (Rule-050/051). Never print raw DSNs.

## Tag lane (STRICT) — Read-only proof

On release tags, CI must prove the Postgres Knowledge MCP is reachable in **read-only** mode and that `mcp.v_catalog` exists:

```bash
make guard.mcp.db.ro STRICT_DB_PROBE=1
```

This runs in tagproof only (no DB probes in PR CI), and must **not** perform any writes.
