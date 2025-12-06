# Phase 8 & 10 PM Decision — ai_nouns.json and Node Source

## Decision Summary

1. **Immediate Action (Option A — APPROVED):**
   - Treat `exports/ai_nouns.json` as a test artifact, not a production SSOT.
   - For Phase 15 and COMPASS work, `scripts/export_graph.py` must use **database/DMS nodes**, not `ai_nouns.json`.
   - Short-term fix:
     - Rename or remove `exports/ai_nouns.json` so the graph export falls back to DB nodes.

2. **Governance Clarification (Option C — ADOPTED):**
   - DB/DMS is the **primary node source** for graph exports.
   - Files like `ai_nouns.json` may only be used via explicit test/experimental flags.
   - They may not silently override DMS-backed exports in the default path.
   - This policy must be reflected in future ADR/SSOT docs and, if needed, in `scripts/export_graph.py` logic.

3. **Deferred Work (Option B — DEFERRED):**
   - Regenerating `ai_nouns.json` with a full node set is **not required** to unblock Phase 15.
   - If we later need `ai_nouns.json` as a derived view, it will:
     - Be generated from the DB,
     - Be clearly labeled as derived, not SSOT,
     - And never override DB nodes by default.

## Next Steps (for OPS)

1. Apply the Option A fix:
   - If `exports/ai_nouns.json` exists, move it aside (e.g., to `exports/ai_nouns.json.bak`).
   - Re-run the graph export to repopulate `exports/graph_latest.json` from DB nodes.

2. Re-run Phase 8 and Phase 10 analytics after the graph export is fixed:
   - `python scripts/temporal_analytics.py` (Phase 8)
   - `export_correlations` via `scripts/export_stats.py` (Phase 10, once DB/DSN/scipy are available)

3. Confirm:
   - `graph_latest.json` has a large node count with required metadata,
   - `temporal_patterns.json` and `graph_correlations.json` contain non-empty, valid data.
