# Implement AgentPM-Next:M4 (Atlas UI Integration)

**Goal**: Visualize the new KB documentation health metrics (freshness, fixes, missing) in the `/status` page, completing the feedback loop from M3 (Snapshot Integration).

## 1. Update `src/services/api_server.py`
- **HTML Template (`status_page`)**:
  - Enhance the `#doc-health-card` to include a "Metrics" subsection.
  - Add placeholders for:
    - Freshness Score (e.g., `kb_fresh_ratio.overall`)
    - Fix Activity (e.g., `kb_fixes_applied_last_7d`)
    - Missing/Stale Counts
- **JavaScript (`loadStatus`)**:
  - Update `loadStatus` to extract `data.kb_doc_health` from the `/api/status/system` response.
  - Implement logic to populate the new HTML elements.
  - Ensure graceful fallback if `kb_doc_health` is missing or available=False.

## 2. Verify UI Integration
- **Test File**: `tests/web/test_status_page.py`
- **Action**: 
  - Update existing tests or add a new test case to verify the new HTML elements are present in the response.
  - Mock `get_system_snapshot` to return sample `kb_doc_health` data and assert it renders in the HTML.

## 3. Documentation
- **Update**: `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md` to reflect M4 completion (UI visualization).

