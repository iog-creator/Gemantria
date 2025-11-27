# AGENTS.md — agentpm/biblescholar

## Directory Purpose

Home for BibleScholar-specific integration logic inside AgentPM, including
read-only adapters to Gematria and other core modules.

This directory must NOT perform database writes or mutate the control-plane
directly; it should provide pure, testable adapters that callers can use.

## Status

- Phase-6J: BibleScholar Gematria adapter (read-only) — COMPLETE
- Phase-6K: BibleScholar Gematria flow (read-only) — COMPLETE
- Phase-6M: Bible DB read-only adapter + passage flow — COMPLETE
- Phase-6N: Lexicon read-only adapter + word-study flow — COMPLETE
- Phase-6O: Vector similarity adapter + verse-similarity flow — COMPLETE
- Phase-13B: Multi-language support — translation_source filtering — COMPLETE

## Related SSOT Docs

- docs/SSOT/BIBLESCHOLAR_INTAKE.md
- docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md
- docs/projects/biblescholar/README.md
- docs/projects/biblescholar/ARCHITECTURE.md

## API Contract

### `gematria_adapter.compute_phrase_gematria()`

**Purpose**: Compute gematria for a Hebrew phrase or verse text in a BibleScholar-friendly format.

**Contract**:
- **Read-only**: No database writes, no control-plane mutations
- **Pure function**: Deterministic output for given inputs
- **System support**: `mispar_hechrachi` (default) and `mispar_gadol`
- **Edge cases**: Handles empty strings, None, mixed scripts, non-Hebrew text gracefully
- **OSIS refs**: Optional OSIS reference can be attached to results

**Inputs**:
- `text: str` - Hebrew text (may contain diacritics, punctuation, mixed scripts)
- `system: str` - Numerics system name (default: `mispar_hechrachi`)
- `osis_ref: str | None` - Optional OSIS reference (e.g., "Gen.4.2")

**Outputs**:
- `GematriaPhraseResult` dataclass with:
  - `text: str` - Original input text
  - `normalized: str` - Normalized Hebrew (diacritics/punctuation removed)
  - `letters: list[str]` - Extracted Hebrew letters
  - `system: str` - Numerics system used
  - `value: int` - Computed gematria value (0 if no Hebrew letters found)
  - `osis_ref: str | None` - OSIS reference if provided

**Error Handling**:
- Invalid system names raise `ValueError` with list of valid systems
- Empty/None text returns result with `value=0`, `normalized=""`, `letters=[]`
- Non-Hebrew text returns result with `value=0` (no error)

## Usage Examples

```python
from agentpm.biblescholar.gematria_adapter import compute_phrase_gematria

# Basic usage (default system: mispar_hechrachi)
result = compute_phrase_gematria("אדם")
assert result.value == 45
assert result.normalized == "אדם"
assert result.letters == ["א", "ד", "ם"]

# With OSIS reference
result = compute_phrase_gematria("הבל", osis_ref="Gen.4.2")
assert result.value == 37
assert result.osis_ref == "Gen.4.2"

# Different numerics system
result = compute_phrase_gematria("אדם", system="mispar_gadol")
# Final mem (ם) = 600 in Gadol vs 40 in Hechrachi
assert result.value == 605  # א=1, ד=4, ם=600

# Edge cases
result = compute_phrase_gematria("")  # Empty string
assert result.value == 0
assert result.normalized == ""
assert result.letters == []

result = compute_phrase_gematria("Hello 123")  # No Hebrew
assert result.value == 0
assert result.normalized == ""
assert result.letters == []

result = compute_phrase_gematria("א hello ב")  # Mixed scripts
assert result.value == 3  # א=1, ב=2
assert result.normalized == "אב"
assert result.letters == ["א", "ב"]
```

## Testing

All adapter functions must have comprehensive tests covering:
- Canonical examples (אדם=45, הבל=37)
- Both numerics systems
- Edge cases (empty, None, mixed scripts, non-Hebrew)
- OSIS reference handling
- Invalid system names

Tests live in `agentpm/biblescholar/tests/test_gematria_adapter.py`.

### Gematria Flow (Phase-6K)

- **Module**: `agentpm/biblescholar/gematria_flow.py`
- **Purpose**: Read-only pipeline hook for BibleScholar to compute Gematria for
  verses (text + OSIS ref) across one or more numerics systems.
