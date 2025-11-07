# Project Documentation

This directory contains the comprehensive documentation system for the Gemantria project, providing multiple layers of documentation to support development, maintenance, and understanding of the semantic network pipeline.

## 🎯 Documentation Layers

The Gemantria documentation system consists of four interconnected layers:

### 1. User-Facing Documentation (`README.md` files)

- **Purpose**: Human-readable guides for developers and users
- **Location**: Every directory contains a `README.md`
- **Content**: Setup instructions, usage examples, architecture overviews
- **Audience**: Developers, maintainers, and end users

### 2. AI Assistant Documentation (`AGENTS.md` files)

- **Purpose**: Structured guidance for AI assistants working on the codebase
- **Location**: Key directories contain `AGENTS.md` files
- **Content**: Development patterns, API contracts, coding standards
- **Audience**: AI assistants and automated tooling

### 3. Architectural Decision Records (`ADRs/` directory)

- **Purpose**: Record important architectural decisions and their rationales
- **Location**: `docs/ADRs/` with ADR-XXX-title.md naming
- **Content**: Context, decision, rationale, alternatives, consequences
- **Audience**: Architects, senior developers, future maintainers

### 4. Single Source of Truth (`SSOT/` directory)

- **Purpose**: Canonical schemas and contract definitions
- **Location**: `docs/SSOT/` with specific schema files
- **Content**: API contracts, data schemas, configuration specifications
- **Audience**: Developers implementing against contracts

## 📁 Directory Structure

```
docs/
├── ADRs/             # Architectural Decision Records
│   ├── ADR-001-database-architecture.md
│   ├── ADR-002-gematria-validation.md
│   └── ...
├── SSOT/             # Single Source of Truth schemas
│   ├── jsonld-schema.md
│   ├── rdf-ontology.md
│   └── ...
├── README.md         # This overview (user-facing)
└── AGENTS.md         # AI assistant guide (machine-readable)
```

## 🔄 Documentation Workflow

### For Code Changes

1. **Identify Impact**: Determine which documentation needs updating
2. **Update README.md**: User-facing documentation in affected directories
3. **Update AGENTS.md**: AI assistant guidance where applicable
4. **Create/Update ADR**: For architectural or significant technical decisions
5. **Update SSOT**: For changes to schemas, contracts, or interfaces
6. **Validate**: Run `scripts/test_docs_sync_rule.sh` to verify compliance

### For New Features

1. **Plan Documentation**: Identify required documentation upfront
2. **Create ADR**: Document architectural decisions first
3. **Implement Code**: With appropriate inline documentation
4. **Create README.md**: For new directories and user-facing features
5. **Create AGENTS.md**: For directories needing AI assistant guidance
6. **Update SSOT**: For new schemas or contract definitions
7. **Cross-Reference**: Ensure all documents reference each other appropriately

## 📚 Key Documentation Files

### ADRs (Architectural Decisions)

| ADR     | Title                          | Status   |
| ------- | ------------------------------ | -------- |
| ADR-001 | Database Architecture & Safety | Accepted |
| ADR-002 | Gematria Calculation Rules     | Accepted |
| ADR-013 | Documentation Synchronization  | Accepted |
| ADR-015 | JSON-LD & Visualization        | Accepted |

### SSOT (Canonical Schemas)

| Schema               | Purpose                             | Format          |
| -------------------- | ----------------------------------- | --------------- |
| `jsonld-schema.md`   | JSON-LD export format specification | Markdown        |
| `rdf-ontology.md`    | RDF vocabulary definitions          | Turtle snippets |
| `webui-contract.md`  | Frontend-backend data contracts     | JSON schemas    |
| `graph-stats-api.md` | Statistics API specification        | JSON examples   |

## 🛠️ Documentation Tools

### Generation & Validation

- **ADR Templates**: `adr-template.md` provides consistent structure
- **Sync Validation**: `scripts/test_docs_sync_rule.sh` enforces requirements
- **Cross-Reference Checking**: Automated link validation between documents
- **Coverage Reporting**: Documentation completeness metrics

### Maintenance Scripts

```bash
# Validate documentation synchronization
./scripts/test_docs_sync_rule.sh

# Check for broken links (future)
./scripts/validate_doc_links.py

# Generate documentation coverage report (future)
./scripts/doc_coverage_report.py
```

## 📋 Documentation Standards

### README.md Files

Every directory must have a README.md containing:

