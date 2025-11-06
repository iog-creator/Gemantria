import os, psycopg


def _dsn() -> str | None:
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise RuntimeError(
            "GEMATRIA_DSN not configured in environment.\n"
            "Please ensure:\n"
            "1. .env file exists (copy from env_example.txt)\n"
            "2. GEMATRIA_DSN is set in .env\n"
            "3. Virtual environment is active: source .venv/bin/activate\n"
            "4. Run environment validation: make env.validate"
        )
    return dsn


def mark_run_started(run_id: str, book: str, notes: str = "") -> None:
    dsn = _dsn()
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
