# PM Snapshot — GemantriaV.2

_Generated: 2025-11-21T11:15:40-08:00_

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

- LM Status: `✗ lm_off`
- LM Mode: `lm_off`
- Graph Status: `✓ Ready`
- Graph Mode: `db_on`

## Status Explanation

- Level: `OK`
- Headline: All systems nominal
- Details: Database is ready and all checks passed. All 4 LM slot(s) are operational....

## Reality Check

- Overall: `✓ OK`
- Mode: `HINT`
- Hints: 3 hint(s)
  - LM configuration incomplete
  - KB: Subsystem 'agentpm' has low document coverage (1 doc(s))
  - KB: Subsystem 'webui' has low document coverage (1 doc(s))

## AI Tracking Summary

- Status: `✗ db_off`
- Mode: `db_off`
- Note: AI tracking query failed: relation "control.agent_run_cli" does not exist
LINE 7:                     FROM control.agent_run_cli
                                 ^

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

- Status: `✓ Available`
- Total documents: `9`
- Valid: `✓ Yes`

## KB Hints (Advisory)

_Note: KB hints are advisory-only and do not affect system health gates._

- INFO **[INFO] KB_LOW_COVERAGE_SUBSYSTEM**: Subsystem 'agentpm' has low document coverage (1 doc(s))
  - Subsystem: agentpm, Current docs: 1
- INFO **[INFO] KB_LOW_COVERAGE_SUBSYSTEM**: Subsystem 'webui' has low document coverage (1 doc(s))
  - Subsystem: webui, Current docs: 1

## Documentation Health (Advisory)

_Note: Documentation health metrics are advisory-only and do not affect system health gates._

- Overall freshness: `100.0%`
  - By subsystem:
    - agentpm: 100.0% fresh (missing=0, stale=0)
    - docs: 100.0% fresh (missing=0, stale=0)
    - root: 100.0% fresh (missing=0, stale=0)
    - webui: 100.0% fresh (missing=0, stale=0)
- Missing documents: `0`
- Fixes applied (last 7 days): `0`
  - Notes:
    - No plan_kb_fix manifests directory; treating fixes_applied_last_7d as 0