- **Purpose**: Clear statement of directory/function responsibility
- **Structure**: Overview of contents and organization
- **Usage**: How to use or interact with the directory contents
- **Dependencies**: What other parts of the system are required
- **Examples**: Code examples or usage patterns where applicable

### AGENTS.md Files

Key directories contain AGENTS.md files with:

- **Development Guidance**: Patterns and practices for the directory
- **API Contracts**: Interface specifications and requirements
- **Testing Standards**: How to test code in this directory
- **Code Quality**: Linting, type checking, and coverage requirements
- **Related Documentation**: Links to ADRs, SSOT, and other relevant docs

### ADR Standards

Architectural decisions are documented with:

- **Context**: Problem statement and background
- **Decision**: Chosen solution clearly stated
- **Rationale**: Why this solution, with quantified benefits
- **Alternatives**: Other options considered with trade-offs
- **Consequences**: Implementation requirements and risks
- **Status**: Current state (Proposed, Accepted, Rejected, etc.)

### SSOT Standards

Canonical schemas include:

- **Version Information**: Current version and change history
- **Complete Specifications**: All required fields and constraints
- **Examples**: Concrete examples of valid data
- **Validation Rules**: How to verify compliance
- **Change Process**: How to update the schema

## 📊 Phase Index

Current development phases and their documentation:

### Active Phases

| Phase | Status | Documentation | Description |
| ----- | ------ | -------------- | ----------- |
| **Phase 10** | ✅ Completed | `docs/phase10/` + `PHASE10_RETROSPECTIVE.md` | UI acceptance harness, headless validation, performance metrics |
| **Phase 11** | 🚧 Sprint 1 | `PHASE11_PLAN.md` + `.cursor/plans/ui-enhancement-*.plan.md` | Unified envelope, virtual graph chunking (10k→100k) |

### Phase Navigation

- **Phase 10 Retrospective**: `docs/PHASE10_RETROSPECTIVE.md` - wins, learnings, follow-ups
- **Phase 11 Breadcrumb**: `docs/PHASE11_PLAN.md` - current sprint decisions & success criteria
- **Implementation Plans**: `.cursor/plans/` - detailed Cursor-generated development plans
- **SSOT Schemas**: `docs/SSOT/` - contracts for unified envelope validation

## 🔍 Finding Documentation

### By Topic

- **Setup/Installation**: Root `README.md` and AGENTS.md
- **Architecture**: ADR files in `docs/ADRs/`
- **API Contracts**: SSOT files in `docs/SSOT/`
- **Development**: AGENTS.md files in source directories
- **Usage Examples**: README.md files throughout the codebase
- **Current Phase**: See Phase Index above

### By Directory

- **Source Code**: Each `src/` subdirectory has README.md + AGENTS.md
- **Scripts**: `scripts/README.md` + `scripts/AGENTS.md`
- **Tests**: `tests/README.md` + `tests/AGENTS.md`
- **Documentation**: This file (`docs/README.md`) + `docs/AGENTS.md`

## 📈 Quality Metrics

### Coverage Requirements

- **README.md**: Every directory (100% coverage)
- **AGENTS.md**: Source code directories (80%+ coverage)
- **ADR**: All architectural decisions documented
- **SSOT**: All schemas and contracts specified
- **Cross-References**: Bidirectional linking between documents

### Validation Gates

| Gate                     | Description                               | Rule                     |
| ------------------------ | ----------------------------------------- | ------------------------ |
| **Documentation Sync**   | Pre-PR validation ensures docs match code | 009 — Documentation Sync |
| **Metrics Verification** | Enforces real data & export consistency   | 021 — Stats Proof        |
| **CI/CD**                | Automated documentation checks            | 007 — Infrastructure     |
| **Release**              | Complete documentation review             | —                        |
| **Audit**                | Periodic documentation quality assessment | —                        |

## 🤝 Contributing to Documentation

### Adding Documentation

1. **Identify Need**: Determine what documentation is missing
2. **Choose Format**: README.md for users, AGENTS.md for AI, ADR for architecture, SSOT for schemas
3. **Follow Templates**: Use established patterns and structures
4. **Cross-Reference**: Link to related documentation
5. **Validate**: Run sync checks to ensure completeness

### Improving Documentation

1. **Review Current State**: Assess existing documentation quality
2. **Identify Gaps**: Find missing information or unclear explanations
3. **Update Content**: Improve clarity, accuracy, and completeness
4. **Add Examples**: Include practical usage examples
5. **Test Changes**: Validate that updates improve understanding

