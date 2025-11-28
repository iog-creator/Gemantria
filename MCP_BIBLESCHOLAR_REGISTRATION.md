# MCP Teaching Pipeline - BibleScholar Registration

## Found: The Teaching System

**MCP (Model Context Protocol)** is the robust, repeatable pipeline for teaching pmagent new capabilities.

## How It Works

1. **Tool Catalog**: `control.mcp_tool_catalog` view (database)
2. **Ingest**: `scripts/mcp/ingest_envelope.py` adds new tools
3. **Discovery**: pmagent can query catalog and learn new capabilities
4. **Documentation**: `PLAN-073_M1_KNOWLEDGE_MCP.md`

## What's Missing: Phase 9 BibleScholar Registration

We built Phase 9 features but **didn't register them in MCP catalog**:
- ❌ semantic_search tool
- ❌ cross_language tool  
- ❌ lexicon_lookup tool
- ❌ verse_insights tool

## Next Step

Create `share/mcp/biblescholar_envelope.json` and ingest it, teaching pmagent about BibleScholar capabilities before building Phase 10.

## Process

```bash
# 1. Create envelope
cat > share/mcp/biblescholar_envelope.json << 'EOF'
{
  "schema": "mcp_ingest_envelope.v1",
  "generated_at": "2025-11-22T21:30:00Z",
  "tools": [
    {
      "name": "bible.semantic_search",
      "desc": "Semantic search across 116k Bible verses using BGE-M3 embeddings",
      "tags": ["biblescholar", "search", "semantic", "pgvector"],
      "cost_est": "medium",
      "visibility": "internal"
    }
  ],
  "endpoints": [...]
}
EOF

# 2. Ingest
make mcp.ingest.default

# 3. pmagent can now discover and use these tools
```
