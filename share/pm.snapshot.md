# PM Snapshot — GemantriaV.2

_Generated: 2025-11-29T18:43:19-08:00_

## Posture (DSNs + STRICT flags)

- BIBLE_DB_DSN: `postgresql://<REDACTED>/bible_db`
- GEMATRIA_DSN: `postgresql://<REDACTED>/gematria`
- CHECKPOINTER: `(unset)`  — expected `postgres` in STRICT
- ENFORCE_STRICT: `(unset)`  — expected `1` in STRICT

### DB Proofs

- Bible RO probe: `bible_db|mccoy`
- Gematria RW temp-write probe: `ok`

### DB Health Guard

- Status: `✗ error`
- Mode: `error`

```json
{
  "ok": false,
  "mode": "error",
  "error": "guard_db_health failed: No module named 'sqlalchemy'"
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
- Error: Failed to read manifest: No module named 'sqlalchemy'

## System Health (DB + LM + Graph)

- LM Status: `✗ error`
- LM Mode: `error`
- Graph Status: `✗ error`
- Graph Mode: `error`

## Status Explanation

- Level: `ERROR`
- Headline: Status explanation unavailable
- Details: Failed to generate explanation: No module named 'sqlalchemy'...

## Reality Check

- Overall: `✗ FAILED`
- Mode: `HINT`

## AI Tracking Summary

- Status: `✗ db_off`
- Mode: `db_off`
- Note: AI tracking failed: No module named 'sqlalchemy'

## Eval Insights Summary (Advisory Analytics)

_Note: Eval insights are export-driven analytics (Phase-8/10) and are advisory only. They do not affect system health gates._

- LM Indicator: `✗ Unavailable`
  - Note: LM indicator export not found
- DB Health Snapshot: `✗ Unavailable`
  - Note: DB health export not found
- Edge Class Counts: `✗ Unavailable`
  - Note: Edge class counts export not found

## KB Registry Summary (Advisory)

_Note: KB registry is advisory-only and read-only in CI. It does not affect system health gates._

- Status: `✗ Unavailable`
- Note: KB registry unavailable: No module named 'sqlalchemy'

## KB Hints (Advisory)

_Note: KB hints are advisory-only and do not affect system health gates._

- ✓ No KB registry issues detected

## Documentation Health (Advisory)

_Note: Documentation health metrics are advisory-only and do not affect system health gates._

- Status: `✗ Unavailable`
- Note: KB doc-health metrics unavailable

