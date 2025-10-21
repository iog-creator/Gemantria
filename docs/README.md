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

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Database Architecture & Safety | Accepted |
| ADR-002 | Gematria Calculation Rules | Accepted |
| ADR-013 | Documentation Synchronization | Accepted |
| ADR-015 | JSON-LD & Visualization | Accepted |

### SSOT (Canonical Schemas)

| Schema | Purpose | Format |
|--------|---------|--------|
| `jsonld-schema.md` | JSON-LD export format specification | Markdown |
| `rdf-ontology.md` | RDF vocabulary definitions | Turtle snippets |
| `webui-contract.md` | Frontend-backend data contracts | JSON schemas |
| `graph-stats-api.md` | Statistics API specification | JSON examples |

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

## 🔍 Finding Documentation

### By Topic

- **Setup/Installation**: Root `README.md` and AGENTS.md
- **Architecture**: ADR files in `docs/ADRs/`
- **API Contracts**: SSOT files in `docs/SSOT/`
- **Development**: AGENTS.md files in source directories
- **Usage Examples**: README.md files throughout the codebase

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

| Gate | Description | Rule |
|------|-------------|------|
| **Documentation Sync** | Pre-PR validation ensures docs match code | 009 — Documentation Sync |
| **Metrics Verification** | Enforces real data & export consistency | 021 — Stats Proof |
| **CI/CD** | Automated documentation checks | 007 — Infrastructure |
| **Release** | Complete documentation review | — |
| **Audit** | Periodic documentation quality assessment | — |

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