- **Dependencies**:
  - `agentpm.biblescholar.gematria_adapter`
  - `agentpm.modules.gematria.core`
- **Non-goals**:
  - No control-plane writes.
  - No database access.
  - No LM calls.

**API**:
- `supported_gematria_systems() -> list[str]` - Returns list of supported systems
- `compute_verse_gematria(text: str, osis_ref: str, systems: Iterable[str] | None = None) -> VerseGematriaSummary`
  - Computes Gematria for a verse across specified systems (or all systems if None)
  - Returns `VerseGematriaSummary` with mapping of system -> `GematriaPhraseResult`

**Usage Example**:
```python
from agentpm.biblescholar.gematria_flow import compute_verse_gematria

# Single system
summary = compute_verse_gematria("אדם", "Gen.2.7", ["mispar_hechrachi"])
assert summary.systems["mispar_hechrachi"].value == 45

# All systems (default)
summary = compute_verse_gematria("הבל", "Gen.4.2")
assert "mispar_hechrachi" in summary.systems
assert "mispar_gadol" in summary.systems
```

### Bible DB Adapter (Phase-6M)

- **Module**: `agentpm/biblescholar/bible_db_adapter.py`
- **Purpose**: Read-only adapter for accessing bible_db database. Provides verse and passage retrieval from `bible.verses` table.
- **Dependencies**:
  - `agentpm.db.loader.get_bible_engine()` (centralized DSN loader)
  - SQLAlchemy for database queries
- **Non-goals**:
  - No database writes (SELECT-only operations)
  - No control-plane writes
  - No LM calls
  - No UI work

**API**:
- `BibleDbAdapter` class:
  - `get_verse(book_name: str, chapter_num: int, verse_num: int, translation_source: str = "KJV") -> VerseRecord | None`
  - `get_passage(book_name: str, start_chapter: int, start_verse: int, end_chapter: int, end_verse: int, translation_source: str = "KJV") -> list[VerseRecord]`
  - `db_status: Literal["available", "unavailable", "db_off"]` property

**Data Model**:
- `VerseRecord` dataclass with fields: `verse_id`, `book_name`, `chapter_num`, `verse_num`, `text`, `translation_source`

**Error Handling**:
- DB unavailable: Returns `None` for `get_verse()`, empty list for `get_passage()`
- DB off (DSN not set): Returns `None`/empty list, sets `db_status` to `"db_off"`
- Connection errors: Returns `None`/empty list, sets `db_status` to `"unavailable"`

**Bible DB Only Rule**: All biblical content answers must come from `bible_db`, not from LLM memory or other sources. This adapter enforces that by providing the only read path to biblical text.

### Bible Passage Flow (Phase-6M)

- **Module**: `agentpm/biblescholar/bible_passage_flow.py`
- **Purpose**: Simple, composable flow for retrieving verses and passages using the bible_db adapter. Provides reference string parsing and convenience functions.
- **Dependencies**:
  - `agentpm.biblescholar.bible_db_adapter`
- **Non-goals**:
  - No LM calls
  - No Gematria (handled by separate flows)
  - No UI work

**API**:
- `parse_reference(reference: str) -> tuple[str, int, int] | None` - Parse "Book Chapter:Verse" format
- `fetch_verse(reference: str, translation_source: str = "KJV", adapter: BibleDbAdapter | None = None) -> VerseRecord | None`
- `fetch_passage(reference: str, translation_source: str = "KJV", adapter: BibleDbAdapter | None = None) -> list[VerseRecord]`
  - Supports formats: "Genesis 1:1" (single), "Genesis 1:1-3" (range), "Genesis 1:1-2:3" (cross-chapter)
- `get_db_status(adapter: BibleDbAdapter | None = None) -> Literal["available", "unavailable", "db_off"]`

**Usage Example**:
```python
from agentpm.biblescholar.bible_passage_flow import fetch_verse, fetch_passage

# Single verse
verse = fetch_verse("Genesis 1:1", "KJV")
if verse:
    print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} - {verse.text}")

# Passage range
verses = fetch_passage("Genesis 1:1-3", "KJV")
for v in verses:
    print(f"{v.verse_num}: {v.text}")

# Cross-chapter passage
verses = fetch_passage("Genesis 1:31-2:3", "KJV")
```

