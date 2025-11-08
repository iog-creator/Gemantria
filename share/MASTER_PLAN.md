# MASTER PLAN — Gemantria Pipeline Project

**Version**: Phase 8 Ledger & Phase 10: Multi-Temporal Analytics with Rolling Windows, Forecasting, and Interactive Exploration
**Last Updated**: 2025-11-07
**Governance**: OPS Contract v6.2.3

---

## Mission

Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts, with self-healing guards and governance.

### Core Priorities
1. **Correctness**: Code gematria > bible_db > LLM (LLM = metadata only)
2. **Determinism**: content_hash identity; uuidv7 surrogate; fixed seeds; position_index
3. **Safety**: bible_db is READ-ONLY; parameterized SQL only; fail-closed if <50 nouns (ALLOW_PARTIAL=1 is explicit)

---

## Phase Overview

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | ✅ **Complete** | Governance v6.2.3, internal guardrails active |
| 1 | ✅ **Complete** | Data Layer (DB foundation) |
| 2 | ✅ **Complete** | Pipeline Core (LangGraph) |
| 3 | ✅ **Complete** | Exports & Badges |
| 5 | ✅ **Complete** | UI Polish |
| 8 | ✅ **Complete** | Temporal Analytics Suite (rolling windows + forecasts + visualization) |
| 9 | ✅ **Complete** | Graph Latest with Node/Edge Exports |
| 10 | ✅ **Complete** | Correlation Visualization + Pattern Analytics |
| 11 | ✅ **Complete** | Unified Envelope (100k nodes, COMPASS validation) |

## Current Status: **Production Operations**

All core development phases are complete. The system is operational with:
- ✅ Unified envelope pipeline working
- ✅ COMPASS mathematical validation active
- ✅ Schema compliance verified
- ✅ UI integration functional
- ✅ Governance rules enforced

---

## Phase 8: Multi-Temporal Analytics Suite

### Goals
- Rolling window analysis of temporal patterns in biblical texts
- Prophet-based forecasting for concept frequency trends
- Interactive temporal exploration UI components
- Schema validation and COMPASS mathematical correctness (>80% score)

### Deliverables
- `temporal_patterns.json` — Rolling statistics with z-scores and change points
- `pattern_forecast.json` — Prophet forecasts with confidence intervals
- Temporal strip visualization component
- COMPASS scorer for mathematical envelope validation

### Current Status: ✅ **Active**
- Rolling window computation implemented
- Temporal schema validation in place
- UI temporal strip component ready
- COMPASS scoring framework deployed

---

## Phase 9: Graph Latest Foundation

### Goals
- Complete graph export with nodes, edges, and metadata
- Node clustering and centrality calculations
- Edge strength computation and classification
- Export validation and schema compliance

### Deliverables
- `graph_latest.json` — Complete graph with 50k+ nodes
- `graph_stats.json` — Degree/betweenness/eigenvector metrics
- `graph_patterns.json` — Cross-text pattern analysis
- Schema validation guards

### Current Status: ✅ **Complete**
- Graph export pipeline operational
- Statistics computation working
- Pattern analysis integrated
- Schema guards active in CI

---

## Phase 10: Correlation Visualization

### Goals
- Cross-text pattern analytics with rerank edge strength
- Interactive correlation matrix visualization
- Pattern discovery and motif identification
- Performance optimization for large graphs

### Deliverables
- `correlation_weights.json` — Edge significance analysis
- `graph_correlations.json` — Matrix exports
- Interactive correlation viewer
- Optimized rendering for 100k+ nodes

### Current Status: ✅ **Complete**
- Correlation matrix generation active
- Edge strength rerank blend implemented
- Visualization components ready
- Performance gates in place

---

## Phase 11: Unified Envelope

### Goals
- Single integrated export format with all artifacts
- COMPASS mathematical envelope validation
- Size extraction (100, 1k, 10k, 100k+ nodes)
- Forward compatibility with schema evolution

