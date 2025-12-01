#!/usr/bin/env python3
"""Manually populate Greek words for Mark 1:1.

Since Mark 1:1 is missing Greek words, this script creates them based on
the Greek text of Mark 1:1. The Greek text is:
"Ἀρχὴ τοῦ εὐαγγελίου Ἰησοῦ Χριστοῦ [υἱοῦ θεοῦ]."

Strong's numbers and morphology are based on standard Greek New Testament analysis.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.config.env import get_bible_db_dsn
import psycopg


# Greek words for Mark 1:1 with Strong's numbers and positions
# Based on: "Ἀρχὴ τοῦ εὐαγγελίου Ἰησοῦ Χριστοῦ [υἱοῦ θεοῦ]."
MARK_1_1_GREEK_WORDS = [
    {
        "word_position": 1,
        "word_text": "Ἀρχὴ",
        "strongs_id": "G0746",
        "grammar_code": "N-NSF",
        "transliteration": "archē",
        "gloss": "beginning",
        "theological_term": None,
    },
    {
        "word_position": 2,
        "word_text": "τοῦ",
        "strongs_id": "G3588",
        "grammar_code": "T-GSN",
        "transliteration": "tou",
        "gloss": "the",
        "theological_term": None,
    },
    {
        "word_position": 3,
        "word_text": "εὐαγγελίου",
        "strongs_id": "G2098",
        "grammar_code": "N-GSN",
        "transliteration": "euangeliou",
        "gloss": "gospel",
        "theological_term": None,
    },
    {
        "word_position": 4,
        "word_text": "Ἰησοῦ",
        "strongs_id": "G2424",
        "grammar_code": "N-GSM",
        "transliteration": "Iēsou",
        "gloss": "Jesus",
        "theological_term": "Jesus",
    },
    {
        "word_position": 5,
        "word_text": "Χριστοῦ",
        "strongs_id": "G5547",
        "grammar_code": "N-GSM",
        "transliteration": "Christou",
        "gloss": "Christ",
        "theological_term": "Christ",
    },
    # Note: Some manuscripts include "υἱοῦ θεοῦ" (Son of God)
    # We'll include it as optional words 6-7
    {
        "word_position": 6,
        "word_text": "υἱοῦ",
        "strongs_id": "G5207",
        "grammar_code": "N-GSM",
        "transliteration": "huiou",
        "gloss": "son",
        "theological_term": None,
    },
    {
        "word_position": 7,
        "word_text": "θεοῦ",
        "strongs_id": "G2316",
        "grammar_code": "N-GSM",
        "transliteration": "theou",
        "gloss": "God",
        "theological_term": "God",
    },
]


def main() -> int:
    """Populate Greek words for Mark 1:1."""
    print("=" * 80)
    print("Populate Greek Words for Mark 1:1")
    print("=" * 80)
    print()

    dsn = get_bible_db_dsn()
    if not dsn:
        print("ERROR: No DSN configured")
        return 1

    conn = psycopg.connect(dsn)
    cur = conn.cursor()

    # Get verse_id for Mark 1:1 KJV
    print("Step 1: Finding Mark 1:1 verse...")
    print("-" * 80)
    cur.execute(
        """
        SELECT verse_id, book_name, chapter_num, verse_num, translation_source, text
        FROM bible.verses
        WHERE book_name = 'Mrk'
          AND chapter_num = 1
          AND verse_num = 1
          AND translation_source = 'KJV'
        LIMIT 1
        """
    )
    verse = cur.fetchone()

    if not verse:
        print("ERROR: Mark 1:1 (KJV) not found in database")
        conn.close()
        return 1

    verse_id, book_name, chapter_num, verse_num, translation_source, text = verse
    print(
        f"Found: verse_id={verse_id} {book_name} {chapter_num}:{verse_num} ({translation_source})"
    )
    print(f"Text: {text}")
    print()

    # Check if Greek words already exist
    print("Step 2: Checking existing Greek words...")
    print("-" * 80)
    cur.execute(
        "SELECT COUNT(*) FROM bible.greek_nt_words WHERE verse_id = %s",
        (verse_id,),
    )
    existing_count = cur.fetchone()[0]
    print(f"Existing Greek words: {existing_count}")

    if existing_count > 0:
        print("WARNING: Greek words already exist for this verse!")
        cur.execute(
            "SELECT word_id, word_position, word_text, strongs_id FROM bible.greek_nt_words WHERE verse_id = %s ORDER BY word_position",
            (verse_id,),
        )
        existing_words = cur.fetchall()
        print("Existing words:")
        for w_id, pos, word, strongs in existing_words:
            print(f"  word_id={w_id} pos={pos} '{word}' {strongs or 'N/A'}")

        response = input("\nDo you want to proceed anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            conn.close()
            return 0

    # Insert Greek words
    print()
    print("Step 3: Inserting Greek words...")
    print("-" * 80)

    inserted = 0
    skipped = 0
    errors = 0

    for word_data in MARK_1_1_GREEK_WORDS:
        # Check if word already exists at this position
        cur.execute(
            "SELECT word_id FROM bible.greek_nt_words WHERE verse_id = %s AND word_position = %s",
            (verse_id, word_data["word_position"]),
        )
        if cur.fetchone():
            print(
                f"  Skipped position {word_data['word_position']}: '{word_data['word_text']}' (already exists)"
            )
            skipped += 1
            continue

        # Insert word
        try:
            cur.execute(
                """
                INSERT INTO bible.greek_nt_words
                (verse_id, word_position, word_text, strongs_id, grammar_code,
                 transliteration, gloss, theological_term)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING word_id
                """,
                (
                    verse_id,
                    word_data["word_position"],
                    word_data["word_text"],
                    word_data["strongs_id"],
                    word_data["grammar_code"],
                    word_data["transliteration"],
                    word_data["gloss"],
                    word_data["theological_term"],
                ),
            )
            word_id = cur.fetchone()[0]
            inserted += 1
            print(
                f"  ✓ Inserted word_id={word_id} pos={word_data['word_position']} '{word_data['word_text']}' {word_data['strongs_id']}"
            )
        except Exception as e:
            errors += 1
            print(f"  ✗ ERROR inserting position {word_data['word_position']}: {e}")

    if inserted > 0:
        conn.commit()
        print()
        print(f"✓ Successfully inserted {inserted} Greek word(s)")
    else:
        print()
        print("⚠ No new words inserted")

    print()
    print("Results:")
    print(f"  Inserted: {inserted}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print()

    # Verify
    if inserted > 0:
        print("Step 4: Verifying inserted words...")
        print("-" * 80)
        cur.execute(
            "SELECT word_id, word_position, word_text, strongs_id FROM bible.greek_nt_words WHERE verse_id = %s ORDER BY word_position",
            (verse_id,),
        )
        all_words = cur.fetchall()
        print(f"Total Greek words for Mark 1:1: {len(all_words)}")
        for w_id, pos, word, strongs in all_words:
            print(f"  word_id={w_id} pos={pos} '{word}' {strongs or 'N/A'}")

    conn.close()
    print()
    print("=" * 80)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
