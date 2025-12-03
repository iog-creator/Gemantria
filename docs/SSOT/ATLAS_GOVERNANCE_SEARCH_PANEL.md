# Atlas Governance Search Panel & Orchestrator Console (Phase-8D)

## 1. Purpose

This document defines the **Phase-8D UI layer** that sits on top of the
already-completed **Phase-8C semantic search backend**:

- Phase-8C: `pmagent/docs/search.py` + `pmagent docs.search` CLI +
  doc fragments/embeddings guards (STRICT/tagproof).
- Phase-8D: Atlas/TV **Governance Search Panel** and **Orchestrator Console**
  that let the human orchestrator search, browse, and understand governance docs
  in a curated way (no raw logs).

The goal is to expose **meaning-based search over Tier-0 governance docs**
through a friendly, movable-panel UI that runs on top of the existing Atlas/Web
framework.

## 2. Backend Inputs (already implemented)

Phase-8C provides:

- `pmagent/docs/search.py` — semantic search implementation
- `pmagent docs search "query" --k 10 --tier0-only --json-only` — CLI entrypoint
- Guards:
  - `guard_doc_fragments.py` — verifies all Tier-0 docs have fragments
  - `guard_doc_embeddings.py` — verifies all fragments have embeddings
- Evidence:
  - `guard_doc_fragments.verify.json`
  - `guard_doc_embeddings.verify.json`
  - `pmagent.docs.search.tier0.single_query.{json,text}`
- Model: `granite-embedding:278m` (1024-dim embeddings, stored in Postgres)

Phase-8D must **reuse this path**. No new embedding logic, no new DB tables.

## 3. API Contract: `/api/docs/search`

### 3.1 Endpoint

- Method: `GET`
- Path: `/api/docs/search`
- Query params:
  - `q` (required): search query string
  - `k` (optional, default: 10): number of results
  - `tier0_only` (optional, default: true): whether to restrict to Tier-0 docs

### 3.2 Response Shape

```jsonc
{
  "query": "How does the system enforce correctness across all Tier-0 documents?",
  "k": 10,
  "tier0_only": true,
  "results": [
    {
      "rank": 1,
      "score": 0.92,
      "source_id": "AGENTS::docs/SSOT/AGENTS.md",
      "title": "AGENTS.md — Gemantria Agent Framework",
      "snippet": "We operate under Rule-050 (LOUD FAIL), Rule-051 (CI gating)...",
      "section": {
        "heading": "Governance Posture — Always-Apply Triad",
        "anchor": "#governance-posture-always-apply-triad"
      },
      "provenance": {
        "doc_path": "docs/SSOT/AGENTS.md",
        "fragment_id": "control.doc_sections:abcd-1234",
        "content_hash": "sha256:..."
      }
    }
  ],
  "model_name": "granite-embedding:278m",
  "ok": true
}
```

### 3.3 Error Response

```jsonc
{
  "ok": false,
  "query": "...",
  "error": "Failed to generate query embedding: ...",
  "results": []
}
```

### 3.4 Implementation Notes

- **Reuse existing search function**: Call `pmagent.docs.search.search_docs()` directly
- **Response transformation**: Map CLI output shape to API response shape:
  - `logical_name` → `source_id` + `title` (parse `AGENTS::` prefix)
  - `content` → `snippet` (already truncated to ~200 chars)
  - Add `rank` (1-indexed) and `section` metadata if available
- **Error handling**: Return 500 on DB/embedding failures, 400 on invalid params
- **CORS**: Already enabled in FastAPI middleware

## 4. UI Component: Governance Search Panel

### 4.1 Location

- **Primary**: New page at `/governance-search` (standalone search interface)
- **Secondary**: Movable panel in Atlas viewer (`/atlas` or `/docs/atlas/index.html`)

### 4.2 Design Requirements

- **Search Form**:
  - Text input for query (required)
  - Number input for `k` (default: 10, range: 1-50)
  - Checkbox for "Tier-0 only" (default: checked)
  - Submit button ("Search")
- **Results Display**:
  - List of results with:
    - Rank + score (badge)
    - Source title (link to doc)
    - Snippet (highlighted query terms)
    - Section heading (if available)
  - Empty state: "No results found" or "Enter a query to search"
  - Loading state: Spinner + "Searching..."
- **Styling**:
  - Use Tailwind CSS (consistent with `/bible` and `/status` pages)
  - Responsive layout (mobile-friendly)
  - Accessible (ARIA labels, keyboard navigation)

### 4.3 Integration with Atlas Viewer

- **Option A (Recommended)**: Standalone page with link from Atlas
  - Add "Governance Search" link in Atlas index.html
  - Keep search UI separate (cleaner, easier to maintain)
- **Option B**: Embedded panel in Atlas
  - Add collapsible search panel to Atlas viewer
  - More complex (requires iframe or shared state)

**Decision**: Start with Option A (standalone page). Option B can be added later if needed.

## 5. Implementation Steps (OPS-026)

