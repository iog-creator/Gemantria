import os, psycopg


def _dsn() -> str | None:
    return os.getenv("GEMATRIA_DSN")


def mark_run_started(run_id: str, book: str, notes: str = "") -> None:
    dsn = _dsn()
    if not dsn:
        return
    with psycopg.connect(dsn) as c, c.cursor() as cur:
        cur.execute(
            """
            INSERT INTO gematria.runs_ledger (run_id, book, notes, started_at)
            VALUES (%s,%s,%s, now())
            ON CONFLICT (run_id) DO NOTHING
        """,
            (run_id, book, notes),
        )


def mark_run_finished(run_id: str, notes: str = "") -> None:
    dsn = _dsn()
    if not dsn:
        return
    with psycopg.connect(dsn) as c, c.cursor() as cur:
        cur.execute(
            """
            UPDATE gematria.runs_ledger
               SET finished_at = now(),
                   notes = COALESCE(NULLIF(%s,''), notes)
             WHERE run_id = %s
        """,
            (notes, run_id),
        )