**Testing**:
- Tests in `agentpm/biblescholar/tests/test_bible_db_adapter.py`
- Tests in `agentpm/biblescholar/tests/test_bible_passage_flow.py`
- Tests verify: SQL query shapes, DB-off handling, no write operations, reference parsing
- **Phase 13B**: Multi-translation tests added to verify translation_source filtering (KJV, ESV, ASV, YLT, TAHOT)

### Lexicon Adapter (Phase-6N)

- **Module**: `agentpm/biblescholar/lexicon_adapter.py`
- **Purpose**: Read-only adapter for accessing bible_db lexicon tables (Hebrew/Greek entries). Provides Strong's number lookup and word-level data retrieval.
- **Dependencies**:
  - `agentpm.db.loader.get_bible_engine()` (centralized DSN loader)
  - SQLAlchemy for database queries
- **Non-goals**:
  - No database writes (SELECT-only operations)
  - No control-plane writes
  - No LM calls
  - No UI work

**API**:
- `LexiconAdapter` class:
  - `get_hebrew_entry(strongs_id: str) -> LexiconEntry | None` - Get Hebrew lexicon entry by Strong's number
  - `get_greek_entry(strongs_id: str) -> LexiconEntry | None` - Get Greek lexicon entry by Strong's number
  - `get_entries_for_reference(book_name: str, chapter_num: int, verse_num: int) -> list[LexiconEntry]` - Get all lexicon entries for words in a verse
  - `db_status: Literal["available", "unavailable", "db_off"]` property

**Data Model**:
- `LexiconEntry` dataclass with fields: `entry_id`, `strongs_id`, `lemma`, `transliteration`, `definition`, `usage`, `gloss`

**Tables Used**:
- `bible.hebrew_entries` - Hebrew lexicon entries (indexed on `strongs_id`)
- `bible.greek_entries` - Greek lexicon entries (indexed on `strongs_id`)
- `bible.hebrew_ot_words` - Hebrew word-level data (links to verses via `verse_id`)
- `bible.greek_nt_words` - Greek word-level data (links to verses via `verse_id`)

**Error Handling**:
- DB unavailable: Returns `None` for entry lookups, empty list for reference queries
- DB off (DSN not set): Returns `None`/empty list, sets `db_status` to `"db_off"`
- Connection errors: Returns `None`/empty list, sets `db_status` to `"unavailable"`

**Bible DB Only Rule**: All biblical/lexical answers must come from `bible_db`, not from LLM memory or other sources. This adapter enforces that by providing the only read path to lexicon data.

### Lexicon Flow (Phase-6N)

- **Module**: `agentpm/biblescholar/lexicon_flow.py`
- **Purpose**: Simple, composable flow for retrieving lexicon entries and word-study data using the lexicon adapter. Provides convenience functions for Strong's number lookup and verse word studies.
- **Dependencies**:
  - `agentpm.biblescholar.lexicon_adapter`
  - `agentpm.biblescholar.bible_passage_flow` (for reference parsing)
- **Non-goals**:
  - No LM calls
  - No Gematria (handled by separate flows)
  - No UI work

**API**:
- `fetch_lexicon_entry(strongs_id: str) -> LexiconEntry | None` - Fetch lexicon entry by Strong's number (auto-detects Hebrew/Greek)
- `fetch_word_study(reference: str) -> WordStudyResult` - Fetch all lexicon entries for words in a verse reference
- `get_db_status(adapter: LexiconAdapter | None = None) -> Literal["available", "unavailable", "db_off"]`

**Data Model**:
- `WordStudyResult` dataclass with fields: `reference`, `entries` (list of `LexiconEntry`), `db_status`

**Usage Example**:
```python
from agentpm.biblescholar.lexicon_flow import fetch_lexicon_entry, fetch_word_study

# Single lexicon entry
entry = fetch_lexicon_entry("H1")  # Hebrew
if entry:
    print(f"{entry.strongs_id}: {entry.lemma} - {entry.gloss}")

entry = fetch_lexicon_entry("G1")  # Greek
if entry:
    print(f"{entry.strongs_id}: {entry.lemma} - {entry.definition}")

# Word study for a verse
result = fetch_word_study("Genesis 1:1")
print(f"Found {len(result.entries)} lexicon entries for {result.reference}")
for entry in result.entries:
    print(f"  {entry.strongs_id}: {entry.lemma} - {entry.gloss}")
```

