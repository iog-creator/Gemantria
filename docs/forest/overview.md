# Forest Overview

Generated: 2025-11-08 16:41:40

## Active Rules

- Rule 000-ssot-index: 000-ssot-index (AlwaysApply)
- Rule 001-db-safety: ---
- Rule 002-gematria-validation: ---
- Rule 003-graph-and-batch: ---
- Rule 004-pr-workflow: ---
- Rule 005-github-operations: ---
- Rule 006-agents-md-governance: ---
- Rule 007-infrastructure: ---
- Rule 008-cursor-rule-authoring: ---
- Rule 009-documentation-sync: ---
- Rule 010-task-brief: ---
- Rule 011-production-safety: ---
- Rule 012-connectivity-troubleshooting: ---
- Rule 013-report-generation-verification: ---
- Rule 014-governance-index: ---
- Rule 015-semantic-export-compliance: ---
- Rule 016-visualization-contract-sync: ---
- Rule 017-agent-docs-presence: ---
- Rule 018-ssot-linkage: ---
- Rule 019-metrics-contract-sync: ---
- Rule 020-ontology-forward-compat: ---
- Rule 021-stats-proof: ---
- Rule 022-visualization-contract-sync: ---
- Rule 023-visualization-api-spec: ---
- Rule 024-dashboard-ui-spec: ---
- Rule 025-phase-gate: ---
- Rule 026-system-enforcement-bridge: ---
- Rule 027-docs-sync-gate: ---
- Rule 028-phase-freshness: ---
- Rule 029-adr-coverage: ---
- Rule 030-share-sync: ---
- Rule 031-correlation-visualization-validation: ---
- Rule 032-pattern-integrity-validation: ---
- Rule 033-visualization-api-validation: ---
- Rule 034-temporal-suite: ---
- Rule 035-forecasting-spec: ---
- Rule 036-temporal-visualization-spec: ---
- Rule 037-data-persistence-completeness: ---
- Rule 038-exports-smoke-gate: ---
- Rule 039-execution-contract: ---
- Rule 040-ci-triage-playbook: ---
- Rule 041-pr-merge-policy: ---
- Rule 042-formatter-single-source-of-truth: ---
- Rule 043-ci-db-bootstrap: ---
- Rule 044-share-manifest-contract: ---
- Rule 045-rerank-blend-SSOT: ---
- Rule 046-ci-hermetic-fallbacks: ---
- Rule 047-reserved: ---
- Rule 048-reserved: ---
- Rule 049-gpt5-contract-v5: ---
- Rule 050-ops-contract: ---
- Rule 051-cursor-insight: ---
- Rule 052-tool-priority: ---
- Rule 053-idempotence: ---
- Rule 054-reuse-first: ---
- Rule 055-auto-docs-sync: ---
- Rule 056-ui-generation: ---
- Rule 057-embedding-consistency: ---
- Rule 058-auto-housekeeping: ---
- Rule 059-context-persistence: ---
- Rule 060-response-style: ---
- Rule 061-ai-learning-tracking: ---
- Rule 062-environment-validation: ---
- Rule 063-git-safety: ---
- Rule 064-ai-tracking-contract: id: "064"

## CI Workflows

- agents-md-lint.yml
- ci-main.yml
- ci-pr.yml
- ci_rfc3339_release.yml
- coverage-nightly.yml
- crossrefs-smoke.yml
- dbmirror.yml
- enforce-ruff.yml
- graph-nightly.yml
- lint-nightly.yml
- nightly.yml
- policy-gate.yml
- pr-comment.yml
- quality-badges.yml
- rc-smokes.yml
- repo-layout-smoke.yml
- reusable-ci.yml
- rules-inventory-nightly.yml
- scorecards.yml
- soft-checks.yml
- ssot-nightly.yml
- system-enforcement.yml
- typing-nightly.yml
- verify-stats.yml
- xref-badges-strict.yml

