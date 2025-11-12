# PM Snapshot — GemantriaV.2

_Generated: 2025-11-11T16:22:29-08:00_

## Posture (DSNs + STRICT flags)

- BIBLE_DB_DSN: `postgresql://<REDACTED>/gematria`
- GEMATRIA_DSN: `postgresql://<REDACTED>/gematria`
- CHECKPOINTER: `(unset)`  — expected `postgres` in STRICT
- ENFORCE_STRICT: `(unset)`  — expected `1` in STRICT

### DB Proofs

- Bible RO probe: `(RO probe failed) psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory
	Is the server running locally and accepting connections on that socket?`
- Gematria RW temp-write probe: `(RW probe failed) psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory
	Is the server running locally and accepting connections on that socket?`

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

