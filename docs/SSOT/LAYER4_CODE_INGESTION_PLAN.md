# Layer 4: Code Ingestion & Embeddings — Implementation Plan

**Status:** ✅ Implemented (Phases 4.1-4.5 Complete)

**Context:** Extending Layer 3 (PDF ingestion) to codebase

**Canonical Doc:** `docs/SSOT/LAYER4_CODE_INGESTION_PLAN.md`

**Scale:** ~15,071 code files discovered → subset as `kb_candidate=true`

**Date:** 2025-01-30

## Executive Summary

Layer 4 extends the DMS (Document Management System) from docs/PDFs to the entire codebase, making 15,071+ Python and TypeScript files LM-queryable through pgvector semantic search. This enables MCP tools to answer "find code that does X" queries and allows the AI librarian to surface relevant code for PM planning.

## Implementation Status

### ✅ Phase 4.1: Code Discovery (Complete)

**Files Modified:**
- `scripts/governance/ingest_docs_to_db.py` - Added `iter_code_files()` with tiered discovery
- `pyproject.toml` - Added `pathspec>=0.11.0` dependency

**Features:**
- Tiered discovery (Tier 1: pmagent/, scripts/; Tier 2: pmagent/, tests/; Tier 3: rest)
- Exclusion patterns from `.gitignore` + explicit patterns
- `--tier`, `--target-dirs`, `--limit` flags
- `--include-code` flag to enable code discovery

**Usage:**
```bash
# Discover Tier 1 code files (pmagent/, scripts/)
python scripts/governance/ingest_docs_to_db.py --include-code --tier 1 --dry-run

# Discover specific directories
python scripts/governance/ingest_docs_to_db.py --include-code --target-dirs pmagent/kb scripts/kb --dry-run
```

### ✅ Phase 4.2: AST-Based Code Fragmentation (Complete)

**Files Modified:**
- `scripts/governance/ingest_doc_content.py` - Added `chunk_python_code()` and `chunk_typescript_code()`

**Features:**
- Python: AST-based fragmentation (functions, classes, imports, constants)
- TypeScript: Regex-based fragmentation (export functions, classes, constants, imports)
- Docstring preservation via `ast.get_docstring()`
- Metadata extraction (function_name, lineno, has_docstring, etc.)

**Fragment Types:**
- `function` - Python functions or TypeScript export functions
- `class` - Python classes or TypeScript export classes
- `import` - Import statements
- `constant` - Module-level constants
- `module` - Fallback for files with no semantic units

**Usage:**
```bash
# Ingest code fragments (after discovery)
python scripts/governance/ingest_doc_content.py --all-docs --limit 10
```

### ✅ Phase 4.3: Code Embeddings (Reuse Existing)

**Status:** Existing embedding pipeline (`scripts/governance/ingest_doc_embeddings.py`) works with code fragments.

**Note:** IVFFlat index migration (`049_add_embedding_ivfflat_index.sql`) is deferred until ≥1000 embeddings exist (per plan).

**Usage:**
```bash
# Generate embeddings for code fragments
python scripts/governance/ingest_doc_embeddings.py --all-docs
```

### ✅ Phase 4.4: AI Classification (Complete)

**Files Modified:**
- `pmagent/kb/classify.py` - Added `classify_code_fragment()` function
- `scripts/governance/classify_fragments.py` - Added `--code-only` flag

**Features:**
- Code-specific classification prompt (subsystem, code_role, importance, etc.)
- Usage frequency heuristic (high: pmagent/, scripts/; medium: pmagent/, tests/; low: rest)
- Control-plane tracking via `_write_agent_run()` (reuses Phase 3.1 pattern)

**Classification Fields:**
- `subsystem`: "pm" | "ops" | "biblescholar" | "gematria" | "webui" | "general"
- `code_role`: "adapter" | "flow" | "util" | "test" | "config" | "ui_component" | "other"
- `importance`: "core" | "supporting" | "nice_to_have"
- `phase_relevance`: Array of phase names
- `should_archive`: Boolean
- `kb_candidate`: Boolean
- `usage_freq`: "high" | "medium" | "low" (heuristic-based)

