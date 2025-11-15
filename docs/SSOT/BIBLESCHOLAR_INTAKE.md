# BibleScholar Intake — Unification Planning

This document tracks what we intend to port from BibleScholar-related projects
into the unified Gemantria.v2 framework.

## 1. Source projects

Initial candidates (from PROJECTS_INVENTORY):

- `BibleScholarProjectClean`

- `Gemantria` (older)

- `RippleAGI` (Bible-related mentions)

## 2. High-value modules / features

### Core Domain Modules (BibleScholarLangChain/src/)

- [ ] **Database layer** (`src/database/`):
  - [ ] `database.py` - Database connection and models
  - [ ] `secure_connection.py` - Secure DB connection handling
  - [ ] `langchain_integration.py` - LangChain integration for AI workflows

- [ ] **API layer** (`src/api/`):
  - [ ] `api_app.py` - RESTful API server (Flask)
  - [ ] `comprehensive_search.py` - Comprehensive Bible search functionality
  - [ ] `contextual_insights_api.py` - Contextual insights endpoints
  - [ ] `cross_language_api.py` - Cross-language (Hebrew/Greek) search
  - [ ] `lexicon_api.py` - Lexicon/word lookup endpoints
  - [ ] `search_api.py` - General search API
  - [ ] `vector_search_api.py` - Semantic/vector search endpoints

- [ ] **Utilities** (`src/utils/`):
  - [ ] `bible_reference_parser.py` - Parse Bible references (book:chapter:verse)
  - [ ] `lm_indicator_adapter.py` - **ALREADY INTEGRATED** (Phase-5 LM indicator widget)
  - [ ] `lm_status_helper.py` - Flask/Jinja helpers for LM status badge
  - [ ] `load_bible_data.py` - Bible data loading utilities
  - [ ] `confirm_pgvector.py` - pgvector confirmation utilities
  - [ ] `create_pgvector_tables.py` - pgvector table creation

### Web Interface (to be harvested into React)

- [ ] **Flask routes** (`web_app.py`):
  - [ ] Main web interface routes (render_template calls)
  - [ ] Search interface
  - [ ] Contextual insights views
  - [ ] Multi-translation support (TAHOT, KJV, ASV, YLT)

### LM / Prompt Patterns

- [ ] LM Studio integration patterns (already aligned with Gemantria control-plane)
  - [ ] Uses `lm_indicator.json` from Gemantria (Phase-5 integration)
  - [ ] Semantic search embeddings via LM Studio (`text-embedding-bge-m3`)

### MCP Operations

- [ ] `mcp_universal_operations.py` - 42+ automated operations for system management
  - [ ] Evaluate which operations are useful for Gemantria control-plane


## 3. Items explicitly *not* ported

- [ ] **Flask/Jinja web interface** - To be replaced by unified React UI in Gemantria.v2
- [ ] **Legacy test files** - Archive/test_files/ contains old test code, not needed for port
- [ ] **MCP server implementations** - Evaluate for Gemantria MCP bridge, but may not need direct port
- [ ] **Standalone web_app.py** - Flask routes will be harvested as reference, but UI rebuilt in React