**Testing**:
- Tests in `agentpm/biblescholar/tests/test_lexicon_adapter.py`
- Tests in `agentpm/biblescholar/tests/test_lexicon_flow.py`
- Tests verify: SQL query shapes, DB-off handling, no write operations, Strong's number lookup, word-study retrieval

### Vector Similarity Adapter (Phase-6O)

- **Module**: `agentpm/biblescholar/vector_adapter.py`
- **Purpose**: Read-only adapter for verse vector similarity queries using pgvector. Provides semantic similarity search for finding similar verses based on embedding vectors stored in `bible.verses.embedding`.
- **Dependencies**:
  - `agentpm.db.loader.get_bible_engine()` (centralized DSN loader)
  - SQLAlchemy for database queries
  - pgvector extension (cosine distance operator `<->`)
- **Non-goals**:
  - No database writes (SELECT-only operations)
  - No control-plane writes
  - No LM calls
  - No UI work

**API**:
- `BibleVectorAdapter` class:
  - `find_similar_by_verse(verse_id: int, limit: int = 10, translation_source: str | None = None) -> list[VerseSimilarityResult]` - Find similar verses by verse_id
  - `find_similar_by_ref(book_name: str, chapter_num: int, verse_num: int, translation_source: str = "KJV", limit: int = 10) -> list[VerseSimilarityResult]` - Find similar verses by Bible reference
  - `db_status: Literal["available", "unavailable", "db_off"]` property

**Data Model**:
- `VerseSimilarityResult` dataclass with fields: `verse_id`, `book_name`, `chapter_num`, `verse_num`, `text`, `translation_source`, `similarity_score` (0.0 to 1.0, higher is more similar)

**Tables Used**:
- `bible.verse_embeddings` - Embedding storage with `embedding vector(1024)` column (1024-dim, BGE-M3 compatible)
- `bible.verses` - Verse text storage (joined with verse_embeddings to get text and metadata)

**Vector Similarity**:
- Uses pgvector's cosine distance operator `<->` for similarity calculations
- Similarity score: `1 - (embedding <-> source_embedding)` (converts distance to similarity, 0.0 to 1.0)
- Results ordered by similarity (highest first)
- Requires `embedding IS NOT NULL` for both source and target verses
- Uses 1024-dimensional embeddings from `verse_embeddings` table (BGE-M3 compatible)

**Error Handling**:
- DB unavailable: Returns empty list
- DB off (DSN not set): Returns empty list, sets `db_status` to `"db_off"`
- Connection errors: Returns empty list, sets `db_status` to `"unavailable"`
- Verse not found or no embedding: Returns empty list

**Bible DB Only Rule**: All verse similarity queries must come from `bible_db` embeddings, not from LLM memory or other sources. This adapter enforces that by providing the only read path to vector similarity data.

### Vector Similarity Flow (Phase-6O)

- **Module**: `agentpm/biblescholar/vector_flow.py`
- **Purpose**: Simple, composable flow for finding similar verses using vector similarity. Provides convenience functions for reference-based similarity search.
- **Dependencies**:
  - `agentpm.biblescholar.vector_adapter`
  - `agentpm.biblescholar.bible_passage_flow` (for reference parsing)
- **Non-goals**:
  - No LM calls
  - No Gematria (handled by separate flows)
  - No UI work

**API**:
- `similar_verses_for_reference(reference: str, translation_source: str = "KJV", limit: int = 10) -> list[VerseSimilarityResult]` - Find similar verses for a Bible reference
- `similar_verses_for_verse_id(verse_id: int, limit: int = 10) -> list[VerseSimilarityResult]` - Find similar verses by verse_id
- `get_db_status(adapter: BibleVectorAdapter | None = None) -> Literal["available", "unavailable", "db_off"]`

**Usage Example**:
```python
from agentpm.biblescholar.vector_flow import similar_verses_for_reference, similar_verses_for_verse_id

# Find similar verses by reference
similar = similar_verses_for_reference("Genesis 1:1", "KJV", limit=5)
for verse in similar:
    print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} (score: {verse.similarity_score:.3f})")
    print(f"  {verse.text}")

# Find similar verses by verse_id
similar = similar_verses_for_verse_id(verse_id=1, limit=10)
for verse in similar:
    print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} - {verse.similarity_score:.3f}")
```

