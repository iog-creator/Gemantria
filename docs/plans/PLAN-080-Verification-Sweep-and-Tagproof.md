# PLAN-080: Phase-1+2 Verification Sweep & Tagproof

**Date:** 2025-11-20
**Session Goal:** Comprehensive verification sweep of Phase-1+2 components and hardening tagproof bundle
**Status:** 📋 Planned — Ready for implementation

## Scope & Objectives

PLAN-080 implements a comprehensive verification sweep of Phase-1+2 components, ensuring all systems are production-ready and creating a hardened tagproof bundle for release validation.

### Key Deliverables
- **E96**: TV-01…TV-05 Re-Run & Coverage Receipt - Re-execute test vectors with full coverage audit
- **E97**: Gatekeeper/Guard Shim Coverage Audit - Validate guard/gatekeeper implementation completeness
- **E98**: Full Extraction & Atlas + Exports Regeneration - End-to-end pipeline verification
- **E99**: Browser Verification & Screenshot Check (Integrated) - Visual and functional UI validation
- **E100**: Strict Tag Lane / Tagproof "Phase-2 Ready" Bundle - Release-ready artifact bundle with STRICT validation

## Implementation Tasks

### E96: TV-01…TV-05 Re-Run & Coverage Receipt
- **Goal:** Re-execute all test vectors (TV-01 through TV-05) with comprehensive coverage audit
- **Scope:** AgentPM guarded calls, gatekeeper policies, tool validation logic
- **Acceptance:** 100% TV coverage with detailed receipts; no regressions from baseline
- **Deliverables:** `evidence/tv_coverage_receipt_E96.json`, updated TV test suite

### E97: Gatekeeper/Guard Shim Coverage Audit
- **Goal:** Audit gatekeeper and guard shim implementation for complete coverage
- **Scope:** Policy enforcement, capability sessions, violation recording
- **Acceptance:** All shim interfaces tested; coverage metrics >95%
- **Deliverables:** `evidence/gatekeeper_guard_audit_E97.json`, coverage reports

### E98: Full Extraction & Atlas + Exports Regeneration
- **Goal:** End-to-end verification of data pipeline from extraction through visualization
- **Scope:** Graph extraction, Atlas dashboard generation, export validation
- **Acceptance:** All artifacts regenerate successfully; COMPASS scores >80%
- **Deliverables:** Fresh `share/atlas/`, `share/exports/`, validation receipts

### E99: Browser Verification & Screenshot Check (Integrated)
- **Goal:** Integrated browser verification with screenshot validation and manifest checks
- **Scope:** Web UI rendering, interactive elements, visual consistency
- **Acceptance:** All pages load correctly; screenshots match manifests; no visual regressions
- **Deliverables:** `evidence/webproof/` updates, screenshot validation receipts

### E100: Strict Tag Lane / Tagproof "Phase-2 Ready" Bundle
- **Goal:** Create hardened tagproof bundle with STRICT validation for Phase-2 readiness
- **Scope:** All Phase-1+2 artifacts, compliance exports, guard receipts, STRICT mode validation
- **Acceptance:** Bundle validates in STRICT mode; all guards pass; release-ready
- **Deliverables:** `tagproof/phase2_ready_bundle.tar.gz`, `evidence/tagproof_phase2_ready.json`

## Current State Assessment

### What Exists Today
- **Test Vectors:** TV-01…TV-05 framework exists in `agentpm/tests/`
- **E96 Coverage:** `test.tv.coverage` and `guard.tv.coverage` targets wired; `evidence/tv_coverage_receipt.json` generated with all TVs passing
- **E97 Coverage:** `gatekeeper.coverage` and `guard.gatekeeper.coverage` targets wired; `evidence/gatekeeper_coverage.json` generated with all seven violation codes present and covered
- **E98 Regeneration:** `regenerate.all` target wired; `share/atlas/` and `share/exports/` fully regenerated with exports (`graph_latest.json`, `graph_stats.json`, `graph_patterns.json`, `temporal_patterns.json`, `pattern_forecast.json`) validated via `ci.exports.smoke`, `atlas.viewer.validate`, `schema.validate`, and `analytics.export`
- **Browser Verification:** Basic browser verification script exists (`scripts/ops/browser_verify.sh`)
- **Tagproof Infrastructure:** Tagproof workflows exist in `.github/workflows/`
- **Atlas/Exports:** Current artifacts in `share/atlas/`, `share/exports/`
- **Guard/Gatekeeper:** Basic implementations exist in `agentpm/guard/`, `agentpm/gatekeeper/`

