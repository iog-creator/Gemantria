#!/usr/bin/env python3

import os, sys, psycopg

from psycopg.rows import dict_row


def check_dsn(name, value, want_ro=False):
    if not value:
        print(f"[FAIL] {name} not set")
        return 1

    try:
        with psycopg.connect(value, autocommit=True) as cx:
            with cx.cursor(row_factory=dict_row) as cur:
                cur.execute("select current_database() db, current_user usr")
                r = cur.fetchone()
                mode = "RO" if want_ro else "RW"
                print(f"[OK] {name} → db={r['db']} user={r['usr']} ({mode})")
                if want_ro:
                    try:
                        cur.execute("create temp table __probe(i int)")
                        print("[WARN] bible_db appears writable (expected RO)")
                    except Exception:
                        pass
                else:
                    cur.execute("create table if not exists gematria.__doctor_probe(i int)")
                    cur.execute("drop table if exists gematria.__doctor_probe")
                return 0
    except Exception as e:
        print(f"[FAIL] {name} connect error: {e}")
        return 2


def main():
    rc = 0
    rc |= check_dsn("BIBLE_DB_DSN", os.getenv("BIBLE_DB_DSN"), want_ro=True)
    rc |= check_dsn("GEMATRIA_DSN", os.getenv("GEMATRIA_DSN"), want_ro=False)
    sys.exit(rc)


if __name__ == "__main__":
    main()
