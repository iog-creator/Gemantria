# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

"""

Export nouns/occurrences to:

- share/exports/nouns.jsonl     (one record per occurrence)

- share/exports/envelope.json   (simple co-occurrence envelope)

MODES:

1. Export from existing gematria.nouns + noun_occurrences tables (default)

2. Extract directly from bible_db.tokens and populate gematria.nouns (--extract-from-bible)

Defaults expect:

  --nouns-table gematria.nouns( id, lemma )

  --occ-table   gematria.noun_occurrences( noun_id, verse_id, token_idx )

  --verses-table bible_db.verses( id, book, book_ord, chapter, verse )

  --tokens-table bible_db.tokens( id, verse_id, word, lemma, pos )

Override with CLI flags if your names differ.

"""

from __future__ import annotations

import os, json, argparse, sys
from pathlib import Path
from collections import defaultdict

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from src.infra.db_utils import get_db_connection, get_connection_dsn
except ImportError:
    # Fallback: try direct import from absolute path
    import importlib.util

    spec = importlib.util.spec_from_file_location("db_utils", src_path / "infra" / "db_utils.py")
    db_utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_utils)
    get_db_connection = db_utils.get_db_connection
    get_connection_dsn = db_utils.get_connection_dsn


OUTDIR = "share/exports"