### Deliverables
- `unified_envelope.json` — Complete integrated format
- COMPASS scorer (correlation + edge blend + temporal validation)
- Size-controlled extraction scripts
- Schema evolution support

### Current Status: ✅ **Complete**
- Unified envelope format implemented
- COMPASS validation framework active
- Size extraction working
- Schema evolution ready

---

## Technical Architecture

### Pipeline Flow
```
Noun Extraction → Enrichment → Network Building → Schema Validation → Analysis → Export
     ↓              ↓              ↓                    ↓             ↓         ↓
collect_nouns → enrichment → network_aggregator → schema_validator → analysis → export_graph
```

### Core Components
1. **LangGraph Orchestration** — Deterministic pipeline execution
2. **Qwen Live Gate** — Fail-closed AI health checks
3. **Schema Validation** — JSON Schema enforcement
4. **COMPASS Scoring** — Mathematical correctness validation
5. **Temporal Analytics** — Rolling windows + forecasting
6. **Unified Exports** — Integrated artifact format

### Quality Gates
- **Schema compliance** — All exports validated against SSOT schemas
- **Mathematical correctness** — COMPASS >80% score requirement
- **Determinism** — Identical inputs produce identical outputs
- **Safety** — bible_db read-only, fail-closed on errors
- **Performance** — Size gates prevent resource exhaustion

---

## Data Lineage

### Primary Artifacts
1. `graph_latest.json` — Core graph with nodes/edges/metadata
2. `temporal_patterns.json` — Time-series rolling window analysis
3. `pattern_forecast.json` — Prophet forecasting results
4. `correlation_weights.json` — Cross-text pattern analytics
5. `unified_envelope.json` — Single integrated format (Phase 11)

### Export Scripts
- `scripts/extract/extract_all.py` — Unified extraction with size controls
- `scripts/temporal_analytics.py` — Rolling window + forecast computation
- `scripts/export_graph.py` — Graph export with statistics
- `scripts/export_correlations.py` — Pattern correlation analysis

---

## Governance & Operations

### Rules Framework
- **Rule 001-061** — Complete governance rule set
- **OPS Contract v6.2.3** — Execution discipline
- **SSOT Schemas** — docs/SSOT/ directory
- **SHARE_MANIFEST.json** — Export synchronization

### CI/CD Pipeline
- **Hermetic builds** — No external dependencies
- **Schema validation** — All exports checked
- **Mathematical verification** — COMPASS scoring
- **Performance gates** — Size and time limits
- **Determinism checks** — Reproducible outputs

### Agent Framework
- **Ingestion Agent** — Text → shards
- **Discovery Agent** — Organic noun extraction
- **Enrichment Agent** — Theological context
- **Graph Builder** — Network construction
- **Analytics Agent** — Stats + patterns + temporal
- **Guard Agent** — Schema + invariants validation

---

## Next Steps

### Immediate (Phase 8 Completion)
- [ ] Temporal analytics integration testing
- [ ] UI temporal strip deployment
- [ ] COMPASS scorer validation
- [ ] Phase 8 documentation updates

### Medium-term (Q1 2026)
- [ ] Phase 12: Advanced Pattern Mining
- [ ] Phase 13: Multi-language Support
- [ ] Phase 14: Real-time Analytics
- [ ] Phase 15: API Gateway

### Long-term Vision
- **Complete Biblical Analytics Suite** — Full corpus analysis
- **Interactive Exploration Platform** — Web-based discovery tools
- **Academic Research Integration** — Scholar collaboration features
- **Global Accessibility** — Multi-language biblical text support

---

## Success Metrics

### Technical Metrics
- **Coverage**: >98% test coverage maintained
- **Performance**: <30s for 100k node exports
- **Correctness**: COMPASS >80% score on all envelopes
- **Reliability**: 99.9% pipeline success rate

