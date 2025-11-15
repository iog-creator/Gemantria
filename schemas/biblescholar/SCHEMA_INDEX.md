# BibleScholar Project — Schema Index

This directory contains validated database schemas extracted from the BibleScholarProjectClean repository for reference and integration planning.

## Purpose

These schemas document the actual database structure used in BibleScholarProjectClean, providing GPT/AI agents with the context needed to:
- Understand the data model
- Plan integration with Gemantria.v2
- Design migration paths
- Ensure schema compatibility

## Files

### SQL Schema Files

1. **`bible_db_structure.sql`** (930 lines)
   - Complete PostgreSQL database schema dump
   - Includes all tables, indexes, constraints, foreign keys
   - Schema: `bible` (main schema)
   - Tables:
     - `books` - Bible book metadata
     - `verses` - Verse text with embeddings (vector(768))
     - `hebrew_ot_words` - Hebrew Old Testament words
     - `greek_nt_words` - Greek New Testament words
     - `hebrew_entries` - Hebrew lexicon entries
     - `greek_entries` - Greek lexicon entries
     - `hebrew_morphology_codes` - Hebrew morphology definitions
     - `greek_morphology_codes` - Greek morphology definitions
     - `verse_embeddings` - Vector embeddings (vector(1024)) for semantic search
     - `verse_word_links` - Links between verses and words
     - `book_abbreviations` - Book name abbreviations
     - `proper_names` - Proper name entries
     - `versification_mappings` - Cross-reference mappings
     - `tahot_verses_staging` - Staging table
   - LangChain tables (public schema):
     - `langchain_pg_collection` - LangChain collection metadata
     - `langchain_pg_embedding` - LangChain embeddings storage

2. **`bible_db_verses_structure.sql`** (120 lines)
   - Focused schema for verses table
   - Includes indexes and constraints specific to verses
   - Vector embedding index (HNSW)

3. **`bible_db_versification_structure.sql`** (94 lines)
   - Versification mapping table structure
   - Cross-reference system mappings

4. **`README.md`**
   - Original database documentation from BibleScholarProjectClean
   - Setup instructions, schema overview, maintenance notes

## Key Schema Details

### Database: `bible_db`
- **PostgreSQL version**: 16.6
- **Extensions**: `vector` (pgvector) for embeddings
- **Main schema**: `bible`
- **Public schema**: LangChain integration tables

### Core Tables

#### `bible.verses`
- Primary verse storage
- Fields: `verse_id`, `book_name`, `chapter_num`, `verse_num`, `text`, `translation_source`
- Vector embedding: `embedding vector(768)` with HNSW index
- Unique constraint: `(book_name, chapter_num, verse_num, translation_source)`

#### `bible.hebrew_ot_words`
- Hebrew word-level data from Old Testament
- Links to verses via `verse_id`
- Fields: `word_text`, `strongs_id`, `grammar_code`, `transliteration`, `gloss`, `theological_term`
- Indexed on `verse_id` and `strongs_id`

#### `bible.greek_nt_words`
- Greek word-level data from New Testament
- Similar structure to Hebrew words
- Links to verses via `verse_id`

#### `bible.verse_embeddings`
- Separate embeddings table (vector(1024))
- Used for semantic search
- Indexed with IVFFlat for similarity search
- Links to verses via `verse_id`

#### `bible.hebrew_entries` / `bible.greek_entries`
- Lexicon entries with Strong's numbers
- Definitions, usage notes, glosses
- Unique constraint on `strongs_id` for Hebrew

### Vector Embeddings

- **Verse embeddings**: `vector(768)` stored in `verses.embedding` column
- **Separate embeddings**: `vector(1024)` in `verse_embeddings` table
- **Indexes**: HNSW for verses, IVFFlat for verse_embeddings
- **LangChain embeddings**: `vector(1024)` in `langchain_pg_embedding` table

### Foreign Key Relationships

```
bible.books (book_id)
  └── bible.verses (book_name → books.name)
       ├── bible.hebrew_ot_words (verse_id → verses.verse_id)
       ├── bible.greek_nt_words (verse_id → verses.verse_id)
       ├── bible.verse_embeddings (verse_id → verses.verse_id)
       └── bible.verse_word_links (verse_id → verses.verse_id)
```

## Integration Notes

### For Gemantria.v2 Integration

1. **Read-only access**: BibleScholar uses `bible_db` as read-only source
2. **Vector compatibility**: Both use pgvector, but different dimensions (768 vs 1024)
3. **Verse references**: OSIS format compatibility needed
4. **Hebrew text**: Normalization may differ from Gemantria's ADR-002 standard
5. **Strong's numbers**: Common identifier for cross-referencing

### Schema Differences from Gemantria.v2

| Aspect | BibleScholar | Gemantria.v2 |
|--------|-------------|--------------|
| Database | `bible_db` | `gematria` |
| Schema | `bible` | `gematria` |
| Verse ID | Integer | UUID |
| Embedding dim | 768/1024 | 1024 |
| Hebrew storage | Separate words table | In concepts table |
| Gematria | Not stored | Core feature |

## Usage

These schemas are provided for:
- **Reference**: Understanding BibleScholar's data model
- **Integration planning**: Designing adapter layers
- **Migration design**: Planning data flow from BibleScholar to Gemantria
- **GPT context**: Giving AI agents full schema understanding

## Source

- **Repository**: `/home/mccoy/Projects/BibleScholarProjectClean`
- **Extracted**: 2025-11-15
- **Version**: Current production schema
- **Format**: PostgreSQL pg_dump output

## Related Documentation

- `docs/projects/biblescholar/README.md` - Project overview
- `docs/projects/biblescholar/ARCHITECTURE.md` - System architecture
- `docs/SSOT/BIBLESCHOLAR_INTAKE.md` - Integration planning
- `docs/rfcs/RFC-081-unified-ui-and-biblescholar-module.md` - Unification RFC

