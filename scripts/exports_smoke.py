# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import sys

try:
    from src.infra.db_utils import get_connection_dsn
    from src.infra.env_loader import ensure_env_loaded  # optional; no-op if absent

    ensure_env_loaded()
except Exception:
    pass

try:
    import psycopg  # psycopg3
except Exception:
    print(
        '[exports.smoke] psycopg (v3) is required. pip install "psycopg[binary]"',
        file=sys.stderr,
    )
    sys.exit(2)

DSN = get_connection_dsn(fallback="postgresql://localhost/gemantria")

PROBES = [
    (
        "concept_network count",
        "SELECT COUNT(*) FROM concept_network",
        lambda row: row[0] > 0,
    ),
    (
        "concept_relations count",
        "SELECT COUNT(*) FROM concept_relations",
        lambda row: row[0] > 0,
    ),
    (
        "relations key NULL-safety",
        "SELECT COUNT(*) FROM concept_relations WHERE source_id IS NULL OR target_id IS NULL",
        lambda row: row[0] == 0,
    ),
]


def main() -> int:
    try:
        with psycopg.connect(DSN) as conn, conn.cursor() as cur:
            failures = 0
            for label, sql, ok in PROBES:
                try:
                    cur.execute(sql)
                    row = cur.fetchone()
                    verdict = ok(row)
                    if verdict:
                        print(f"[exports.smoke] OK {label}: {row[0]}")
                    else:
                        print(f"[exports.smoke] FAIL {label}: {row[0]}", file=sys.stderr)
                        failures += 1
                except Exception as e:
                    print(f"[exports.smoke] FAIL {label}: {e}", file=sys.stderr)
                    failures += 1
    except Exception as e:
        print(f"[exports.smoke] DB connection failed: {e}", file=sys.stderr)
        return 2

    if failures:
        print(f"[exports.smoke] SUMMARY: {failures} failure(s)", file=sys.stderr)
        return 1
    print("[exports.smoke] SUMMARY: all checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
