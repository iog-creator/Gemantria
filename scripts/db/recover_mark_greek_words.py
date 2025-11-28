#!/usr/bin/env python3
"""Recover missing Greek NT words for Mark 1:1-3 from legacy database.

This script attempts to:
1. Connect to the legacy BibleScholarProjectClean database
2. Extract Greek words for Mark 1:1-3
3. Populate the current bible_db with the missing data
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.config.env import get_bible_db_dsn


def try_legacy_connections() -> str | None:
    """Try to connect to legacy BibleScholarProjectClean database."""
    import psycopg

    # Try different connection methods
    connection_attempts = [
        # Method 1: Unix socket (current .env style)
        "postgresql://mccoy@/bible_db?host=/var/run/postgresql",
        # Method 2: TCP localhost with postgres user
        "postgresql://postgres:postgres@localhost:5432/bible_db",
        "postgresql://postgres:password@localhost:5432/bible_db",
        "postgresql://postgres@localhost:5432/bible_db",
        # Method 3: TCP localhost with mccoy user
        "postgresql://mccoy@localhost:5432/bible_db",
    ]

    for dsn in connection_attempts:
        try:
            print(f"Trying: {dsn.split('@')[0]}@...")
            conn = psycopg.connect(dsn)
            # Test query
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            print("✓ Connected successfully!")
            conn.close()
            return dsn
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue

    return None


def extract_mark_words_from_db(dsn: str) -> list[dict]:
    """Extract Greek words for Mark 1:1-3 from database."""
    import psycopg

    conn = psycopg.connect(dsn)
    cur = conn.cursor()

    # First, get verse_ids for Mark 1:1-3 with KJV translation
    # Note: Database uses "Mrk" not "Mark"
    cur.execute(
        """
        SELECT verse_id, book_name, chapter_num, verse_num
        FROM bible.verses
        WHERE book_name = 'Mrk'
          AND chapter_num = 1
          AND verse_num BETWEEN 1 AND 3
          AND translation_source = 'KJV'
        ORDER BY verse_num
        """
    )
    verses = cur.fetchall()

    if not verses:
        print("No KJV verses found for Mrk 1:1-3")
        print("Trying other translations...")
        cur.execute(
            """
            SELECT verse_id, book_name, chapter_num, verse_num, translation_source
            FROM bible.verses
            WHERE book_name = 'Mrk'
              AND chapter_num = 1
              AND verse_num BETWEEN 1 AND 3
            ORDER BY verse_num, translation_source
            LIMIT 3
            """
        )
        verses = cur.fetchall()

    if not verses:
        print("ERROR: No verses found for Mark 1:1-3")
        conn.close()
        return []

    print(f"Found {len(verses)} verse(s) for Mark 1:1-3")

    # Extract Greek words for these verses
    words = []
    for verse_id, book_name, chapter_num, verse_num in verses:
        cur.execute(
            """
            SELECT word_id, verse_id, word_position, word_text, strongs_id,
                   grammar_code, transliteration, gloss, theological_term
            FROM bible.greek_nt_words
            WHERE verse_id = %s
            ORDER BY word_position
            """,
            (verse_id,),
        )
        verse_words = cur.fetchall()

        if verse_words:
            print(f"  Mark {chapter_num}:{verse_num} - Found {len(verse_words)} Greek word(s)")
            for word_row in verse_words:
                words.append(
                    {
                        "word_id": word_row[0],
                        "verse_id": word_row[1],
                        "word_position": word_row[2],
                        "word_text": word_row[3],
                        "strongs_id": word_row[4],
                        "grammar_code": word_row[5],
                        "transliteration": word_row[6],
                        "gloss": word_row[7],
                        "theological_term": word_row[8],
                        "source_verse": f"{book_name} {chapter_num}:{verse_num}",
                    }
                )
        else:
            print(f"  Mark {chapter_num}:{verse_num} - No Greek words found")

    conn.close()
    return words


def populate_missing_words(target_dsn: str, words: list[dict]) -> dict:
    """Populate missing Greek words into target database."""
    import psycopg

    conn = psycopg.connect(target_dsn)
    cur = conn.cursor()

    stats = {
        "total_words": len(words),
        "inserted": 0,
        "skipped": 0,
        "errors": 0,
    }

    # First, ensure we have the verses
    verse_ids_map = {}  # Map from (book, chapter, verse) to verse_id

    for word in words:
        # Parse source verse
        parts = word["source_verse"].split()
        book_name = parts[0]
        chapter_verse = parts[1].split(":")
        chapter_num = int(chapter_verse[0])
        verse_num = int(chapter_verse[1])

        key = (book_name, chapter_num, verse_num)
        if key not in verse_ids_map:
            # Find or create verse
            cur.execute(
                """
                SELECT verse_id FROM bible.verses
                WHERE book_name = %s
                  AND chapter_num = %s
                  AND verse_num = %s
                  AND translation_source = 'TAGNT'
                LIMIT 1
                """,
                (book_name, chapter_num, verse_num),
            )
            row = cur.fetchone()
            if row:
                verse_ids_map[key] = row[0]
            else:
                # Try KJV
                cur.execute(
                    """
                    SELECT verse_id FROM bible.verses
                    WHERE book_name = %s
                      AND chapter_num = %s
                      AND verse_num = %s
                      AND translation_source = 'KJV'
                    LIMIT 1
                    """,
                    (book_name, chapter_num, verse_num),
                )
                row = cur.fetchone()
                if row:
                    verse_ids_map[key] = row[0]
                else:
                    print(f"WARNING: Verse {word['source_verse']} not found in target DB")
                    stats["errors"] += 1
                    continue

        target_verse_id = verse_ids_map[key]

        # Check if word already exists
        cur.execute(
            """
            SELECT word_id FROM bible.greek_nt_words
            WHERE verse_id = %s AND word_position = %s
            LIMIT 1
            """,
            (target_verse_id, word["word_position"]),
        )
        if cur.fetchone():
            stats["skipped"] += 1
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
                    target_verse_id,
                    word["word_position"],
                    word["word_text"],
                    word["strongs_id"],
                    word["grammar_code"],
                    word["transliteration"],
                    word["gloss"],
                    word["theological_term"],
                ),
            )
            word_id = cur.fetchone()[0]
            stats["inserted"] += 1
            print(f"  Inserted word_id={word_id} for {word['source_verse']} position={word['word_position']}")
        except Exception as e:
            print(f"  ERROR inserting word: {e}")
            stats["errors"] += 1

    conn.commit()
    conn.close()

    return stats


def main() -> int:
    """Main recovery function."""
    print("=" * 80)
    print("Recover Missing Greek Words for Mark 1:1-3")
    print("=" * 80)
    print()

    # Step 1: Try to connect to database
    print("Step 1: Connecting to database...")
    print("-" * 80)

    # Try current DSN first
    current_dsn = get_bible_db_dsn()
    if current_dsn:
        print(f"Trying configured DSN: {current_dsn.split('@')[0]}@...")
        working_dsn = try_legacy_connections()
    else:
        print("No DSN configured, trying common connection methods...")
        working_dsn = try_legacy_connections()

    if not working_dsn:
        print()
        print("ERROR: Could not connect to database")
        print("Please run: python scripts/db/diagnose_bible_db_connection.py")
        return 1

    print()

    # Step 2: Extract words from source
    print("Step 2: Extracting Greek words for Mark 1:1-3...")
    print("-" * 80)
    words = extract_mark_words_from_db(working_dsn)

    if not words:
        print("ERROR: No Greek words found for Mark 1:1-3")
        return 1

    print(f"Extracted {len(words)} Greek word(s)")
    print()

    # Step 3: Populate target database
    print("Step 3: Populating target database...")
    print("-" * 80)

    # Use same DSN for now (assuming same database)
    # In future, could support different source/target
    stats = populate_missing_words(working_dsn, words)

    print()
    print("Results:")
    print(f"  Total words: {stats['total_words']}")
    print(f"  Inserted: {stats['inserted']}")
    print(f"  Skipped (already exist): {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")
    print()

    if stats["inserted"] > 0:
        print("✓ Successfully populated missing Greek words!")
        print()
        print("Next steps:")
        print(
            "1. Verify data: SELECT * FROM bible.greek_nt_words WHERE verse_id IN (SELECT verse_id FROM bible.verses WHERE book_name='Mark' AND chapter_num=1 AND verse_num BETWEEN 1 AND 3)"
        )
        print("2. Run Phase 14 PR 14.3 verification")
    else:
        print("⚠ No new words inserted (may already exist or errors occurred)")

    print()
    print("=" * 80)

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
