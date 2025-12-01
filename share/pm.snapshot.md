# PM Snapshot — GemantriaV.2

_Generated: 2025-12-01T08:00:53-08:00_

## Posture (DSNs + STRICT flags)

- BIBLE_DB_DSN: `postgresql://<REDACTED>/bible_db`
- GEMATRIA_DSN: `postgresql://<REDACTED>/gematria`
- CHECKPOINTER: `(unset)`  — expected `postgres` in STRICT
- ENFORCE_STRICT: `(unset)`  — expected `1` in STRICT

### DB Proofs

- Bible RO probe: `bible_db|mccoy`
- Gematria RW temp-write probe: `ok`

### DB Health Guard

- Status: `✓ Ready`
- Mode: `ready`
- Driver available: `✓`
- Connection OK: `✓`
- Graph stats ready: `✓`

```json
{
  "ok": true,
  "mode": "ready",
  "checks": {
    "driver_available": true,
    "connection_ok": true,
    "graph_stats_ready": true
  },
  "details": {
    "errors": []
  }
}
```

## Now / Next / Later (PM-facing)

**Now**
- Keep GemantriaV.2 as the active project.
- Use `STRICT` posture when DSNs present; otherwise HINT mode is allowed for hermetic tests.
- Regenerate this PM Snapshot on each bring-up or DSN change (`make pm.snapshot`).

**Next**
- Ensure `share/` always contains the canonical 25 files (see Manifest section).
- Add the `Pilot-001 (VL Validator)` checklist when bring-up is green.

**Later**
- Attach Atlas/CI proofs to this snapshot (screenshots + JSON tails) once Web proof targets are finalized.

## Evidence links

- Guards summary: (bring-up not yet run in this session)

## Manifest status

- Status: `✗ Error`
- File count: `0`
- Error: Manifest file not found: /home/mccoy/Projects/docs/SSOT/SHARE_MANIFEST.json

## System Health (DB + LM + Graph)

- LM Status: `✓ Ready`
- LM Mode: `lm_ready`
- Graph Status: `✓ Ready`
- Graph Mode: `db_on`

## Status Explanation

- Level: `OK`
- Headline: All systems nominal
- Details: Database is ready and all checks passed. All 4 LM slot(s) are operational....

## Reality Check

- Overall: `✓ OK`
- Mode: `HINT`
- Hints: 2 hint(s)
  - DMS-REQUIRED: reality.green STRICT must pass all required checks before declaring system ready.
  - KB: KB registry file not found (registry may not be seeded yet)

## AI Tracking Summary

- Status: `✓ Active`
- Mode: `db_on`
- Runtime LM calls (agent_run): 2270 total, 111 last 24h
- CLI commands (agent_run_cli): 68 total, 28 last 24h, 3 success, 0 errors

## Eval Insights Summary (Advisory Analytics)

_Note: Eval insights are export-driven analytics (Phase-8/10) and are advisory only. They do not affect system health gates._

- LM Indicator: `✗ Unavailable`
  - Note: LM indicator export not available (file missing)
- DB Health Snapshot: `✗ Unavailable`
  - Note: DB health snapshot not available (file missing; run `make pm.snapshot`)
- Edge Class Counts: `✗ Unavailable`
  - Note: Edge class counts export not available (file missing)

## KB Registry Summary (Advisory)

_Note: KB registry is advisory-only and read-only in CI. It does not affect system health gates._

- Status: `✗ Unavailable`
- Note: KB registry file not found

## KB Hints (Advisory)

_Note: KB hints are advisory-only and do not affect system health gates._

- INFO **[INFO] KB_REGISTRY_UNAVAILABLE**: KB registry file not found (registry may not be seeded yet)

## Documentation Health (Advisory)

_Note: Documentation health metrics are advisory-only and do not affect system health gates._

- Status: `✗ Unavailable`
- Note: KB doc-health metrics unavailable