### What Needs Implementation
- **E99 Integration:** Unified browser + screenshot validation
- **E100 Bundle:** STRICT-mode tagproof bundle assembly

### PLAN-092 Verification Evidence

**M1 - KB Worklist Generation:**
```json
{
    "available": true,
    "total_items": 2,
    "by_subsystem": {"agentpm": 1, "webui": 1},
    "items": [
        {
            "id": "subsystem:agentpm",
            "title": "Subsystem 'agentpm' documentation",
            "severity": "low_coverage"
        }
    ]
}
```

**M3 - KB Health Reporting:**
```json
{
    "available": true,
    "metrics": {
        "kb_fresh_ratio": {"overall": 100.0},
        "kb_missing_count": {"overall": 0},
        "kb_fixes_applied_last_7d": 0
    }
}
```

**M4 - UI Integration (pm.snapshot kb_doc_health):**
```json
"kb_doc_health": {
    "available": true,
    "metrics": {
        "kb_fresh_ratio": {"overall": 100.0},
        "kb_missing_count": {"overall": 0}
    }
}
```

## Implementation Strategy

### Execution Order
1. **E96** (TV Re-run) - Establish baseline coverage receipts
2. **E97** (Guard Audit) - Validate implementation completeness
3. **E98** (Extraction Regen) - Verify end-to-end pipeline
4. **E99** (Browser Verify) - Confirm UI/visual integrity
5. **E100** (Tagproof Bundle) - Assemble release-ready artifacts

### PR Structure
- **Individual PRs:** Each E96-E100 as separate PR for focused review
- **Integration PR:** Final PR combining all E96-E100 changes
- **Tagproof PR:** STRICT validation and bundle assembly

### Success Criteria
- **E96-E99:** All tasks complete with green receipts in HINT mode
- **E100:** STRICT tagproof bundle validates successfully
- **Integration:** All Phase-1+2 components verified end-to-end

### Key PLAN-092 Files Created/Modified
- `agentpm/status/kb_metrics.py` - Core KB registry and metrics engine
- `pmagent/cli.py` - Added plan kb, plan kb fix, report kb subcommands
- `agentpm/status/snapshot.py` - Integrated kb_doc_health into system snapshots
- `src/services/api_server.py` - Added kb_doc_health to /api/status/system
- `tests/web/test_status_page.py` - UI tests for KB metrics display
- Various test files for CLI and runtime verification

## Evidence & Validation

### Pre-Implementation Evidence
- **TV Framework:** `agentpm/tests/` contains TV-01…TV-05 test structures
- **Browser Scripts:** `scripts/ops/browser_verify.sh` exists with basic functionality
- **Tagproof Workflows:** `.github/workflows/tagproof*.yml` exist
- **Atlas Artifacts:** `share/atlas/` contains current dashboard exports
- **Guard Infrastructure:** `agentpm/guard/`, `agentpm/gatekeeper/` have base implementations

### Success Metrics
- **Coverage:** >95% for all guard/gatekeeper shims (E97)
- **Validation:** All TVs pass with receipts (E96)
- **Pipeline:** COMPASS >80% on regenerated exports (E98)
- **UI:** All browser verifications pass (E99)
- **Release:** STRICT tagproof bundle validates (E100)

## Related Components
- **reality.green:** End-to-end system validation target
- **Browser Verification:** Integrated visual testing framework
- **Tagproof Workflows:** STRICT validation for releases
- **Atlas Dashboard:** Visual verification target

## Related PRs
- **PR #581**: AgentPM-Next PLAN-092 (M1-M4) implementation (merged) ✅
- Includes M1 kb planning, M2 kb fix orchestration, M3 kb reporting, M4 Atlas UI integration

## PLAN-092 Summary

**AgentPM-Next PLAN-092 (M1-M4)** introduces a comprehensive KB registry-powered planning system for documentation management. The implementation provides CLI tools for worklist generation, orchestrated fixes, health reporting, and Atlas UI integration. All components are verified working and the feature is fully shipped.

**Status**: ✅ COMPLETE - Ready for next plan selection