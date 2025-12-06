# Phase 9.1 & Phase 10 Documentation Updates

## Phase 9.1: DMS Integration - COMPLETE

**Files Updated:**

1. **docs/SSOT/PM_CONTRACT.md** 
   - Added Section 2.6: DMS-First Context Discovery
   - Documents requirement to query Postgres control plane before file searching
   - Establishes feature registration workflow (MCP envelope → ingest → KB registry)

2. **.cursor/rules/053-pm-dms-integration.mdc** (NEW)
   - Full workflow specification
   - Context query sequence
   - Feature registration steps
   - Contract violations and enforcement

3. **AGENTS.md**
   - Added "PM DMS Integration (Rule-053)" section
   - Quick reference for DMS-first workflow
   - Points to detailed documentation

**Key Workflow Change:**
```
OLD: PM searches files (grep_search, find_by_name)
NEW: PM queries DB first (pmagent kb, control.mcp_tool_catalog)
```

**Registration Flow:**
```
Build feature → Create MCP envelope → make mcp.ingest → Update KB registry → PM discovers tool
```

---

## Phase 10: Revised Architecture (Cursor Auto Feedback)

**Original Plan (MY MISTAKE):**
- Separate React app (`webui/biblescholar/`)
- New FastAPI server
- Didn't check existing infrastructure

**Cursor Auto's Correction (BETTER):**
- **Hybrid approach**: Hermetic by default + optional live API mode
- Use existing `src/services/api_server.py`
- Use existing backend flows (already implemented)
- Keep BibleScholar in orchestrator-shell (RFC-081 compliant)
- No separate app needed

**Why This is Better:**
1. Follows RFC-081 (BibleScholar as module)
2. Uses existing infrastructure
3. Maintains hermetic fallback
4. Optional live mode doesn't break existing workflow
5. Simpler implementation

**Revised Phase 10 Plan:**

**Phase 10A**: API endpoint completion (use existing `api_server.py`)
- Add missing endpoints using existing flows

**Phase 10B**: Hybrid tab components
- Add "Live Search" toggle to each tab (default: OFF = hermetic)
- When OFF: use static exports (current behavior)
- When ON: call live API
- Fallback to hermetic if API fails

**Phase 10C-E**: Search UI enhancement, additional features, polish

---

## Next Steps

**Option 1: Execute Phase 9.1 First** (Register BibleScholar in MCP)
- Create `biblescholar_envelope.json`
- Run `make mcp.ingest`
- Update KB registry
- Test PM DMS-first behavior

**Option 2: Revise Phase 10 Plan First**
- Update implementation_plan.md with hybrid approach
- Get user approval
- Then execute Phase 9.1

**Recommendation**: Execute Phase 9.1 first - it's small, self-contained, and validates the DMS workflow. Then tackle Phase 10 with correct architecture.
