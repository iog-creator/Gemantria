# AGENTS.md — pmagent/biblescholar

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
from pmagent.biblescholar.gematria_adapter import compute_phrase_gematria

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

Tests live in `pmagent/biblescholar/tests/test_gematria_adapter.py`.

### Gematria Flow (Phase-6K)

- **Module**: `pmagent/biblescholar/gematria_flow.py`
- **Purpose**: Read-only pipeline hook for BibleScholar to compute Gematria for
  verses (text + OSIS ref) across one or more numerics systems.
- **Dependencies**:
  - `pmagent.biblescholar.gematria_adapter`
  - `pmagent.modules.gematria.core`
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
from pmagent.biblescholar.gematria_flow import compute_verse_gematria

# Single system
summary = compute_verse_gematria("אדם", "Gen.2.7", ["mispar_hechrachi"])
assert summary.systems["mispar_hechrachi"].value == 45

# All systems (default)
summary = compute_verse_gematria("הבל", "Gen.4.2")
assert "mispar_hechrachi" in summary.systems
assert "mispar_gadol" in summary.systems
```

### Bible DB Adapter (Phase-6M)

- **Module**: `pmagent/biblescholar/bible_db_adapter.py`
- **Purpose**: Read-only adapter for accessing bible_db database. Provides verse and passage retrieval from `bible.verses` table.
- **Dependencies**:
  - `pmagent.db.loader.get_bible_engine()` (centralized DSN loader)
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

- **Module**: `pmagent/biblescholar/bible_passage_flow.py`
- **Purpose**: Simple, composable flow for retrieving verses and passages using the bible_db adapter. Provides reference string parsing and convenience functions.
- **Dependencies**:
  - `pmagent.biblescholar.bible_db_adapter`
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
from pmagent.biblescholar.bible_passage_flow import fetch_verse, fetch_passage

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
- Tests in `pmagent/biblescholar/tests/test_bible_db_adapter.py`
- Tests in `pmagent/biblescholar/tests/test_bible_passage_flow.py`
- Tests verify: SQL query shapes, DB-off handling, no write operations, reference parsing

### Lexicon Adapter (Phase-6N)

- **Module**: `pmagent/biblescholar/lexicon_adapter.py`
- **Purpose**: Read-only adapter for accessing bible_db lexicon tables (Hebrew/Greek entries). Provides Strong's number lookup and word-level data retrieval.
- **Dependencies**:
  - `pmagent.db.loader.get_bible_engine()` (centralized DSN loader)
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

- **Module**: `pmagent/biblescholar/lexicon_flow.py`
- **Purpose**: Simple, composable flow for retrieving lexicon entries and word-study data using the lexicon adapter. Provides convenience functions for Strong's number lookup and verse word studies.
- **Dependencies**:
  - `pmagent.biblescholar.lexicon_adapter`
  - `pmagent.biblescholar.bible_passage_flow` (for reference parsing)
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
from pmagent.biblescholar.lexicon_flow import fetch_lexicon_entry, fetch_word_study

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
- Tests in `pmagent/biblescholar/tests/test_lexicon_adapter.py`
- Tests in `pmagent/biblescholar/tests/test_lexicon_flow.py`
- Tests verify: SQL query shapes, DB-off handling, no write operations, Strong's number lookup, word-study retrieval

### Vector Similarity Adapter (Phase-6O)

- **Module**: `pmagent/biblescholar/vector_adapter.py`
- **Purpose**: Read-only adapter for verse vector similarity queries using pgvector. Provides semantic similarity search for finding similar verses based on embedding vectors stored in `bible.verses.embedding`.
- **Dependencies**:
  - `pmagent.db.loader.get_bible_engine()` (centralized DSN loader)
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

- **Module**: `pmagent/biblescholar/vector_flow.py`
- **Purpose**: Simple, composable flow for finding similar verses using vector similarity. Provides convenience functions for reference-based similarity search.
- **Dependencies**:
  - `pmagent.biblescholar.vector_adapter`
  - `pmagent.biblescholar.bible_passage_flow` (for reference parsing)
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
from pmagent.biblescholar.vector_flow import similar_verses_for_reference, similar_verses_for_verse_id

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
- Tests in `pmagent/biblescholar/tests/test_vector_adapter.py`
- Tests in `pmagent/biblescholar/tests/test_vector_flow.py`
- Tests verify: SQL query shapes, DB-off handling, no write operations, vector similarity calculations, reference parsing

### Reference Parser (Phase-7A)

- **Module**: `pmagent/biblescholar/reference_parser.py`
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
from pmagent.biblescholar.reference_parser import parse_reference

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
- Tests in `pmagent/biblescholar/tests/test_reference_parser.py`
- Covers: Normalization, standard/OSIS formats, ranges, error handling

### Keyword Search Flow (Phase-7D)

- **Module**: `pmagent/biblescholar/search_flow.py`
- **Purpose**: Keyword search across verses using `ILIKE` (case-insensitive).
- **Dependencies**:
  - `pmagent.biblescholar.bible_db_adapter`
- **Non-goals**:
  - No full-text search engine (simple SQL match only)
  - No semantic search (use vector flow for that)

**API**:
- `search_verses(query: str, translation: str = "KJV", limit: int = 20) -> list[VerseRecord]`
  - Validates query length (min 2 chars)
  - Delegates to `BibleDbAdapter.search_verses`

**Usage Example**:
```python
from pmagent.biblescholar.search_flow import search_verses

