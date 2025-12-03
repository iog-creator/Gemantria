#!/usr/bin/env python3
"""
Ingest nouns from Bible DB into `concepts` and `verse_noun_occurrences`.
This hydrates the canonical database with Bible data, enabling the `v_concepts_with_verses` view.
"""

import os
import sys
import psycopg
from collections import defaultdict

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.infra.env_loader import ensure_env_loaded
from src.infra.db_utils import get_connection_dsn
from scripts.config.env import get_bible_db_dsn

ensure_env_loaded()

def calculate_gematria(word):
    """Simple standard gematria calculation."""
    gematria_map = {
        "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
        "י": 10, "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50,
        "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90, "ק": 100, "ר": 200,
        "ש": 300, "ת": 400
    }
    return sum(gematria_map.get(char, 0) for char in word)

def ingest_nouns():
    bible_dsn = get_bible_db_dsn()
    gematria_dsn = get_connection_dsn("GEMATRIA_DSN")

    print(f"Reading from Bible DB...")
    
    # 1. Extract Nouns from Bible DB
    with psycopg.connect(bible_dsn) as bible_conn:
        with bible_conn.cursor() as cur:
            # Set search path
            cur.execute('SET search_path TO bible, public')
            
            # Query for nouns (H% grammar code)
            cur.execute("""
                SELECT 
                    v.book_name, v.chapter_num, v.verse_num, 
                    t.word_text as surface, l.lemma, t.strongs_id
                FROM verses v
                JOIN hebrew_ot_words t ON v.verse_id = t.verse_id
                JOIN hebrew_entries l ON l.strongs_id = t.strongs_id
                WHERE (t.grammar_code LIKE 'H%/N%' OR t.grammar_code LIKE 'HN%')
                AND t.grammar_code NOT LIKE '%/V%'
                ORDER BY v.verse_id, t.word_position
            """)
            rows = cur.fetchall()
            print(f"Found {len(rows)} noun occurrences.")

    # 2. Process Data
    concepts_map = {} # lemma -> {data}
    occurrences = [] # (lemma, book, chapter, verse, position)

    for r in rows:
        book, chapter, verse, surface, lemma, strongs = r
        
        # Calculate position
        position = (chapter * 1000) + verse
        
        if lemma not in concepts_map:
            # Use surface for Hebrew and Gematria (since lemma is English)
            # Note: This might include prefixes/suffixes from the first occurrence
            print(f"🔥🔥🔥 LOUD HINT [data.bible_lemma_english]: Bible DB 'lemma' column contains English definitions. Using surface form for Hebrew text & Gematria. 🔥🔥🔥", file=sys.stderr)
            concepts_map[lemma] = {
                "name": lemma,
                "hebrew_text": surface, 
                "gematria_value": calculate_gematria(surface),
                "book_source": book,
                "primary_verse": f"{book} {chapter}:{verse}",
                "strong_number": strongs,
                "english_meaning": "Biblical Noun" # Placeholder
            }
        
        occurrences.append({
            "lemma": lemma,
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "position": position
        })

    print(f"Identified {len(concepts_map)} unique concepts.")

    # 3. Insert into Gematria DB
    with psycopg.connect(gematria_dsn) as conn:
        with conn.cursor() as cur:
            # A. Insert Concepts
            print("Inserting concepts...")
            inserted_count = 0
            lemma_to_id = {}
            
            for lemma, data in concepts_map.items():
                # Check if exists
                cur.execute("SELECT id FROM concepts WHERE name = %s", (lemma,))
                res = cur.fetchone()
                
                if res:
                    lemma_to_id[lemma] = res[0]
                else:
                    cur.execute("""
                        INSERT INTO concepts 
                        (name, hebrew_text, gematria_value, book_source, primary_verse, strong_number, english_meaning, insights, theological_significance)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, '', '')
                        RETURNING id
                    """, (
                        data["name"], data["hebrew_text"], data["gematria_value"], 
                        data["book_source"], data["primary_verse"], data["strong_number"],
                        data["english_meaning"]
                    ))
                    lemma_to_id[lemma] = cur.fetchone()[0]
                    inserted_count += 1
            
            print(f"Inserted {inserted_count} new concepts. Total mapped: {len(lemma_to_id)}")

            # B. Insert Occurrences
            print("Inserting occurrences...")
            occ_count = 0
            
            # Batch insert for performance? Doing simple loop for safety/simplicity first.
            # Truncate occurrences first to avoid dupes? No, use ON CONFLICT if possible, 
            # but table has no unique constraint on (concept_id, position)?
            # Let's check constraints. 
            # "verse_noun_occurrences_pkey" PRIMARY KEY, btree (id)
            # No unique constraint on content.
            # We should probably clear table for clean slate or check existence.
            # For now, let's just insert.
            
            for occ in occurrences:
                concept_id = lemma_to_id.get(occ["lemma"])
                if not concept_id:
                    continue
                    
                cur.execute("""
                    INSERT INTO verse_noun_occurrences
                    (concept_id, bible_book_name, bible_chapter, bible_verse_num, occurrence_position)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    concept_id, occ["book"], occ["chapter"], occ["verse"], occ["position"]
                ))
                occ_count += 1
                
            print(f"Inserted {occ_count} occurrences.")
            
        conn.commit()

if __name__ == "__main__":
    ingest_nouns()
