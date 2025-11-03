# Phase 11: UI Enhancement & Data Pipeline Improvement

## Sprint 1 Fork Decisions (Breadcrumb for Future Handoffs)

* **1d**: Unified pipeline (graph + temporal + correlations → single envelope)
* **2a**: Modern-minimalist UI (soft blues, gradients, subtle shadows)
* **3a**: Virtual scrolling + chunked rendering for large datasets
* **4d**: Dual metrics views (user-facing badges + developer debug panel)

## Success Criteria for Stub Stage

* Extract stub generates `unified_envelope_SIZE.json` in <2 sec for SIZE=10,000
* GraphPreview logs "Large dataset: Chunked rendering active" for nodeCount>10,000, and renders ≤5,000 nodes
* Badge thresholds: Green <200 ms, Yellow <500 ms, Red ≥500 ms
* Fallback decision: if UI render time >3 sec for 50k nodes, escalate to WebGL (Sprint 3)
* Accessibility secondary check: screen-reader + keyboard navigation for large-dataset view

## Versioning and Tagging Discipline

* Tag new extract format as `unified-v1` in metadata; ensure backward compatibility remains until `unified-v2`
* Include schema version in envelope header

## Data Pipeline Lineage

See AGENTS.md section "Data Extraction Lineage" for complete flow: graph_latest → temporal_export → correlation_weights → unified_envelope

## Implementation Reference

See `.cursor/plans/ui-enhancement-18696d49.plan.md` for detailed implementation plan with 5 phases and specific file targets.

## Acceptance Criteria

- [ ] `docs/PHASE11_PLAN.md` exists with Sprint 1 fork decisions documented
- [ ] Success criteria defined: extract <2sec, chunked rendering >10k nodes
- [ ] Badge thresholds: Green <200ms, Yellow <500ms, Red ≥500ms
- [ ] Fallback path: >3sec@50k → WebGL escalation documented
- [ ] Data lineage section added to `AGENTS.md`
- [ ] `make plan` target added and functional
- [ ] Accessibility secondary check plan documented
