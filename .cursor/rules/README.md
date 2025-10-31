# Cursor IDE Configuration Rules

This directory contains Cursor IDE configuration rules that enforce development standards, code quality, and project-specific policies. These rules automatically apply to relevant files and provide real-time guidance during development.

## 🎯 Purpose

The rules directory serves as the enforcement layer for:

- **Code Quality Standards**: Automatic linting and formatting requirements
- **Project Policies**: Domain-specific rules for the Gemantria project
- **Development Workflow**: IDE-assisted enforcement of best practices
- **Safety Gates**: Critical validation rules that prevent common errors
- **Documentation Requirements**: Automatic checking of documentation completeness

## 📋 Rule Categories

### Global Rules (Always Applied)

#### `000-always-apply.mdc` - Core Project Constraints

**Scope**: All files in the project
**Purpose**: Fundamental rules that always apply regardless of file type
**Contents**:

- Code gematria takes priority over bible_db and LLM (LLM = metadata only)
- Bible database is read-only with enforced safety
- No mock datasets in production code
- Hebrew normalization standards
- Gematria calculation rules (Mispar Hechrachi, finals=regular)
- Identity standards (content_hash SHA-256, uuidv7 surrogates)
- Batch processing semantics (50 nouns default, ALLOW_PARTIAL=1 explicit)
- Network standards (pgvector embeddings, cosine similarity thresholds)
- Qwen Live Gate requirements

### Database & Safety Rules

#### `001-db-safety.mdc` - Database Safety & SQL Discipline

**Scope**: Database operations and SQL queries
**Purpose**: Prevent SQL injection and ensure safe database access
**Enforcement**:

- Parameterized queries only (no f-string SQL)
- Connection pooling requirements
- Transaction management standards
- Schema validation checks

### Validation Rules

#### `002-gematria-validation.mdc` - Hebrew & Gematria Validation

**Scope**: Text processing and gematria calculation code
**Purpose**: Ensure correct Hebrew handling and mathematical accuracy
**Enforcement**:

- Unicode normalization verification (NFKD → NFC)
- Maqaf and punctuation stripping requirements
- Gematria calculation accuracy checks
- Final letter form handling validation

### Processing Rules

#### `003-graph-and-batch.mdc` - Graph Processing & Batch Semantics

**Scope**: Pipeline orchestration and batch processing
**Purpose**: Ensure correct graph construction and batch handling
**Enforcement**:

- Batch size validation (50 nouns default)
- ALLOW_PARTIAL=1 explicit requirement for deviations
- Graph construction standards
- Batch failure handling requirements

### Workflow Rules

#### `004-pr-workflow.mdc` - Pull Request Workflow Standards

**Scope**: Git operations and PR management
**Purpose**: Standardize development workflow and collaboration
**Enforcement**:

- Branch naming conventions
- Commit message standards
- PR template requirements
- Review process guidelines

#### `005-github-operations.mdc` - GitHub Operations Safety

**Scope**: GitHub API interactions and MCP server usage
**Purpose**: Safe and effective GitHub operations via MCP
**Enforcement**:

- Ownership verification requirements
- Search before creation policies
- MCP server usage standards
- Issue/PR management protocols

### Infrastructure Rules

#### `006-agents-md-governance.mdc` - AGENTS.md Governance

**Scope**: AGENTS.md file management and maintenance
**Purpose**: Ensure AI assistant documentation quality
**Enforcement**:

- AGENTS.md presence requirements
- Content quality standards
- Update synchronization rules
- Cross-reference validation

#### `007-infrastructure.mdc` - Infrastructure & Checkpointer Safety

**Scope**: Infrastructure components and state management
**Purpose**: Reliable infrastructure operation and state persistence
**Enforcement**:

- Checkpointer configuration requirements
- Infrastructure monitoring standards
- State persistence guarantees
- Recovery mechanism validation

#### `008-cursor-rule-authoring.mdc` - Rule Authoring Standards

**Scope**: Rule file creation and maintenance
**Purpose**: Consistent and effective rule authoring
**Enforcement**:

- Rule file format standards
- Globbing pattern best practices
- Rule naming conventions
- Documentation requirements

### Semantic & AI Rules

#### `010-semantic-network.mdc` - Semantic Network Standards

**Scope**: Embedding generation and semantic processing
**Purpose**: Ensure high-quality semantic network construction
**Enforcement**:

- Embedding dimensionality requirements (1024-dim)
- Normalization standards (L2 normalized)
- Similarity threshold validation
- Network quality metrics

#### `011-production-safety.mdc` - Production Safety & Live Model Enforcement

**Scope**: Production deployments and AI model interactions
**Purpose**: Production safety with Qwen Live Gate enforcement
**Enforcement**:

- Qwen Live Gate requirements (ENFORCE_QWEN_LIVE=1)
- Health check verification
- Model availability validation
- Production mock prohibitions

### Connectivity & Troubleshooting

#### `012-connectivity-troubleshooting.mdc` - External Service Handling

**Scope**: External API interactions and connectivity
**Purpose**: Robust external service integration
**Enforcement**:

- Timeout configuration standards
- Retry logic requirements
- Error handling patterns
- Connection pooling guidelines

### Quality Assurance

#### `013-report-generation-verification.mdc` - Report Generation Verification

**Scope**: Report generation and validation scripts
**Purpose**: Ensure reports contain real data, not placeholders
**Enforcement**:

- Real data verification requirements
- Template compliance validation
- Database query result checking
- Timestamp accuracy verification

### Export & Integration