## ADRs

- 010-chapter-mode-extraction: ADR-010: Chapter-Mode Execution for OT Extraction
- ADR-000-langgraph: ADR-000: Orchestration via LangGraph (StateGraph)
- ADR-001-two-db: ADR-001: Two-DB Safety (bible_db RO; gematria RW)
- ADR-002-gematria-rules: ADR-002: Gematria and Normalization Rules
- ADR-003-batch-semantics: ADR-003: Batch Semantics & Validation Gates
- ADR-004-postgres-checkpointer: ADR-004: Postgres Checkpointer with BaseCheckpointSaver Interface
- ADR-005-metrics-logging: ADR-005: Metrics & Structured Logging
- ADR-006-observability-dashboards: ADR-006: Observability Dashboards & Queries
- ADR-007-llm-integration: ADR-007: LLM Integration and Confidence Metadata
- ADR-008-confidence-validation: ADR-008: Confidence-Aware Batch Validation
- ADR-009-semantic-aggregation: ADR-009: Semantic Aggregation & Network Analysis
- ADR-010-qwen-integration: ADR-010: Qwen3 Integration for Real Semantic Intelligence
- ADR-011-concept-network-verification: ADR-011: Concept Network Health Verification Views
- ADR-012-concept-network-dimension-fix: ADR-012: Concept Network Vector Dimension Correction
- ADR-013-documentation-sync-enhancement: ADR-013: Comprehensive Documentation Synchronization Enhancement
- ADR-014-relations-and-pattern-discovery: ADR-014: Relations & Pattern Discovery
- ADR-015-jsonld-and-visualization: ADR-015: JSON-LD & RDF Graph Exports + Visualization Interface
- ADR-016-insight-metrics-and-ontology: ADR-016: Insight Metrics & Ontology Enrichment
- ADR-017-agent-documentation-presence: ADR-017: Agent Documentation Presence Enforcement
- ADR-018-pattern-correlation: ADR-018: Pattern Correlation Engine
- ADR-019-forest-governance: ADR-019: Forest Governance & Phase Gate System
- ADR-020-ontology-forward-compatibility: ADR-020: Ontology Forward Compatibility
- ADR-021-metrics-contract-synchronization: ADR-021: Metrics Contract Synchronization
- ADR-022-cross-text-pattern-analysis: ADR-022: Cross-Text Pattern Analysis
- ADR-022-system-enforcement-bridge: ADR-022: System Enforcement Bridge
- ADR-023-visualization-api-and-dashboard: ADR-023: Visualization API and Dashboard
- ADR-025-multi-temporal-analytics: ADR-025: Multi-Temporal Analytics & Predictive Patterns
- ADR-026-reranker-bi-encoder-proxy: ADR-026: Reranker Bi-Encoder Proxy Implementation
- ADR-032-bibledb-as-SSOT-roadmap: ADR-032: bible_db as Single Source of Truth (Roadmap)
- ADR-033-ai-nouns-ssot-contract: ADR-033: AI Nouns SSOT Contract (v1)
- ADR-034-uuid-key-evolution: ADR-034: UUID Key Evolution and FK Realignment
- ADR-055-auto-docs-sync-ci: ADR-055: Auto-Docs Sync CI Enforcement
- ADR-056-auto-housekeeping-ci: ADR-056: Auto-Housekeeping CI Enforcement
- ADR-057-context-persistence-ci: ADR-057: Context Persistence CI Enforcement
- ADR-058-gpt-system-prompt-governance: ADR-058: GPT System Prompt Requirements as Operational Governance
- AGENTS: AGENTS.md - Architectural Decision Records Directory

## Phase Gate Status

- Forest regeneration: ✅ Required before new PRs (Rule 025)
- SSOT sync: ✅ Docs/ADRs/rules must sync (Rule 027)
- ADR coverage: ✅ New changes require ADR delta (Rule 029)

