# Master Reference Tracking (OPS v6.2)

- Source of truth file: `docs/SSOT/GEMATRIA_MASTER_REFERENCE*.md`

- Tracker writes section metadata to DB table `document_sections` (managed by populate script).

- Make targets:

  - `make docs.masterref.populate` — run tracker (HINT: skips if no DSN; STRICT: fail closed)

  - `make docs.masterref.check` — run hints/consistency checks if available

- CI can run this when `vars.ENABLE_MASTERREF=1` and a RO/RW DSN secret is provided.