**Testing**:
- Tests in `agentpm/biblescholar/tests/test_vector_adapter.py`
- Tests in `agentpm/biblescholar/tests/test_vector_flow.py`
- Tests verify: SQL query shapes, DB-off handling, no write operations, vector similarity calculations, reference parsing

### Reference Parser (Phase-7A)

- **Module**: `agentpm/biblescholar/reference_parser.py`
- **Purpose**: Pure-function parser for Bible references. Supports standard formats ("John 3:16"), verse ranges ("Gen 1:1-5"), and OSIS format ("Gen.1.1"). Replaces legacy `bible_reference_parser.py`.
- **Dependencies**: None (Pure Python)
- **Non-goals**:
  - No database access
  - No validation against book existence (normalization only)

**API**:
- `ParsedReference` dataclass:
  - `book: str` (Normalized abbreviation, e.g., "Gen")
  - `chapter: int`
  - `verse: int | None`
  - `end_verse: int | None`
  - `translation: str` (Default "KJV")
- `parse_reference(ref: str) -> ParsedReference`
- `normalize_book_name(book_name: str) -> str`

**Usage Example**:
```python
from agentpm.biblescholar.reference_parser import parse_reference

# Standard format
ref = parse_reference("John 3:16")
assert ref.book == "Joh"
assert ref.chapter == 3
assert ref.verse == 16

# Verse range
ref = parse_reference("Gen 1:1-5")
assert ref.book == "Gen"
assert ref.chapter == 1
assert ref.verse == 1
assert ref.end_verse == 5

# OSIS format
ref = parse_reference("Gen.1.1")
assert ref.book == "Gen"

# Numbered books
ref = parse_reference("1 Corinthians 13:4")
assert ref.book == "1Co"
```

**Testing**:
- Tests in `agentpm/biblescholar/tests/test_reference_parser.py`
- Covers: Normalization, standard/OSIS formats, ranges, error handling

### Keyword Search Flow (Phase-7D)

- **Module**: `agentpm/biblescholar/search_flow.py`
- **Purpose**: Keyword search across verses using `ILIKE` (case-insensitive).
- **Dependencies**:
  - `agentpm.biblescholar.bible_db_adapter`
- **Non-goals**:
  - No full-text search engine (simple SQL match only)
  - No semantic search (use vector flow for that)

**API**:
- `search_verses(query: str, translation: str, limit: int = 20) -> list[VerseRecord]`
  - **translation**: Required translation identifier (e.g., "KJV", "ESV", "ASV", "YLT")
  - Validates query length (min 2 chars)
  - Delegates to `BibleDbAdapter.search_verses`

**Usage Example**:
```python
from agentpm.biblescholar.search_flow import search_verses

# Basic search (translation is required)
results = search_verses("beginning", "KJV", limit=5)
for verse in results:
    print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} - {verse.text}")

# Different translation
results = search_verses("love", "ESV")
```

- Tests in `agentpm/biblescholar/tests/test_bible_db_adapter.py`
- Covers: Query validation, empty results, limit handling, DB-off mode

### Contextual Insights Flow (Phase-8A)

- **Module**: `agentpm/biblescholar/insights_flow.py`
- **Purpose**: Aggregates verse data (text, lexicon, similar verses) into a unified context object and formats it for LLM consumption.
- **Dependencies**:
  - `agentpm.biblescholar.bible_passage_flow`
  - `agentpm.biblescholar.lexicon_flow`
  - `agentpm.biblescholar.vector_flow`
- **Non-goals**:
  - No direct LLM calls (formatting only)

**API**:
- `VerseContext` dataclass:
  - `reference: str`
  - `primary_text: str` (KJV)
  - `secondary_texts: dict[str, str]`
  - `lexicon_entries: list[LexiconEntry]`
  - `similar_verses: list[VerseSimilarityResult]`
- `get_verse_context(ref: str, translations: list[str], include_lexicon: bool, include_similar: bool) -> VerseContext`
- `format_context_for_llm(context: VerseContext) -> str`

**Usage Example**:
```python
from agentpm.biblescholar.insights_flow import get_verse_context, format_context_for_llm

# Get full context
context = get_verse_context("Genesis 1:1", translations=["ESV"])

# Format for LLM
prompt_context = format_context_for_llm(context)
print(prompt_context)
# Output:
# # Context: Genesis 1:1
# ## Text (KJV)
# > In the beginning...
# ...
```