**Usage:**
```bash
# Classify code fragments
python scripts/governance/classify_fragments.py --code-only --limit 10
```

### ✅ Phase 4.5: KB Registry & Search (Complete)

**Files Created:**
- `pmagent/kb/search.py` - Semantic code search via pgvector

**Files Modified:**
- `scripts/kb/build_kb_registry.py` - Extended to include code files (already supports CODE::*)
- `pmagent/cli.py` - Added `pmagent kb search` command

**Features:**
- Semantic code search using pgvector cosine similarity
- Subsystem filtering (e.g., `--subsystem=gematria`)
- Returns top-k results with scores and metadata

**Usage:**
```bash
# Search code
pmagent kb search "Hebrew gematria calculation" --subsystem=gematria

# Refresh KB registry (includes code files)
pmagent kb refresh
```

## Workflow

### Complete End-to-End Workflow

1. **Discover code files:**
   ```bash
   python scripts/governance/ingest_docs_to_db.py --include-code --tier 1
   ```

2. **Fragment code:**
   ```bash
   python scripts/governance/ingest_doc_content.py --all-docs
   ```

3. **Generate embeddings:**
   ```bash
   python scripts/governance/ingest_doc_embeddings.py --all-docs
   ```

4. **Classify fragments:**
   ```bash
   python scripts/governance/classify_fragments.py --code-only
   ```

5. **Build KB registry:**
   ```bash
   pmagent kb refresh
   ```

6. **Search code:**
   ```bash
   pmagent kb search "Hebrew gematria calculation"
   ```

## Gotchas Addressed

1. ✅ **Scale Risk**: Tiered rollout mitigates 753K fragment risk
2. ✅ **File Exclusions**: `.gitignore` parsing + explicit patterns
3. ✅ **TypeScript Parser**: Regex-based fallback (no AST dependency)
4. ✅ **Code Embedding Model**: BGE-M3 fallback (code-specific model deferred)
5. ✅ **Control-Plane Tracking**: Reuses `_write_agent_run()` pattern from Phase 3.1
6. ✅ **Docstring Preservation**: AST extracts and includes docstrings
7. ✅ **Usage Frequency**: Heuristic-based (directory-based, not git log)
8. ✅ **BibleScholar Integration**: Search command enables multilingual queries

## Known Limitations

1. **TypeScript fragmentation** is regex-based (not AST) - may miss edge cases
2. **Usage frequency** is heuristic (not git log) - approximate only
3. **Code embedding model** is text-focused (not code-tuned) - may affect search quality
4. **IVFFlat index** requires >1000 rows to be effective - seed Tier 1 first

## Next Steps

1. **Benchmark code search quality** - Test queries like "Hebrew gematria calculation" and verify top-10 recall >70%
2. **Create IVFFlat index** - After ≥1000 embeddings exist, run migration `049_add_embedding_ivfflat_index.sql`
3. **Expand to Tier 2/3** - Once Tier 1 is validated, expand to pmagent/, tests/, and TypeScript files
4. **Research code-specific embedding models** - Evaluate Salesforce/codet5-base or microsoft/codebert-base for future migration

## Phase 4.6: Future AI-Assisted Governance

**Status:** Planned

**Objective:**
Evolve "Self-Healing" from simple logic (e.g., pruning missing files) to AI-driven inference and reranking.

**Features:**
- **AI Reranking:** Granite AI assistant to re-rank search results based on user intent and semantic context, not just cosine similarity.
- **Smart Pruning:** AI agent to detect obsolete documentation not just by file presence, but by semantic staleness (e.g., "This doc refers to Phase 25 which is deprecated").
- **Inference Layer:** Integrate Granite model to suggest "Next Best Action" for governance failures (e.g., suggest specific `ingest` commands or Manifest edits).

**Dependencies:**
- Layer 4 Code Ingestion (Complete)
- Knowledge MCP (Phase 27)
- Granite Model Integration (Future)


## Related Documentation

- Layer 3 Plan: `docs/SSOT/LAYER3_AI_DOC_INGESTION_PLAN.md`
- DMS Schema: `migrations/047_control_doc_content_schema.sql`
- KB Registry: `pmagent/kb/registry.py`
- Search Implementation: `pmagent/kb/search.py`