# Basic search
results = search_verses("beginning", "KJV", limit=5)
for verse in results:
    print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} - {verse.text}")

# Different translation
results = search_verses("love", "ESV")
```

- Tests in `pmagent/biblescholar/tests/test_bible_db_adapter.py`
- Covers: Query validation, empty results, limit handling, DB-off mode

### Contextual Insights Flow (Phase-8A)

- **Module**: `pmagent/biblescholar/insights_flow.py`
- **Purpose**: Aggregates verse data (text, lexicon, similar verses) into a unified context object and formats it for LLM consumption.
- **Dependencies**:
  - `pmagent.biblescholar.bible_passage_flow`
  - `pmagent.biblescholar.lexicon_flow`
  - `pmagent.biblescholar.vector_flow`
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
from pmagent.biblescholar.insights_flow import get_verse_context, format_context_for_llm

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

- Tests in `pmagent/biblescholar/tests/test_insights_flow.py`
- Covers: Aggregation logic, formatting output, missing data handling

### Cross-Language Flow (Phase-8B)

- **Module**: `pmagent/biblescholar/cross_language_flow.py`
- **Purpose**: Advanced word analysis and cross-language (Hebrew/Greek) connections using lexicon adapter and vector search.
- **Dependencies**:
  - `pmagent.biblescholar.lexicon_flow`
  - `pmagent.biblescholar.vector_flow`
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
from pmagent.biblescholar.cross_language_flow import analyze_word_in_context, find_cross_language_connections

# Analyze word
analysis = analyze_word_in_context("Genesis 1:1", "H7225")
print(f"{analysis.lemma}: {analysis.occurrence_count} occurrences")

# Find connections
matches = find_cross_language_connections("H7225")
for match in matches:
    print(f"Match: {match.target_lemma} ({match.target_strongs}) - Score: {match.similarity_score}")
```

**Testing**:
- Tests in `pmagent/biblescholar/tests/test_cross_language_flow.py`
- Covers: Word analysis, cross-language matching logic, error handling

### Phase 15 Wave-2: Advanced RAG Engine (Option B - Standard)

- **Status**: Implementation COMPLETE (Testing in progress)
- **Architecture Profile**: Option B (Standard) - Committed configuration
  - 5-verse context window (±2 verses from seed)
  - Cross-language lemma signals from Phase 14 `RelationshipAdapter`
  - Embedding-based scoring with reranker fallback
  - 1024-D embeddings (BGE-M3 fidelity)
  - Ketiv as primary reading for Gematria

**Modules**:

1. **`embedding_adapter.py`** - 1024-D Vector Embeddings
   - Purpose: Provides 1024-D BGE-M3 compatible embedding retrieval and vector search via pgvector
   - API:
     - `get_embedding_for_verse(verse_id: int) -> np.ndarray | None` - Retrieve 1024-D embedding
     - `compute_query_embedding(query: str) -> np.ndarray | None` - Generate query embedding (Wave-3)
     - `vector_search(query_embedding, top_k: int) -> list[tuple[int, float]]` - pgvector cosine similarity search
     - `db_status` property - Returns "available", "unavailable", or "db_off"
   - Hermetic: Returns `None`/empty list when DB unavailable
   - Tests: 7 tests in `test_embedding_adapter.py`

2. **`reranker_adapter.py`** - Cross-Encoder Reranking
   - Purpose: Mandatory reranking layer per Option B to reduce hallucination rate
   - API:
     - `rerank_chunks(chunks: list[dict], query: str) -> list[dict]` - Rerank with combined scoring
     - `lm_status` property - Returns "available", "unavailable", or "lm_off"
   - Scoring: Combined score = 0.7 * embedding_score + 0.3 * reranker_score
   - Fallback: Returns original ranking when LM unavailable (hermetic mode)
   - Tests: 8 tests in `test_reranker_adapter.py`

3. **`rag_retrieval.py`** - RAG Retrieval Orchestrator
   - Purpose: Main RAG retrieval engine integrating embeddings, reranking, and context expansion
   - API:
     - `RAGRetriever.retrieve_contextual_chunks(query: str, top_k: int) -> list[dict]`
   - Pipeline:
     1. Compute query embedding (1024-D)
     2. Vector search via pgvector
     3. Build chunks with embedding scores
     4. Apply reranker fallback (updates relevance_score)
     5. Expand context windows (5-verse, placeholder for Wave-3)
     6. Enrich with Phase 14 metadata (proper names, Greek words, cross-language hints)
   - Hermetic: Returns empty list when DB/LM unavailable
   - Tests: 1 test in `test_rag_retrieval.py` (4 skipped Test Vectors pending)

4. **`contextual_chunks.py`** - Context Window Expansion
   - Purpose: Build enriched contextual chunks with 5-verse window expansion
   - API:
     - `build_contextual_chunks(verse_ref: str) -> list[dict]` - Single verse chunk with Phase 14 enrichment
     - `expand_context_window(verse_ref: str, window_size: int = 5) -> list[dict]` - ±2 verse expansion
   - Features:
     - Integrates `RelationshipAdapter` for proper names
     - Integrates `LexiconAdapter` for Greek words
     - Cross-language lemma resolution (Greek→Hebrew hints)
     - Marks seed verse in window
   - Hermetic: Returns empty list when DB unavailable

5. **Phase 14 Adapter Batch Methods** - N+1 Query Optimization
   - `RelationshipAdapter.get_enriched_context_batch(verse_ids: list[int]) -> dict[int, EnrichedContext]`
     - Optimizes proper name retrieval for multi-verse contexts
     - Prevents N+1 query problem in 5-verse windows
   - `LexiconAdapter.get_greek_words_batch(verse_refs: list[str]) -> dict[str, list[dict]]`
     - Batch Greek word retrieval with single DB query
     - Optimizes context window queries
   - Tests: 2 tests in `test_adapter_batch_methods.py`

**Schema**:
- `docs/SSOT/rag_retrieval.schema.json` - JSON schema for RAG response format
- `docs/SSOT/PHASE15_WAVE2_SPEC.md` - Complete RAG specification

**Test Coverage**: 20 tests (7 embedding + 8 reranker + 1 RAG + 2 batch + 2 vector)

**Dependencies**:
- Phase 14 adapters (`RelationshipAdapter`, `LexiconAdapter`)
- `bible_db.verse_embeddings` table (1024-D pgvector)
- PostgreSQL with pgvector extension
- LM Studio/Ollama for reranker (optional, hermetic fallback)

**Non-goals**:
- No query embedding generation in Wave-2 (placeholder for Wave-3)
- No full context expansion in Wave-2 (metadata only)
- No live DB/LM tests yet (hermetic validation only)

## Future Extensions

- Batch processing for multiple phrases
- Comparison utilities (difference between systems)
- Integration with BibleScholar verse lookup
- Caching layer (if needed, still read-only)
- More sophisticated reference parsing (OSIS format, book abbreviations)