### Step 1: API Endpoint

1. Add endpoint to `src/services/api_server.py`:
   ```python
   @app.get("/api/docs/search")
   async def search_docs_endpoint(
       q: str = Query(..., description="Search query"),
       k: int = Query(10, ge=1, le=50, description="Number of results"),
       tier0_only: bool = Query(True, description="Restrict to Tier-0 docs"),
   ) -> JSONResponse:
       """Search governance/docs content via semantic similarity."""
       from pmagent.docs.search import search_docs
       
       result = search_docs(query=q, k=k, tier0_only=tier0_only)
       
       if not result.get("ok"):
           raise HTTPException(status_code=500, detail=result.get("error", "Search failed"))
       
       # Transform CLI output to API response shape
       # ... (map logical_name to source_id/title, add rank, etc.)
       
       return JSONResponse(content=transformed_result)
   ```

2. Update root endpoint to include new endpoint in `endpoints` dict

3. Test endpoint:
   ```bash
   curl "http://localhost:8000/api/docs/search?q=governance&k=5&tier0_only=true"
   ```

### Step 2: HTML Page

1. Add route to `src/services/api_server.py`:
   ```python
   @app.get("/governance-search", response_class=HTMLResponse)
   async def governance_search_page() -> HTMLResponse:
       """HTML page for governance docs search."""
       # Return HTML template (similar to /bible page)
   ```

2. Create HTML template with:
   - Search form (query, k, tier0_only)
   - Results container
   - JavaScript fetch logic (call `/api/docs/search`)
   - Tailwind CSS styling

3. Test page:
   ```bash
   # Start server
   python -m src.services.api_server
   # Navigate to http://localhost:8000/governance-search
   ```

### Step 3: Atlas Integration

1. Add link in `docs/atlas/index.html`:
   ```html
   <div class="card">
     <h2>Governance Search</h2>
     <p>Search Tier-0 governance docs via semantic similarity.</p>
     <ul><li><a href="/governance-search">Open search interface</a></li></ul>
   </div>
   ```

2. Test integration:
   - Navigate to Atlas viewer
   - Click "Governance Search" link
   - Verify search page loads and works

### Step 4: Documentation

1. Update `src/services/AGENTS.md`:
   - Add `/api/docs/search` endpoint to list
   - Document response shape and error handling

2. Update `docs/SSOT/DOC_CONTENT_VECTOR_PLAN.md`:
   - Mark Phase-8D as IMPLEMENTED
   - Add link to this spec document

3. Update `MASTER_PLAN.md`:
   - Add Phase-8D entry with status

## 6. Testing Requirements

### Unit Tests

- Test API endpoint with various queries
- Test error handling (DB down, invalid params)
- Test response transformation (CLI → API shape)

### Integration Tests

- Test end-to-end search flow (query → results)
- Test Tier-0 filtering (tier0_only=true vs false)
- Test pagination (k parameter)

### Manual Testing

- Verify search returns relevant results
- Verify UI is responsive and accessible
- Verify Atlas link works correctly

## 7. Acceptance Criteria

- [ ] API endpoint `/api/docs/search` returns correct response shape
- [ ] HTML page `/governance-search` renders and functions correctly
- [ ] Search returns relevant results for sample queries
- [ ] Tier-0 filtering works (tier0_only parameter)
- [ ] Atlas viewer has link to search page
- [ ] Documentation updated (AGENTS.md, DOC_CONTENT_VECTOR_PLAN.md, MASTER_PLAN.md)
- [ ] Tests pass (unit + integration)
- [ ] Manual testing complete

## 8. Future Enhancements (Post-Phase-8D)

- **Advanced Filtering**: Filter by doc type, date range, etc.
- **Result Highlighting**: Highlight query terms in snippets
- **Deep Linking**: Link directly to specific sections in docs
- **Search History**: Store recent searches (localStorage)
- **Export Results**: Download results as JSON/CSV
- **Embedded Panel**: Add collapsible search panel to Atlas viewer (Option B)

## 9. Related Documents

- `docs/SSOT/DOC_CONTENT_VECTOR_PLAN.md` — Phase-8C backend implementation
- `docs/SSOT/DOC_REGISTRY_PLAN.md` — Doc registry schema
- `docs/runbooks/GOVERNANCE_DB_SSOT.md` — Governance DB SSOT overview
- `pmagent/docs/search.py` — Search implementation (backend)
- `src/services/api_server.py` — API server (integration point)
- `docs/atlas/index.html` — Atlas viewer (UI integration point)

## 10. Notes

- **No new DB tables**: Reuse existing `control.doc_embedding`, `control.doc_fragment`, `control.doc_registry`
- **No new embedding logic**: Reuse `pmagent.docs.search.search_docs()`
- **Consistent styling**: Use Tailwind CSS (same as `/bible`, `/status` pages)
- **Accessibility**: Follow WCAG 2.1 AA guidelines (keyboard navigation, ARIA labels)
- **Performance**: Consider caching frequent queries (future enhancement)