### Documentation Maintenance

1. **Monitor Changes**: Track code changes that affect documentation
2. **Update References**: Fix broken links and outdated information
3. **Review Regularly**: Periodic review of documentation accuracy
4. **Gather Feedback**: Incorporate user and developer feedback
5. **Version Updates**: Ensure documentation matches code versions

## 🎯 Documentation Goals

### User Experience

- **Discoverability**: Easy to find relevant information
- **Clarity**: Clear, concise, and accurate explanations
- **Completeness**: All necessary information provided
- **Consistency**: Uniform style and structure across documents

### Developer Experience

- **Guidance**: Clear development patterns and practices
- **Automation**: Tools to maintain documentation quality
- **Integration**: Documentation built into development workflow
- **Evolution**: Documentation that grows with the codebase

### System Understanding

- **Architecture**: Clear system structure and component relationships
- **Decisions**: Rationales behind important technical choices
- **Contracts**: Precise interface specifications
- **Evolution**: Historical context for system changes

## 📚 Related Documentation

- **Root README.md**: Project overview and getting started
- **AGENTS.md**: AI assistant development guide (this directory)
- **ADR-013**: Documentation synchronization requirements
- **SSOT Directory**: Schema and contract definitions

## Architectural Decision Records

# Architectural Decision Records (ADRs)

