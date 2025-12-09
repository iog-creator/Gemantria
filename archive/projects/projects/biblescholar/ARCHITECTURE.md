# BibleScholar Architecture

## Core Design Principles

### MCP Rule: Database-Only Biblical Answers

- All biblical answers must come **only** from the `bible_db` database.
- LLMs (including LM Studio) may only summarize, paraphrase, or format results from the database.
- LLMs must **never** generate biblical content directly or use their own knowledge.
- If the answer is not in the database, the system must respond:

  > Sorry, I can only answer using the Bible database. No answer found for your query.

- This rule is enforced in all API endpoints, web UI, and LLM/system prompts.

## Component Architecture

### 1. Database Layer (`src/database/`)
- `database.py` - Database connection and models
- `secure_connection.py` - Secure DB connection handling
- `langchain_integration.py` - LangChain integration for AI workflows

### 2. API Layer (`src/api/`)
- `api_app.py` - RESTful API server (Flask)
- `comprehensive_search.py` - Comprehensive Bible search functionality
- `contextual_insights_api.py` - Contextual insights endpoints
- `cross_language_api.py` - Cross-language (Hebrew/Greek) search
- `lexicon_api.py` - Lexicon/word lookup endpoints
- `search_api.py` - General search API
- `vector_search_api.py` - Semantic/vector search endpoints

### 3. Utilities (`src/utils/`)
- `bible_reference_parser.py` - Parse Bible references (book:chapter:verse)
- `lm_indicator_adapter.py` - **ALREADY INTEGRATED** (Phase-5 LM indicator widget)
- `lm_status_helper.py` - Flask/Jinja helpers for LM status badge
- `load_bible_data.py` - Bible data loading utilities
- `confirm_pgvector.py` - pgvector confirmation utilities
- `create_pgvector_tables.py` - pgvector table creation

### 4. Web Interface (`web_app.py`)
- Flask routes for main web interface
- Search interface
- Contextual insights views
- Multi-translation support (TAHOT, KJV, ASV, YLT)

## Integration Points with Gemantria

### LM Indicator Integration
- Uses `lm_indicator.json` from Gemantria (Phase-5 integration)
- Semantic search embeddings via LM Studio (`text-embedding-bge-m3`)
- LM Studio integration patterns aligned with Gemantria control-plane

### Data Access Patterns
- Reads from `bible_db` database (read-only for biblical content)
- Uses Gemantria exports for LM status and control-plane data
- Vector embeddings stored in PostgreSQL with pgvector

## MCP Operations

The `mcp_universal_operations.py` provides 42+ automated operations across 7 domains:
- System health monitoring
- Database queries and statistics
- Git repository analysis
- Issue logging and tracking
- Process monitoring
- Documentation generation
- System validation