- Tests in `agentpm/biblescholar/tests/test_insights_flow.py`
- Covers: Aggregation logic, formatting output, missing data handling

### Passage Commentary Service (Phase-9A)

- **Module**: `agentpm/biblescholar/passage.py`
- **Purpose**: Provides passage lookup with theology-aware commentary using enriched context (lexicon + similar verses) and the Christian Bible Expert model.
- **Dependencies**:
  - `agentpm.biblescholar.bible_passage_flow` (passage retrieval)
  - `agentpm.biblescholar.insights_flow` (enriched context gathering)
  - `agentpm.adapters.theology` (Christian Bible Expert model)
- **Fail-closed**: No fallbacks allowed. Raises `ValueError` if `use_lm=False` or no verses found. Raises `RuntimeError` if theology model unavailable.

**API**:
- `fetch_passage_dict(reference: str, translation_source: str = "KJV") -> dict[str, Any]` - Fetch passage from bible_db
- `generate_commentary(passage: dict[str, Any], *, use_lm: bool = True) -> dict[str, Any]` - Generate commentary with enriched context
- `get_passage_and_commentary(reference: str, *, use_lm: bool = True, translation_source: str = "KJV") -> dict[str, Any]` - Combined passage + commentary

**Enriched Context Flow**:
1. Find passage in bible_db ✓
2. Semantic check: Find similar verses via vector search ✓
3. Pull information: Gather lexicon entries (word study) ✓
4. Format enriched context for LLM ✓
5. Pass to Christian Bible Expert model for synthesis ✓

**Error Handling**:
- `use_lm=False`: Raises `ValueError` (fallbacks not allowed)
- No verses found: Raises `ValueError` (fail-closed)
- Theology model unavailable: Raises `RuntimeError` (fail-closed via `theology_chat()`)

**Usage Example**:
```python
from agentpm.biblescholar.passage import get_passage_and_commentary

# Get passage with AI commentary (enriched context)
result = get_passage_and_commentary("Genesis 5:5", use_lm=True)
print(f"Reference: {result['reference']}")
print(f"Verses: {len(result['verses'])}")
print(f"Commentary source: {result['commentary']['source']}")  # Always "lm_theology"
print(f"Commentary: {result['commentary']['text']}")
```

**Testing**:
- Tests in `agentpm/biblescholar/tests/test_passage.py`
- Covers: Passage retrieval, enriched context gathering, theology model integration, fail-closed behavior

### Cross-Language Flow (Phase-8B)

- **Module**: `agentpm/biblescholar/cross_language_flow.py`
- **Purpose**: Advanced word analysis and cross-language (Hebrew/Greek) connections using lexicon adapter and vector search.
- **Dependencies**:
  - `agentpm.biblescholar.lexicon_flow`
  - `agentpm.biblescholar.vector_flow`
- **Non-goals**:
  - No full semantic mapping (heuristic based on vector similarity)

**API**:
- `WordAnalysis` dataclass:
  - `strongs_id`, `lemma`, `gloss`, `occurrence_count`, `related_verses`
- `CrossLanguageMatch` dataclass:
  - `source_strongs`, `target_strongs`, `target_lemma`, `similarity_score`, `common_verses`
- `analyze_word_in_context(ref: str, strongs_id: str) -> WordAnalysis`
- `find_cross_language_connections(strongs_id: str, reference: str, limit: int) -> list[CrossLanguageMatch]`

**Usage Example**:
```python
from agentpm.biblescholar.cross_language_flow import analyze_word_in_context, find_cross_language_connections

# Analyze word
analysis = analyze_word_in_context("Genesis 1:1", "H7225")
print(f"{analysis.lemma}: {analysis.occurrence_count} occurrences")

# Find connections
matches = find_cross_language_connections("H7225")
for match in matches:
    print(f"Match: {match.target_lemma} ({match.target_strongs}) - Score: {match.similarity_score}")
```

**Testing**:
- Tests in `agentpm/biblescholar/tests/test_cross_language_flow.py`
- Covers: Word analysis, cross-language matching logic, error handling

## Future Extensions

- Batch processing for multiple phrases
- Comparison utilities (difference between systems)
- Integration with BibleScholar verse lookup
- Caching layer (if needed, still read-only)
- More sophisticated reference parsing (OSIS format, book abbreviations)

