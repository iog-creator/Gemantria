# AGENTS.md - ADR Directory

## Directory Purpose

The `docs/adr/` directory contains Architecture Decision Records (ADRs) that document significant architectural decisions, their context, rationale, and consequences. ADRs provide a historical record of why certain technical choices were made and serve as reference documentation for future development.

## Key Documents

### Active ADRs

- **ADR-029: Remove legacy offline scripts** - Deprecates legacy scripts in favor of LangGraph orchestrator
- **ADR-030: DB-seeded noun source for STRICT extraction** - Enables DB-seeded noun discovery for ≥50 noun gate compliance
- **ADR-063: TS Code-Execution Sandbox (PoC)** - TypeScript sandbox for code execution (feature-flagged)
- **ADR-064: RFC3339 Fast-Lane Contract** - Standardizes timestamp format for graph exports (RFC3339)

### ADR Format

All ADRs follow a standard structure:

1. **Context** - The situation and problem being addressed
2. **Decision** - The architectural choice made
3. **Consequences** - Expected outcomes and trade-offs
4. **Verification** - How the decision is validated

## Documentation Standards

### ADR Naming Convention

- **Numbered ADRs**: `029-remove-legacy-scripts.md`, `030-db-seeded-noun-source.md`
- **Named ADRs**: `ADR-063-code-exec-ts.md`, `ADR-064-rfc3339-fast-lane.md`
- **Status**: Include status (Accepted, Proposed, Deprecated) in ADR header

### ADR Content Requirements

- **Clear context**: Explain the problem or situation
- **Explicit decision**: State the chosen approach
- **Consequences documented**: List expected outcomes and trade-offs
- **Verification criteria**: Define how success is measured
- **Related ADRs**: Cross-reference related decisions

### ADR Lifecycle

1. **Proposed** - Initial draft for discussion
2. **Accepted** - Decision finalized and implemented
3. **Deprecated** - Superseded by newer ADR
4. **Superseded** - Replaced by specific ADR number

## Development Guidelines

### When to Create an ADR

Create an ADR when making decisions that:

- **Affect architecture**: Database schema, API contracts, system boundaries
- **Change contracts**: Data formats, protocol specifications, SSOT definitions
- **Impact governance**: Rule changes, workflow modifications, quality gates
- **Introduce new patterns**: Design patterns, integration approaches, tooling choices

### ADR Maintenance

- **Update status**: Mark ADRs as Accepted/Deprecated when appropriate
- **Cross-reference**: Link related ADRs in the "Related ADRs" section
- **Keep current**: Update ADRs when decisions change or are superseded
- **Archive evidence**: Store verification evidence in `share/evidence/` when applicable

### ADR Review Process

1. **Draft ADR**: Create ADR file with Context/Decision/Consequences/Verification
2. **PR review**: Include ADR in PR that implements the decision
3. **Update index**: Add ADR to `RULES_INDEX.md` or governance index if applicable
4. **Archive evidence**: Store verification results in `share/evidence/` directory

## Related ADRs

| Document | Related ADRs | Status |
|----------|--------------|--------|
| ADR-029 | ADR-030 (noun source), ADR-063 (orchestrator) | Accepted |
| ADR-030 | ADR-029 (pipeline), Rule 002 (gematria validation) | Accepted |
| ADR-063 | ADR-029 (orchestrator), Rule 050 (OPS contract) | Accepted |
| ADR-064 | Rule 039 (execution contract), Rule 038 (exports smoke gate) | Accepted |

## Related Documentation

- **Root AGENTS.md**: Repository-wide agent framework
- **RULES_INDEX.md**: Governance rules index (may reference ADRs)
- **MASTER_PLAN.md**: Project plan (may reference ADRs for implementation decisions)
- **Rule 029**: ADR Coverage requirement (new rules/migrations require ADR delta)

## Integration with Governance

### Rule 029 - ADR Coverage

Any new rules or migrations require an ADR delta documenting:

- **Context**: Why the change is needed
- **Decision**: What approach is chosen
- **Consequences**: Expected impact on system
- **Verification**: How compliance is validated

### Rule 018 - SSOT Linkage

All SSOT documents must be linked from ADRs and vice versa:

- **SSOT docs**: Reference relevant ADRs in "Related ADRs" section
- **ADRs**: Link to SSOT schemas and contracts in "Related Documentation"

## Maintenance Notes

- **Keep ADRs current**: Update status when decisions are implemented or superseded
- **Archive evidence**: Store verification results in `share/evidence/` with ADR references
- **Cross-reference**: Maintain links between related ADRs and governance rules
- **Review periodically**: Audit ADRs for accuracy and relevance during governance reviews
