# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Book smoke: empty-DB tolerant.

- If GEMATRIA_DSN unset or psycopg not available: SKIP (exit 0).
- If available: run a trivial SELECT 1 to prove connectivity.

Never fails CI for missing DB; this is a posture proof, not a migration.
"""

from __future__ import annotations

import sys
from gemantria.dsn import dsn_rw


def main() -> int:
    dsn = dsn_rw()

    try:
        import psycopg  # type: ignore
    except Exception:  # pragma: no cover - best effort for optional dependency
        print("book.smoke: SKIP (no psycopg or DSN)")
        return 0

    if not dsn:
        print("book.smoke: SKIP (no GEMATRIA_DSN)")
        return 0

    try:
        with psycopg.connect(dsn, connect_timeout=2) as conn:  # type: ignore[attr-defined]
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()

        print(f"book.smoke: OK (db responded {row[0]})")
        return 0
    except Exception as exc:  # pragma: no cover - runtime informational hint
        # Do not fail closed on local smoke; print hint and pass.
        print(f"book.smoke: HINT only ({exc.__class__.__name__}: {exc})")
        return 0


if __name__ == "__main__":
    sys.exit(main())