Total ADRs: 33

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [docs/ADRs/ADR-000-langgraph.md](docs/ADRs/ADR-000-langgraph.md) | ADR-000: Orchestration via LangGraph (StateGraph) | Accepted | Unknown |
| [docs/ADRs/ADR-001-two-db.md](docs/ADRs/ADR-001-two-db.md) | ADR-001: Two-DB Safety (bible_db RO; gematria RW) | Accepted | Unknown |
| [docs/ADRs/ADR-002-gematria-rules.md](docs/ADRs/ADR-002-gematria-rules.md) | ADR-002: Gematria and Normalization Rules | Accepted | Unknown |
| [docs/ADRs/ADR-003-batch-semantics.md](docs/ADRs/ADR-003-batch-semantics.md) | ADR-003: Batch Semantics & Validation Gates | Unknown | Unknown |
| [docs/ADRs/ADR-004-postgres-checkpointer.md](docs/ADRs/ADR-004-postgres-checkpointer.md) | ADR-004: Postgres Checkpointer with BaseCheckpointSaver Interface | Unknown | Unknown |
| [docs/ADRs/ADR-005-metrics-logging.md](docs/ADRs/ADR-005-metrics-logging.md) | ADR-005: Metrics & Structured Logging | Accepted | Unknown |
| [docs/ADRs/ADR-006-observability-dashboards.md](docs/ADRs/ADR-006-observability-dashboards.md) | ADR-006: Observability Dashboards & Queries | Accepted | Unknown |
| [docs/ADRs/ADR-007-llm-integration.md](docs/ADRs/ADR-007-llm-integration.md) | ADR-007: LLM Integration and Confidence Metadata | Accepted | Unknown |
| [docs/ADRs/ADR-008-confidence-validation.md](docs/ADRs/ADR-008-confidence-validation.md) | ADR-008: Confidence-Aware Batch Validation | Accepted | Unknown |
| [docs/ADRs/ADR-009-semantic-aggregation.md](docs/ADRs/ADR-009-semantic-aggregation.md) | ADR-009: Semantic Aggregation & Network Analysis | Accepted | Unknown |
| [docs/ADRs/ADR-010-qwen-integration.md](docs/ADRs/ADR-010-qwen-integration.md) | ADR-010: Qwen3 Integration for Real Semantic Intelligence | Accepted | Unknown |
| [docs/ADRs/ADR-011-concept-network-verification.md](docs/ADRs/ADR-011-concept-network-verification.md) | ADR-011: Concept Network Health Verification Views | Accepted | Unknown |
| [docs/ADRs/ADR-012-concept-network-dimension-fix.md](docs/ADRs/ADR-012-concept-network-dimension-fix.md) | ADR-012: Concept Network Vector Dimension Correction | Accepted | Unknown |
| [docs/ADRs/ADR-013-documentation-sync-enhancement.md](docs/ADRs/ADR-013-documentation-sync-enhancement.md) | ADR-013: Comprehensive Documentation Synchronization Enhancement | Accepted | Unknown |
| [docs/ADRs/ADR-014-relations-and-pattern-discovery.md](docs/ADRs/ADR-014-relations-and-pattern-discovery.md) | ADR-014: Relations & Pattern Discovery | Accepted | Unknown |
| [docs/ADRs/ADR-015-jsonld-and-visualization.md](docs/ADRs/ADR-015-jsonld-and-visualization.md) | ADR-015: JSON-LD & RDF Graph Exports + Visualization Interface | Proposed | Unknown |
| [docs/ADRs/ADR-016-insight-metrics-and-ontology.md](docs/ADRs/ADR-016-insight-metrics-and-ontology.md) | ADR-016: Insight Metrics & Ontology Enrichment | Accepted | Unknown |
| [docs/ADRs/ADR-017-agent-documentation-presence.md](docs/ADRs/ADR-017-agent-documentation-presence.md) | ADR-017: Agent Documentation Presence Enforcement | Accepted | Unknown |
| [docs/ADRs/ADR-018-pattern-correlation.md](docs/ADRs/ADR-018-pattern-correlation.md) | ADR-018: Pattern Correlation Engine | Accepted | Unknown |
| [docs/ADRs/ADR-019-forest-governance.md](docs/ADRs/ADR-019-forest-governance.md) | ADR-019: Forest Governance & Phase Gate System | Accepted | Unknown |
| [docs/ADRs/ADR-020-ontology-forward-compatibility.md](docs/ADRs/ADR-020-ontology-forward-compatibility.md) | ADR-020: Ontology Forward Compatibility | Accepted | Unknown |
| [docs/ADRs/ADR-021-metrics-contract-synchronization.md](docs/ADRs/ADR-021-metrics-contract-synchronization.md) | ADR-021: Metrics Contract Synchronization | Accepted | Unknown |
| [docs/ADRs/ADR-022-cross-text-pattern-analysis.md](docs/ADRs/ADR-022-cross-text-pattern-analysis.md) | ADR-022: Cross-Text Pattern Analysis | Accepted | Unknown |
| [docs/ADRs/ADR-022-system-enforcement-bridge.md](docs/ADRs/ADR-022-system-enforcement-bridge.md) | ADR-022: System Enforcement Bridge | Accepted | Unknown |
| [docs/ADRs/ADR-023-visualization-api-and-dashboard.md](docs/ADRs/ADR-023-visualization-api-and-dashboard.md) | ADR-023: Visualization API and Dashboard | Accepted | Unknown |
| [docs/ADRs/ADR-025-multi-temporal-analytics.md](docs/ADRs/ADR-025-multi-temporal-analytics.md) | ADR-025: Multi-Temporal Analytics & Predictive Patterns | Accepted | Unknown |
| [docs/ADRs/ADR-026-reranker-bi-encoder-proxy.md](docs/ADRs/ADR-026-reranker-bi-encoder-proxy.md) | ADR-026: Reranker Bi-Encoder Proxy Implementation | Accepted | Unknown |
| [docs/ADRs/ADR-032-bibledb-as-SSOT-roadmap.md](docs/ADRs/ADR-032-bibledb-as-SSOT-roadmap.md) | ADR-032: bible_db as Single Source of Truth (Roadmap) | Proposed | Unknown |
| [docs/ADRs/ADR-033-ai-nouns-ssot-contract.md](docs/ADRs/ADR-033-ai-nouns-ssot-contract.md) | ADR-033: AI Nouns SSOT Contract (v1) | Accepted | Unknown |
| [docs/ADRs/ADR-034-uuid-key-evolution.md](docs/ADRs/ADR-034-uuid-key-evolution.md) | ADR-034: UUID Key Evolution and FK Realignment | Proposed | Unknown |
| [docs/ADRs/ADR-055-auto-docs-sync-ci.md](docs/ADRs/ADR-055-auto-docs-sync-ci.md) | ADR-055: Auto-Docs Sync CI Enforcement | Proposed | Unknown |
| [docs/ADRs/ADR-056-auto-housekeeping-ci.md](docs/ADRs/ADR-056-auto-housekeeping-ci.md) | ADR-056: Auto-Housekeeping CI Enforcement | Proposed | Unknown |
| [docs/ADRs/ADR-057-context-persistence-ci.md](docs/ADRs/ADR-057-context-persistence-ci.md) | ADR-057: Context Persistence CI Enforcement | Proposed | Unknown |

