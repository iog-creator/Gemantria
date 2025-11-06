#!/usr/bin/env python3
import os, json, sys
import psycopg
from datetime import datetime, UTC

DSN = os.getenv("BIBLE_DB_DSN")
if not DSN:
    print("ERROR: BIBLE_DB_DSN not set", file=sys.stderr)
    sys.exit(2)


# SSOT noun adapter (tolerant to legacy fields)
def to_ssot_noun(row):
    surface = row["surface"]
    lemma = row.get("lemma")
    pos = row.get("pos") or ""
    morph = row.get("morph")
    strongs = row.get("strongs_id")
    translit = row.get("transliteration")
    gloss = row.get("gloss")
    defi = row.get("definition")
    klass = "person" if pos == "NOUN-PROP" else ("thing" if pos.startswith("NOUN") else "other")

    return {
        "surface": surface,
        "letters": None,  # calculated downstream
        "gematria_value": None,  # calculated downstream
        "class": klass,
        "analysis": {
            "lemma": lemma,
            "pos": pos,
            "morph": morph,
            "strongs_id": strongs,
            "transliteration": translit,
            "gloss": gloss,
            "definition": defi,
        },
        "sources": [{"name": "bible_db.v_morph_tokens", "ref": row["osis_ref"]}],
    }


def main(limit=None, out_path="exports/ai_nouns.db_morph.json"):
    # Escape % for psycopg3 - use %% in LIKE pattern
    q = """
    SELECT osis_ref, surface, lemma, strongs_id, morph, pos, transliteration, gloss, definition
    FROM bible.v_morph_tokens
    WHERE pos LIKE 'NOUN%%'
    """
    if limit:
        q += " LIMIT %s"
        params = (limit,)
    else:
        params = ()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    nouns = []

    with psycopg.connect(DSN) as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(q, params)
        for row in cur:
            nouns.append(to_ssot_noun(row))

    envelope = {
        "schema": "gemantria/ai-nouns.v1",
        "source": "bible_db.v_morph_tokens",
        "generated_at": datetime.now(UTC).isoformat(),
        "nodes": nouns,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(nouns)} nouns → {out_path}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", type=str, default="exports/ai_nouns.db_morph.json")
    args = ap.parse_args()
    main(limit=args.limit, out_path=args.out)
