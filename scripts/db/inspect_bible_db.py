#!/usr/bin/env python3
"""Inspect bible_db to see what data exists."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.config.env import get_bible_db_dsn
import psycopg


def main() -> int:
    dsn = get_bible_db_dsn()
    if not dsn:
        print("ERROR: No DSN configured")
        return 1

    conn = psycopg.connect(dsn)
    cur = conn.cursor()

    print("=" * 80)
    print("Bible DB Inspection")
    print("=" * 80)
    print()

    # Check books
    print("1. Books in database:")
    print("-" * 80)
    cur.execute("SELECT book_id, name, testament, chapters FROM bible.books ORDER BY book_id LIMIT 30")
    books = cur.fetchall()
    for book_id, name, testament, chapters in books:
        print(f"  {book_id:3d} {name:20s} {testament or 'N/A':4s} {chapters:3d} chapters")

    # Check if Mark exists
    print()
    print("2. Searching for 'Mark' in books:")
    print("-" * 80)
    cur.execute("SELECT book_id, name, testament FROM bible.books WHERE name ILIKE '%mark%'")
    mark_books = cur.fetchall()
    if mark_books:
        for book_id, name, testament in mark_books:
            print(f"  Found: {book_id} - {name} ({testament})")
    else:
        print("  No books found matching 'Mark'")

    # Check translation sources
    print()
    print("3. Translation sources in verses:")
    print("-" * 80)
    cur.execute(
        "SELECT DISTINCT translation_source, COUNT(*) FROM bible.verses GROUP BY translation_source ORDER BY translation_source"
    )
    sources = cur.fetchall()
    for source, count in sources:
        print(f"  {source:20s} {count:8d} verses")

    # Check verses for Mark (any translation)
    print()
    print("4. Verses for Mark (any book name containing 'Mark'):")
    print("-" * 80)
    cur.execute("""
        SELECT DISTINCT v.book_name, v.translation_source, COUNT(*) as verse_count
        FROM bible.verses v
        JOIN bible.books b ON v.book_name = b.name
        WHERE b.name ILIKE '%mark%'
        GROUP BY v.book_name, v.translation_source
        ORDER BY v.book_name, v.translation_source
    """)
    mark_verses = cur.fetchall()
    if mark_verses:
        for book_name, translation, count in mark_verses:
            print(f"  {book_name:20s} {translation:10s} {count:6d} verses")
    else:
        print("  No verses found for Mark")

    # Check Mark 1:1 specifically
    print()
    print("5. Checking Mark 1:1 specifically:")
    print("-" * 80)
    cur.execute("""
        SELECT verse_id, book_name, chapter_num, verse_num, translation_source, LEFT(text, 50) as text_preview
        FROM bible.verses
        WHERE book_name ILIKE '%mark%'
          AND chapter_num = 1
          AND verse_num = 1
        LIMIT 5
    """)
    mark_1_1 = cur.fetchall()
    if mark_1_1:
        for verse_id, book_name, chapter, verse, translation, text_preview in mark_1_1:
            print(f"  verse_id={verse_id} {book_name} {chapter}:{verse} ({translation})")
            print(f"    Text: {text_preview}...")
    else:
        print("  No Mark 1:1 found")

    # Check Greek words for any Mark verses
    print()
    print("6. Greek words for Mark (any verses):")
    print("-" * 80)
    cur.execute("""
        SELECT COUNT(DISTINCT w.word_id) as word_count, COUNT(DISTINCT w.verse_id) as verse_count
        FROM bible.greek_nt_words w
        JOIN bible.verses v ON w.verse_id = v.verse_id
        WHERE v.book_name ILIKE '%mark%'
    """)
    greek_stats = cur.fetchone()
    if greek_stats:
        word_count, verse_count = greek_stats
        print(f"  Total Greek words: {word_count}")
        print(f"  Verses with Greek words: {verse_count}")
    else:
        print("  No Greek words found for Mark")

    # Check sample Greek words
    print()
    print("7. Sample Greek words (first 10):")
    print("-" * 80)
    cur.execute("""
        SELECT w.word_id, w.verse_id, w.word_position, w.word_text, w.strongs_id,
               v.book_name, v.chapter_num, v.verse_num
        FROM bible.greek_nt_words w
        JOIN bible.verses v ON w.verse_id = v.verse_id
        LIMIT 10
    """)
    sample_words = cur.fetchall()
    if sample_words:
        for word_id, verse_id, pos, word_text, strongs, book, ch, v in sample_words:
            print(f"  word_id={word_id} {book} {ch}:{v} pos={pos} '{word_text}' {strongs or 'N/A'}")
    else:
        print("  No Greek words found in database")

    conn.close()
    print()
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