#### `015-semantic-export-compliance.mdc` - Semantic Export Compliance

**Scope**: JSON-LD and RDF export scripts
**Purpose**: Ensure semantic web standards compliance
**Enforcement**:

- rdflib import verification
- JSON-LD @context validation
- RDF/Turtle syntax checking
- URI namespace compliance

#### `016-visualization-contract-sync.mdc` - Visualization Contract Sync

**Scope**: WebUI components and data contracts
**Purpose**: Maintain frontend-backend data contract consistency
**Enforcement**:

- Required field validation
- TypeScript interface compliance
- Data loading contract verification
- Error handling standardization

#### `017-agent-docs-presence.mdc` - Agent Documentation Presence

**Scope**: Directory structure and AGENTS.md files
**Purpose**: Ensure comprehensive AI assistant documentation coverage
**Enforcement**:

- AGENTS.md presence in source directories
- Related ADRs table requirements
- Directory classification accuracy
- Documentation completeness validation

#### `018-ssot-linkage.mdc` - SSOT Documentation Linkage

**Scope**: ADRs, SSOT docs, and cross-references
**Purpose**: Maintain bidirectional documentation relationships
**Enforcement**:

- ADR to SSOT reference requirements
- SSOT to ADR linkage validation
- Cross-reference consistency checking
- Link accuracy verification

## 🔧 Rule File Format

### Structure

Each rule file follows the Markdown Cursor (`.mdc`) format:

```mdc
---
description: Brief description of the rule's purpose
globs:
  - path/patterns/where/rule/applies
alwaysApply: true/false
---

# Rule content in Markdown format
# Enforcement criteria, examples, rationale
```

### Key Components

- **Description**: Clear, actionable summary of the rule's purpose
- **Globs**: File patterns where the rule should be applied
- **Always Apply**: Whether the rule applies universally or conditionally
- **Content**: Detailed enforcement criteria, examples, and rationale

## 📊 Rule Application

### Automatic Application

Rules are automatically applied by Cursor IDE based on:

- **File Path Matching**: Glob patterns determine which files get which rules
- **Context Awareness**: Rules activate based on file content and project structure
- **Real-time Enforcement**: Immediate feedback during editing
- **Severity Levels**: Warnings vs. errors based on rule criticality

### Manual Verification

Rules can be manually verified using:

```bash
# Run documentation sync validation
./scripts/test_docs_sync_rule.sh

# Check specific rule compliance
# (Rules are enforced by Cursor IDE during development)
```

## 🎯 Rule Development

### Creating New Rules

See the comprehensive guide in the main [AGENTS.md](../../AGENTS.md#how-agents-should-use-rules) for detailed instructions on when and how to create Cursor rules, including:

- **When to Create Rules**: Critical safety issues, recurring problems, new standards, process improvements
- **Rule File Structure**: Naming conventions, numbering, and MDC format requirements
- **Glob Patterns**: Guidelines for efficient and effective file targeting
- **Always Apply Logic**: When to use global vs. conditional rules
- **Complete Workflow**: Step-by-step rule creation and validation process

### Rule Maintenance

1. **Monitor Effectiveness**: Track rule violation patterns and developer feedback
2. **Update Content**: Modify rules as project standards evolve
3. **Version Control**: Rules are versioned with project code via git
4. **Cross-Reference**: Ensure rules reference relevant ADRs and documentation
5. **Performance**: Monitor IDE impact and optimize glob patterns for efficiency

## 🔍 Rule Categories by Impact

### Critical Safety (Always Apply)

- Database safety and SQL discipline
- Qwen Live Gate and AI model verification
- Production mock prohibitions
- Core project constraints

### Quality Assurance (High Priority)

- Documentation synchronization requirements
- Code quality and linting standards
- Testing coverage requirements
- Schema validation rules

### Development Workflow (Medium Priority)

- PR workflow and GitHub operations
- Branch naming and commit standards
- Infrastructure configuration requirements
- External service integration patterns

### Optimization (Low Priority)

- Performance monitoring and alerting
- Report generation verification
- Visualization contract synchronization
- Semantic export compliance

## 📚 Documentation

- **Rule Authoring Guide**: See `008-cursor-rule-authoring.mdc`
- **Documentation Sync**: See `009-documentation-sync.mdc`
- **ADR References**: ADR-013 covers rule system design
- **Parent Directory**: See `.cursor/README.md` for IDE configuration overview

## 🤝 Development Guidelines

### Rule Writing Standards

- **Clear Purpose**: Each rule should have a single, clear objective
- **Actionable Guidance**: Rules should provide specific, actionable requirements
- **Evidence-Based**: Rules should be based on real project needs and issues
- **Maintainable**: Rules should be easy to understand and modify as needed

### Rule Organization

- **Logical Grouping**: Related rules should be numbered sequentially
- **Consistent Naming**: Use descriptive, consistent naming patterns
- **Progressive Numbering**: New rules get the next available number
- **Deprecation Handling**: Clearly mark deprecated rules and their replacements

### Rule Effectiveness

- **Measurable Impact**: Rules should address real problems or prevent real issues
- **Balanced Enforcement**: Rules should provide value without being overly restrictive
- **User-Friendly**: Rules should provide helpful guidance, not just restrictions
- **Regular Review**: Rules should be reviewed periodically for continued relevance

### Integration with Workflow

- **IDE Integration**: Rules work seamlessly within the development environment
- **CI/CD Compatibility**: Rules align with automated quality checks
- **Team Alignment**: Rules reflect and reinforce team standards and practices
- **Evolution Support**: Rules can evolve as the project and team mature
