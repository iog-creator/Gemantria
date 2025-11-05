# AGENTS.md - Architectural Decision Records Directory

## Directory Purpose

The `docs/ADRs/` directory contains Architectural Decision Records that document significant design decisions, trade-offs, and rationales for the Gemantria project. ADRs ensure maintainability and knowledge transfer.

## ADR Sequence & Organization

### Current ADR Sequence

- **ADR-000**: LangGraph adoption for pipeline orchestration
- **ADR-001**: Two-database architecture (Bible + Gematria)
- **ADR-002**: Hebrew normalization and gematria calculation rules
- **ADR-003**: Batch processing semantics and validation gates
- **ADR-004**: Postgres checkpointer for resumable execution
- **ADR-005**: Metrics logging and structured observability
- **ADR-006**: Observability dashboards and monitoring views
- **ADR-007**: LLM integration with LM Studio
- **ADR-008**: Confidence validation and quality gates
- **ADR-009**: Semantic aggregation and network building
- **ADR-010**: Qwen integration with embedding models
- **ADR-011**: Concept network health verification views
- **ADR-012**: Concept network vector dimension correction
- **ADR-013**: Comprehensive documentation synchronization enhancement
- **ADR-015**: JSON-LD and visualization exports
- **ADR-016**: Insight metrics and ontology
- **ADR-017**: Agent documentation presence enforcement
- **ADR-018**: Pattern correlation engine
- **ADR-019**: Forest governance & phase gate system
- **ADR-020**: Ontology forward compatibility
- **ADR-021**: Metrics contract synchronization
- **ADR-022**: System enforcement bridge
- **ADR-025**: Multi-temporal analytics and predictive patterns

### Naming Convention

**Format**: `ADR-XXX-descriptive-title.md`

- **XXX**: Zero-padded number (001, 002, etc.)
- **descriptive-title**: Hyphen-separated, URL-friendly
- **Example**: `ADR-010-qwen-integration.md`

## ADR Lifecycle Management

### Status Values

- **Proposed**: Initial draft, under discussion
- **Accepted**: Approved for implementation
- **Rejected**: Considered but not chosen
- **Deprecated**: No longer relevant
- **Superseded**: Replaced by newer ADR (reference new one)

### Decision Categories

#### Architecture Decisions

- System component design and relationships
- Data flow and processing patterns
- External service integration strategies
- Scalability and performance approaches

#### Technical Decisions

- Programming language and framework choices
- Database schema and indexing strategies
- API design and interface contracts
- Algorithm selection and optimization

#### Process Decisions

- Development workflow and tooling
- Testing strategy and quality gates
- Deployment and operational procedures
- Documentation and knowledge management

#### Dependency Decisions

- External library and service adoption
- Version compatibility and upgrade paths
- Licensing and security considerations
- Maintenance and support planning

## ADR Content Standards

### Required Sections

```markdown
# ADR-XXX: [Clear, Actionable Title]

## Status

[Current status from lifecycle]

## Housekeeping (Rule 058)

After ANY code changes in this directory, run comprehensive housekeeping:

```bash
# Rule 058 mandatory housekeeping checklist
python3 scripts/rules_audit.py
make share.sync
python3 scripts/generate_forest.py
ruff format --check . && ruff check .
# Check if ADR needed/updated (Rule 029)
PYTHONPATH=. python3 -m pytest tests/ -v --tb=short
# Verify docs updated (AGENTS.md, SSOT, README)
```

**DO NOT SKIP ANY STEP.** See [Rule 058](../../.cursor/rules/058-auto-housekeeping.mdc) for complete checklist.


## Related ADRs

[Links to related architectural decisions]

## Related Rules

[Links to cursor rules implementing or enforcing this decision]

## Context

[Problem statement, constraints, requirements]

## Decision

[Chosen solution, clearly stated]

## Rationale

[Why chosen, benefits, trade-offs]

## Alternatives Considered

[Other options with pros/cons]

## Consequences

[Implementation requirements, risks, follow-ups]

## Notes

[Additional context, references, future considerations]
```

### Cross-Referencing Requirements

- **Related ADRs**: All ADRs must reference related decisions with direct links
- **Related Rules**: ADRs must link to cursor rules that implement or enforce the decision
- **Implementation Links**: ADRs should reference PRs, issues, and code changes
- **Status Dependencies**: ADRs should indicate prerequisite ADRs that must be accepted first

### Quality Criteria

- **Context**: Sufficient background for decision understanding
- **Decision**: Clear, unambiguous statement of choice
- **Rationale**: Logical explanation with quantified benefits
- **Alternatives**: Fair evaluation of other options
- **Consequences**: Realistic assessment of impacts

## ADR Maintenance Workflow

### Creating New ADRs

1. **Identify Decision**: Recognize need for architectural choice
2. **Draft ADR**: Follow template with comprehensive analysis
3. **Socialize**: Share with team for feedback and refinement
4. **Finalize**: Incorporate feedback and mark status
5. **Implement**: Track implementation in related issues/PRs

### Updating Existing ADRs

1. **Context Change**: Monitor for invalidating conditions
2. **Status Update**: Mark deprecated/superseded as needed
3. **Reference Updates**: Ensure links remain accurate
4. **Implementation Drift**: Update when code diverges from decision

### ADR Review Process

1. **Technical Review**: Validate technical accuracy
2. **Stakeholder Review**: Ensure alignment with goals
3. **Implementation Review**: Verify feasibility and requirements
4. **Documentation Review**: Check clarity and completeness

## ADR Discovery & Usage

### Finding Relevant ADRs

- **By Topic**: Search ADR titles and content
- **By Status**: Filter by current/rejected/proposed
- **By Component**: Cross-reference with code areas
- **By Timeline**: Chronological decision evolution

### Using ADRs in Development

- **New Features**: Check for conflicting or related decisions
- **Refactoring**: Understand original design intent
- **Onboarding**: Learn system architecture and rationale
- **Troubleshooting**: Understand trade-offs and constraints

## ADR Analytics & Insights

### Decision Patterns

- **Common Themes**: Identify recurring decision types
- **Success Metrics**: Track implementation success rates
- **Learning Opportunities**: Analyze rejected decisions

### Quality Metrics

- **Completeness**: Required sections present and filled
- **Clarity**: Decision and rationale clearly stated
- **Relevance**: Current applicability to codebase
- **Maintenance**: Regular updates and status changes

## Tooling & Automation

### ADR Management Tools

- **Templates**: Standardized document structure
- **Validation**: Automated quality and completeness checks
- **Search**: Full-text search across ADR corpus
- **Linking**: Cross-reference between related ADRs

### Integration Points

- **PR Templates**: Reference relevant ADRs
- **Code Comments**: Link to decision rationale
- **Documentation**: ADR references in guides
- **Reviews**: ADR compliance checking

## ADR Evolution Tracking

### Version History

- **Git History**: Track ADR content changes
- **Status Changes**: Log decision lifecycle events
- **Implementation Links**: Connect to code changes

### Future Considerations

- **ADR 2.0**: Potential format improvements
- **Automation**: Enhanced tooling and validation
- **Integration**: Deeper CI/CD and development workflow integration

## ADR Community & Culture

### Decision-Making Culture

- **Collaborative**: Team input on significant decisions
- **Documented**: All architectural choices recorded
- **Transparent**: Rationale and trade-offs visible
- **Accountable**: Decision ownership and follow-through

### Knowledge Sharing

- **Onboarding**: ADRs as architectural learning resource
- **Mentoring**: Decision-making pattern examples
- **Documentation**: System understanding and maintenance
- **Innovation**: Foundation for future architectural work
