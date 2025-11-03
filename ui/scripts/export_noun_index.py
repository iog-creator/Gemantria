#!/usr/bin/env python3

"""

Export nouns/occurrences to:

- share/exports/nouns.jsonl     (one record per occurrence)

- share/exports/envelope.json   (simple co-occurrence envelope)

Defaults expect:

  --nouns-table gematria.nouns( id, lemma )

  --occ-table   gematria.noun_occurrences( noun_id, verse_id, token_idx )

  --verses-table bible_db.verses( id, book, book_ord, chapter, verse )

Override with CLI flags if your names differ.

"""

from __future__ import annotations

import os, json, argparse

from collections import defaultdict

from src.infra.db_utils import get_db_connection, get_connection_dsn


OUTDIR = "share/exports"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nouns-table", default="gematria.nouns")
    ap.add_argument("--occ-table", default="gematria.noun_occurrences")
    ap.add_argument("--verses-table", default="bible_db.verses")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(OUTDIR, exist_ok=True)
    dsn = get_connection_dsn()
    with get_db_connection(dsn) as conn, conn.cursor() as cur:
        # Row-wise facts (JSONL)
        sql = f"""
          SELECT o.verse_id, v.book, v.book_ord, v.chapter, v.verse,
                 n.lemma, o.token_idx
          FROM {args.occ_table} o
          JOIN {args.nouns_table} n ON n.id = o.noun_id
          JOIN {args.verses_table} v ON v.id = o.verse_id
          ORDER BY v.book_ord, o.verse_id, o.token_idx
        """
        if args.limit > 0:
            sql += " LIMIT %s"

        cur.execute(sql, (args.limit,) if args.limit > 0 else ())
        rows = cur.fetchall()

        jsonl_path = os.path.join(OUTDIR, "nouns.jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as jf:
            for verse_id, book, book_ord, chapter, verse, lemma, token_idx in rows:
                rec = {
                    "verse_id": verse_id,
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
            verse_to_lemmas[verse_id].append(lemma)

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
            "meta": {"kind": "noun_cooccurrence", "source": "existing_nouns_pipeline"},
            "nodes": nodes,
            "edges": edges,
        }

        with open(os.path.join(OUTDIR, "envelope.json"), "w", encoding="utf-8") as ef:
            json.dump(env, ef, ensure_ascii=False)

        print(f"exported: {jsonl_path} and {os.path.join(OUTDIR, 'envelope.json')}")


if __name__ == "__main__":
    main()