def extract_and_populate_nouns(bible_conn, gematria_conn, args):
    """Extract nouns from bible_db and populate gematria.nouns table."""
    # Create tables in gematria DB first
    with gematria_conn.cursor() as cur:
        cur.execute(f"""
            CREATE SCHEMA IF NOT EXISTS gematria;

            CREATE TABLE IF NOT EXISTS {args.nouns_table} (
                id            BIGSERIAL PRIMARY KEY,
                lemma         TEXT NOT NULL UNIQUE,
                language      TEXT NOT NULL DEFAULT 'he',
                created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS {args.occ_table} (
                noun_id       BIGINT NOT NULL REFERENCES {args.nouns_table}(id) ON DELETE CASCADE,
                verse_id      BIGINT NOT NULL,
                token_idx     INT NOT NULL,
                created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (noun_id, verse_id, token_idx)
            );

            CREATE INDEX IF NOT EXISTS idx_nouns_lemma ON {args.nouns_table}(lemma);
            CREATE INDEX IF NOT EXISTS idx_noun_occurrences_verse_id ON {args.occ_table}(verse_id);
        """)

    # Extract from bible DB
    with bible_conn.cursor() as bible_cur:
        # Set search path to include bible schema
        bible_cur.execute('SET search_path TO bible, public, "$user"')

        # Build query for extracting nouns from hebrew_ot_words
        query = """
            SELECT v.book_name, v.chapter_num, v.verse_num, v.verse_id,
                   t.word_text as surface, l.lemma, t.word_id as token_id, t.word_position as token_idx
            FROM verses v
            JOIN hebrew_ot_words t ON v.verse_id = t.verse_id
            JOIN lemmas l ON l.strong_number = t.strongs_id
            WHERE t.grammar_code LIKE %s  -- Hebrew nouns
            AND t.grammar_code NOT LIKE %s  -- Exclude verbs
            AND t.grammar_code NOT LIKE %s  -- Exclude adjectives
        """
        params = ["H%/N%", "%/V%", "%/A%"]

        if args.books:
            books = [b.strip() for b in args.books.split(",")]
            placeholders = ",".join(["%s"] * len(books))
            query += f" AND v.book_name IN ({placeholders})"
            params.extend(books)

        query += " ORDER BY v.book_name, v.chapter_num, v.verse_num, t.word_position"

        if args.limit > 0:
            query += " LIMIT %s"
            params.append(args.limit)

        bible_cur.execute(query, params)
        rows = bible_cur.fetchall()

        print(f"Found {len(rows)} noun tokens to process")

        # Group by lemma for deduplication
        lemma_occurrences = defaultdict(list)

        for book, chapter, verse, verse_id, surface, lemma, token_id, token_idx in rows:
            lemma_occurrences[lemma].append(
                {
                    "book": book,
                    "chapter": chapter,
                    "verse": verse,
                    "verse_id": verse_id,
                    "surface": surface,
                    "token_id": str(token_id),
                    "token_idx": token_idx,
                }
            )

    # Insert unique nouns and occurrences into gematria DB
    with gematria_conn.cursor() as gematria_cur:
        # Insert unique nouns first
        unique_lemmas = list(lemma_occurrences.keys())
        print(f"Inserting {len(unique_lemmas)} unique lemmas...")

        for lemma in unique_lemmas:
            gematria_cur.execute(
                f"""
                INSERT INTO {args.nouns_table} (lemma, language)
                VALUES (%s, 'he')
                ON CONFLICT (lemma) DO NOTHING
            """,
                (lemma,),
            )

        nouns_inserted = gematria_cur.rowcount
        print(f"Inserted {nouns_inserted} new unique nouns")

        # Now insert all occurrences
        occurrences_inserted = 0

        for lemma, occurrences in lemma_occurrences.items():
            # Get the noun_id
            gematria_cur.execute(f"SELECT id FROM {args.nouns_table} WHERE lemma = %s", (lemma,))
            noun_id = gematria_cur.fetchone()[0]

            # Insert all occurrences for this lemma
            for occ in occurrences:
                gematria_cur.execute(
                    f"""
                    INSERT INTO {args.occ_table} (noun_id, verse_id, token_idx)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (noun_id, verse_id, token_idx) DO NOTHING
                """,
                    (noun_id, occ["verse_id"], occ["token_idx"]),
                )
                occurrences_inserted += 1

        print(f"Inserted {occurrences_inserted} noun occurrences")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nouns-table", default="gematria.nouns")
    ap.add_argument("--occ-table", default="gematria.noun_occurrences")
    ap.add_argument("--verses-table", default="bible.verses")
    ap.add_argument("--tokens-table", default="bible.hebrew_ot_words")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument(
        "--extract-from-bible",
        action="store_true",
        help="Extract nouns directly from bible.hebrew_ot_words and populate gematria.nouns",
    )
    ap.add_argument("--books", help="Comma-separated book names (for --extract-from-bible)")
    args = ap.parse_args()

    os.makedirs(OUTDIR, exist_ok=True)

    # Get both DSNs
    bible_dsn = get_connection_dsn("BIBLE_DB_DSN")
    gematria_dsn = get_connection_dsn("GEMATRIA_DSN")

    if args.extract_from_bible:
        print(f"DEBUG: Using bible DSN: {bible_dsn}", file=sys.stderr)
        print(f"DEBUG: Using gematria DSN: {gematria_dsn}", file=sys.stderr)
        with (
            get_db_connection(bible_dsn) as bible_conn,
            get_db_connection(gematria_dsn) as gematria_conn,
        ):
            extract_and_populate_nouns(bible_conn, gematria_conn, args)

    # Always export from gematria DB
    print(f"DEBUG: Using gematria DSN for export: {gematria_dsn}", file=sys.stderr)
    with get_db_connection(gematria_dsn) as conn:
        # Export from gematria tables (whether just populated or pre-existing)
        # Note: Simplified export without verse metadata for now
        with conn.cursor() as cur:
            sql = f"""
              SELECT o.verse_id, n.lemma, o.token_idx
              FROM {args.occ_table} o
              JOIN {args.nouns_table} n ON n.id = o.noun_id
              ORDER BY o.verse_id, o.token_idx
            """
            if args.limit > 0:
                sql += " LIMIT %s"

            cur.execute(sql, (args.limit,) if args.limit > 0 else ())
            rows = cur.fetchall()

            if not rows:
                print(
                    f"No noun data found in {args.nouns_table}. Run with --extract-from-bible first."
                )
                return

            jsonl_path = os.path.join(OUTDIR, "nouns.jsonl")
            with open(jsonl_path, "w", encoding="utf-8") as jf:
                for verse_id, lemma, token_idx in rows:
                    rec = {
                        "verse_id": str(verse_id),
                        "lemma": lemma,
                        "token_idx": token_idx,
                    }
                    jf.write(json.dumps(rec, ensure_ascii=False) + "\n")

            # Envelope (co-occurrence per verse)
            verse_to_lemmas = defaultdict(list)
            for verse_id, lemma, _ti in rows:
                verse_to_lemmas[str(verse_id)].append(lemma)

            nodes_map, nodes, edges = {}, [], []
            nid = 0
            for lemmas in verse_to_lemmas.values():
                uniq = list(dict.fromkeys(lemmas))
                for lemma in uniq:
                    if lemma not in nodes_map:
                        nodes_map[lemma] = str(nid)
                        nodes.append({"id": str(nid), "label": lemma})
                        nid += 1
                for i in range(len(uniq)):
                    for j in range(i + 1, len(uniq)):
                        edges.append(
                            {
                                "src": nodes_map[uniq[i]],
                                "dst": nodes_map[uniq[j]],
                                "rel_type": "cooccur",
                            }
                        )

            env = {
                "meta": {"kind": "noun_cooccurrence", "source": "gematria_nouns_pipeline"},
                "nodes": nodes,
                "edges": edges,
            }

            with open(os.path.join(OUTDIR, "envelope.json"), "w", encoding="utf-8") as ef:
                json.dump(env, ef, ensure_ascii=False)

            print(f"exported: {jsonl_path} and {os.path.join(OUTDIR, 'envelope.json')}")


if __name__ == "__main__":
    main()