### Product Metrics
- **Completeness**: All major biblical books analyzed
- **Accuracy**: Verified gematria calculations
- **Usability**: Intuitive visualization interfaces
- **Adoption**: Active research community engagement

---

## Risk Mitigation

### Technical Risks
- **Scale**: Size gates and performance monitoring
- **Data Integrity**: Schema validation + COMPASS scoring
- **AI Dependency**: Fail-closed Qwen Live Gate
- **Determinism**: Fixed seeds + content hashing

### Operational Risks
- **Code Drift**: git pull blocking + wrapper scripts
- **Schema Evolution**: Versioned schemas + compatibility
- **CI Stability**: Hermetic builds + rollback procedures
- **Documentation**: SSOT sync + automated updates

---

## Conclusion

The Gemantria project represents a comprehensive approach to biblical text analysis, combining rigorous mathematical methods with AI-powered insights and interactive visualization. Through careful phase planning, strict governance, and mathematical validation, we deliver reliable, reproducible results for biblical research and exploration.

**Current Focus**: Phase 8 temporal analytics completion and Phase 11 unified envelope stabilization.

**Next Milestone**: Phase 12 advanced pattern mining capabilities.

<!-- RULES_TABLE_START -->
| # | Title |
|---:|-------|
| 000 | # (Default-Apply) |
| 001 | # (Default-Apply) |
| 002 | # (Default-Apply) |
| 003 | # (Default-Apply) |
| 004 | # (Default-Apply) |
| 005 | # (Default-Apply) |
| 006 | # (Default-Apply) |
| 007 | # (Default-Apply) |
| 008 | # (Default-Apply) |
| 009 | # (Default-Apply) |
| 010 | # (Default-Apply) |
| 011 | # (Default-Apply) |
| 012 | # (Default-Apply) |
| 013 | # (Default-Apply) |
| 014 | # (Default-Apply) |
| 015 | # (Default-Apply) |
| 016 | # (Default-Apply) |
| 017 | # (Default-Apply) |
| 018 | # (Default-Apply) |
| 019 | # (Default-Apply) |
| 020 | # (Default-Apply) |
| 021 | # (Default-Apply) |
| 022 | # (Default-Apply) |
| 023 | # (Default-Apply) |
| 024 | # (Default-Apply) |
| 025 | # (Default-Apply) |
| 026 | # (Default-Apply) |
| 027 | # (Default-Apply) |
| 028 | # (Default-Apply) |
| 029 | # (Default-Apply) |
| 030 | # (Default-Apply) |
| 031 | # (Default-Apply) |
| 032 | # (Default-Apply) |
| 033 | # (Default-Apply) |
| 034 | # (Default-Apply) |
| 035 | # (Default-Apply) |
| 036 | # (Default-Apply) |
| 037 | # (Default-Apply) |
| 038 | # (Default-Apply) |
| 039 | # (Default-Apply) |
| 040 | # (Default-Apply) |
| 041 | # (Default-Apply) |
| 042 | # (Default-Apply) |
| 043 | # (Default-Apply) |
| 044 | # (Default-Apply) |
| 045 | # (Default-Apply) |
| 046 | # (Default-Apply) |
| 047 | # (Default-Apply) |
| 048 | # (Default-Apply) |
| 049 | # (Default-Apply) |
| 050 | # (AlwaysApply) |
| 051 | # (AlwaysApply) |
| 052 | # (AlwaysApply) |
| 053 | # (Default-Apply) |
| 054 | # (Default-Apply) |
| 055 | # (Default-Apply) |
| 056 | # (Default-Apply) |
| 057 | # (Default-Apply) |
| 058 | # (Default-Apply) |
| 059 | # (Default-Apply) |
| 060 | # (Default-Apply) |
| 061 | # (Default-Apply) |
| 062 | # (Default-Apply) |
| 063 | # (Default-Apply) |
<!-- RULES_TABLE_END -->
