# Cross-Project Schema Registry

This directory contains validated schemas from all sibling projects in the Gemantria ecosystem, organized for GPT/AI agent context and integration planning.

## Purpose

Provide comprehensive schema documentation across all projects to enable:
- **Context understanding**: GPT agents can see all data models
- **Integration planning**: Design adapters and migration paths
- **Schema compatibility**: Identify differences and alignment opportunities
- **Unification planning**: Plan unified data models (RFC-081)

## Directory Structure

```
share/schemas/
├── SCHEMA_REGISTRY.md          # This file
├── biblescholar/               # BibleScholarProjectClean schemas
│   ├── bible_db_structure.sql
│   ├── bible_db_verses_structure.sql
│   ├── bible_db_versification_structure.sql
│   ├── README.md
│   └── SCHEMA_INDEX.md
└── storymaker/                 # StoryMaker schemas (if any)
```

## Projects

### BibleScholarProjectClean

**Location**: `/home/mccoy/Projects/BibleScholarProjectClean`

**Database**: `bible_db` (PostgreSQL 16.6)

**Key Schemas**:
- `bible` schema - Main biblical data
- `public` schema - LangChain integration

**Core Tables**:
- `bible.verses` - Verse text with vector(768) embeddings
- `bible.hebrew_ot_words` - Hebrew word-level data
- `bible.greek_nt_words` - Greek word-level data
- `bible.verse_embeddings` - Separate vector(1024) embeddings
- `bible.hebrew_entries` / `bible.greek_entries` - Lexicon entries
- `bible.versification_mappings` - Cross-reference mappings

**See**: `biblescholar/SCHEMA_INDEX.md` for complete documentation

### StoryMaker

**Location**: `/home/mccoy/Projects/StoryMaker`

**Status**: Schema extraction pending

**Note**: StoryMaker may use different data storage (JSON files, in-memory, etc.)

### Gemantria.v2

**Location**: `/home/mccoy/Projects/Gemantria.v2`

**Database**: `gematria` (PostgreSQL)

**Key Schemas**:
- `gematria` schema - Main application data
- `public` schema - Control plane, AI tracking

**Core Tables**:
- `gematria.concepts` - Hebrew nouns with gematria values
- `gematria.concept_relations` - Graph edges
- `gematria.concept_network` - Vector embeddings (vector(1024))
- `gematria.concept_centrality` - Graph metrics

**Schema Files**: See `schemas/` directory in Gemantria.v2 root

## Schema Comparison

### Vector Embeddings

| Project | Dimension | Storage | Index Type |
|---------|-----------|---------|------------|
| BibleScholar | 768, 1024 | `verses.embedding`, `verse_embeddings.embedding` | HNSW, IVFFlat |
| Gemantria | 1024 | `concept_network.embedding` | HNSW |

### Verse/Concept References

| Project | Format | Storage |
|---------|--------|---------|
| BibleScholar | `book_name, chapter_num, verse_num` | Separate columns |
| Gemantria | OSIS format (e.g., "Gen.2.7") | Text field |

### Hebrew Text

| Project | Normalization | Storage |
|---------|---------------|---------|
| BibleScholar | Raw + transliteration | `word_text`, `transliteration` |
| Gemantria | ADR-002 (NFKD → strip → NFC) | `hebrew_text` |

## Integration Patterns

### BibleScholar → Gemantria Adapter

1. **Verse Lookup**: Query `bible.verses` by OSIS reference
2. **Hebrew Extraction**: Join `bible.hebrew_ot_words` for word-level data
3. **Gematria Calculation**: Use Gemantria's `agentpm.modules.gematria` module
4. **Storage**: Write to `gematria.concepts` with computed values

### Common Identifiers

- **Strong's Numbers**: Present in both (Hebrew: H####, Greek: G####)
- **OSIS References**: Can be derived from BibleScholar's `book_name, chapter_num, verse_num`
- **Verse IDs**: Different (Integer vs UUID), need mapping

## Usage for GPT/AI Agents

When working on integration tasks:

1. **Read relevant schema files** from this directory
2. **Understand data model differences** using comparison tables
3. **Design adapter layers** that bridge schema differences
4. **Plan migration paths** considering data volume and relationships
5. **Ensure compatibility** with existing Gemantria schemas

## Maintenance

- **Update frequency**: When schemas change in source projects
- **Extraction method**: Manual copy from source project `database/` or `schemas/` directories
- **Validation**: Verify schemas match actual database structure
- **Documentation**: Update SCHEMA_INDEX.md files when schemas change

## Related Documentation

- `docs/projects/biblescholar/README.md` - BibleScholar project overview
- `docs/projects/storymaker/README.md` - StoryMaker project overview
- `docs/rfcs/RFC-081-unified-ui-and-biblescholar-module.md` - Unification architecture
- `docs/SSOT/BIBLESCHOLAR_INTAKE.md` - Integration planning
- `schemas/README.md` - Gemantria.v2 schema documentation

## Notes

- **Not in SHARE_MANIFEST.json**: These schema files are for GPT context only, not part of the standard share manifest
- **Read-only reference**: These are documentation/reference files, not executable schemas
- **Source of truth**: Actual schemas live in their respective project repositories
