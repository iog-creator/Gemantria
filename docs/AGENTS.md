# AGENTS.md - Documentation Directory

## Directory Purpose
The `docs/` directory contains all project documentation including architectural decision records (ADRs), guides, and reference materials. This documentation ensures maintainability and knowledge transfer.

## Directory Structure

### `ADRs/` - Architectural Decision Records
**Purpose**: Record important architectural decisions and their rationales
**Naming**: ADR-XXX-descriptive-title.md
**Status**: [Proposed | Accepted | Rejected | Deprecated | Superseded]
**Template**: adr-template.md provides standard structure

### Root Documentation Files
**Purpose**: Project-level guides and reference materials
- **README.md**: Project overview, setup, and usage
- **MASTER_PLAN.md**: High-level project roadmap and goals
- **qwen_integration.md**: LM Studio and Qwen model integration guide

## ADR Guidelines

### When to Create an ADR
- **Schema Changes**: Database structure modifications
- **Architecture Decisions**: Major design pattern changes
- **Dependency Changes**: New external libraries or services
- **Process Changes**: Development workflow modifications
- **Performance Decisions**: Significant optimization choices

### ADR Structure
```markdown
# ADR-XXX: [Decision Title]

## Status
[Accepted | Proposed | Rejected]

## Context
[Problem description and constraints]

## Decision
[Chosen solution clearly stated]

## Rationale
[Why this solution, benefits, trade-offs]

## Alternatives Considered
[Other options and why rejected]

## Consequences
[Positive and negative outcomes]

## Implementation Requirements
[What needs to be done]

## Related ADRs
[Links to related decisions]

## Notes
[Additional context or future considerations]
```

### ADR Lifecycle
1. **Draft**: Initial proposal with context and options
2. **Review**: Team feedback and refinement
3. **Accepted**: Implementation approved and tracked
4. **Implemented**: Changes deployed and verified
5. **Superseded**: Replaced by newer decision (reference new ADR)

## Documentation Standards

### Writing Guidelines
- **Clear**: Use simple language, avoid jargon
- **Complete**: Include all necessary context and examples
- **Current**: Update when implementation changes
- **Consistent**: Follow established patterns and templates

### Maintenance Responsibilities
- **Authors**: Keep documentation current with code changes
- **Reviewers**: Validate documentation accuracy in PRs
- **Team**: Use documentation for decision making and onboarding

## Key Documentation Areas

### Setup & Getting Started
- Environment setup and configuration
- Development workflow and tools
- Testing and quality assurance processes

### Architecture & Design
- System architecture and component relationships
- Data flow and processing pipelines
- External service integrations

### Operational Guides
- Deployment and monitoring procedures
- Troubleshooting common issues
- Performance optimization guidelines

### API & Interface Documentation
- Module interfaces and contracts
- Configuration options and parameters
- Error handling and recovery procedures

## Documentation Tools & Workflow

### Markdown Standards
- **Headers**: Use # ## ### for hierarchy
- **Code**: Inline `code` and fenced code blocks
- **Links**: Reference other docs and ADRs
- **Lists**: Use - for bullets, 1. for numbered

### Review Process
- **PR Integration**: Documentation changes with code changes
- **Peer Review**: Technical accuracy validation
- **Automated Checks**: Link validation, formatting consistency

### Version Control
- **Git History**: Track documentation evolution
- **Branch Strategy**: Documentation updates with feature branches
- **Release Notes**: Highlight significant documentation changes

## Quality Assurance

### Completeness Checks
- [ ] All major components documented
- [ ] Setup instructions verified by new team members
- [ ] Troubleshooting guides cover common issues
- [ ] API documentation matches implementation

### Accuracy Validation
- [ ] Code examples execute successfully
- [ ] Configuration examples work in test environments
- [ ] Performance claims backed by benchmarks
- [ ] Architecture diagrams reflect current implementation

### Maintenance Tracking
- [ ] Documentation updated with code changes
- [ ] Outdated information flagged for updates
- [ ] Missing documentation identified and planned
- [ ] Documentation quality metrics tracked

## Tooling & Automation

### Documentation Generation
- **API Docs**: Auto-generated from code comments
- **Diagrams**: Architecture visualization tools
- **Examples**: Executable code snippets

### Validation Tools
- **Link Checkers**: Validate internal and external links
- **Format Validators**: Ensure consistent markdown formatting
- **Content Linters**: Check for clarity and completeness

### Publishing Pipeline
- **Build Process**: Documentation included in CI/CD
- **Artifact Storage**: Versioned documentation archives
- **Access Control**: Appropriate visibility for different audiences

