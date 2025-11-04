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

import os, json, argparse

from collections import defaultdict

from src.infra.db_utils import get_db_connection, get_connection_dsn


OUTDIR = "share/exports"


def extract_and_populate_nouns(conn, args):
    """Extract nouns from bible_db and populate gematria.nouns table."""
    with conn.cursor() as cur:
        # Create tables if they don't exist
        cur.execute(f"""
            CREATE SCHEMA IF NOT EXISTS gematria;

            CREATE TABLE IF NOT EXISTS {args.nouns_table} (
                id            BIGSERIAL PRIMARY KEY,
                book          TEXT NOT NULL,
                chapter       INT  NOT NULL,
                verse         INT  NOT NULL,
                lemma         TEXT NOT NULL,
                surface       TEXT NOT NULL,
                language      TEXT NOT NULL DEFAULT 'he',
                source_id     TEXT,
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
            CREATE INDEX IF NOT EXISTS idx_nouns_book_chapter_verse ON {args.nouns_table}(book,chapter,verse);
            CREATE INDEX IF NOT EXISTS idx_noun_occurrences_verse_id ON {args.occ_table}(verse_id);
        """)

        # Build query for extracting nouns
        query = f"""
            SELECT v.book, v.book_ord, v.chapter, v.verse,
                   t.word as surface, t.lemma, t.id as token_id, t.token_idx
            FROM {args.verses_table} v
            JOIN {args.tokens_table} t ON v.id = t.verse_id
            WHERE t.pos LIKE 'N%%'
        """

        params = []
        if args.books:
            books = [b.strip() for b in args.books.split(',')]
            placeholders = ','.join(['%s'] * len(books))
            query += f" AND v.book IN ({placeholders})"
            params.extend(books)

        query += " ORDER BY v.book_ord, v.chapter, v.verse, t.token_idx"

        if args.limit > 0:
            query += " LIMIT %s"
            params.append(args.limit)

        cur.execute(query, params)
        rows = cur.fetchall()

        print(f"Found {len(rows)} noun tokens to process")

        # Group by lemma for deduplication
        lemma_occurrences = defaultdict(list)

        for book, book_ord, chapter, verse, surface, lemma, token_id, token_idx in rows:
            verse_id = f"{book_ord:02d}{chapter:03d}{verse:03d}"
            lemma_occurrences[lemma].append({
                'book': book,
                'chapter': chapter,
                'verse': verse,
                'verse_id': verse_id,
                'surface': surface,
                'token_id': str(token_id),
                'token_idx': token_idx
            })

        # Insert nouns and occurrences
        nouns_inserted = 0
        occurrences_inserted = 0

        for lemma, occurrences in lemma_occurrences.items():
            # Use first occurrence for primary noun record
            first_occ = occurrences[0]

            # Insert noun
            cur.execute(f"""
                INSERT INTO {args.nouns_table} (book, chapter, verse, lemma, surface, source_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (book, chapter, verse, lemma) DO UPDATE SET
                    surface = EXCLUDED.surface,
                    source_id = EXCLUDED.source_id
            """, (
                first_occ['book'], first_occ['chapter'], first_occ['verse'],
                lemma, first_occ['surface'], first_occ['token_id']
            ))

            # Get the noun_id
            cur.execute(f"""
                SELECT id FROM {args.nouns_table}
                WHERE book = %s AND chapter = %s AND verse = %s AND lemma = %s
            """, (first_occ['book'], first_occ['chapter'], first_occ['verse'], lemma))

            noun_id = cur.fetchone()[0]

            # Insert all occurrences
            for occ in occurrences:
                cur.execute(f"""
                    INSERT INTO {args.occ_table} (noun_id, verse_id, token_idx)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (noun_id, verse_id, token_idx) DO NOTHING
                """, (noun_id, int(occ['verse_id']), occ['token_idx']))
                occurrences_inserted += 1

            nouns_inserted += 1

            if nouns_inserted % 100 == 0:
                print(f"Processed {nouns_inserted} unique lemmas...")

        print(f"Inserted {nouns_inserted} unique nouns and {occurrences_inserted} occurrences")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nouns-table", default="gematria.nouns")
    ap.add_argument("--occ-table", default="gematria.noun_occurrences")
    ap.add_argument("--verses-table", default="bible_db.verses")
    ap.add_argument("--tokens-table", default="bible_db.tokens")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--extract-from-bible", action="store_true",
                   help="Extract nouns directly from bible_db.tokens and populate gematria.nouns")
    ap.add_argument("--books", help="Comma-separated book names (for --extract-from-bible)")
    args = ap.parse_args()

    os.makedirs(OUTDIR, exist_ok=True)
    dsn = get_connection_dsn()
    with get_db_connection(dsn) as conn:
        if args.extract_from_bible:
            # Extract from bible_db and populate gematria tables
            extract_and_populate_nouns(conn, args)

        # Export from gematria tables (whether just populated or pre-existing)
        with conn.cursor() as cur:
            sql = f"""
              SELECT o.verse_id, v.book, v.book_ord, v.chapter, v.verse,
                     n.lemma, o.token_idx
              FROM {args.occ_table} o
              JOIN {args.nouns_table} n ON n.id = o.noun_id
              JOIN {args.verses_table} v ON CAST(v.id AS TEXT) = CAST(o.verse_id AS TEXT)
              ORDER BY v.book_ord, o.verse_id, o.token_idx
            """
            if args.limit > 0:
                sql += " LIMIT %s"

            cur.execute(sql, (args.limit,) if args.limit > 0 else ())
            rows = cur.fetchall()

            if not rows:
                print(f"No noun data found in {args.nouns_table}. Run with --extract-from-bible first.")
                return

            jsonl_path = os.path.join(OUTDIR, "nouns.jsonl")
            with open(jsonl_path, "w", encoding="utf-8") as jf:
                for verse_id, book, book_ord, chapter, verse, lemma, token_idx in rows:
                    rec = {
                        "verse_id": str(verse_id),
                        "book": book,
                        "book_ord": book_ord,
                        "chapter": chapter,
                        "verse": verse,
                        "lemma": lemma,
                        "token_idx": token_idx,
                    }
                    jf.write(json.dumps(rec, ensure_ascii=False) + "\n")

            # Envelope (co-occurrence per verse)
            verse_to_lemmas = defaultdict(list)
            for verse_id, _book, _bo, _c, _v, lemma, _ti in rows:
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
