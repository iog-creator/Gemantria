# AGENTS.md - RFCs Directory

## Directory Purpose

The `docs/rfcs/` directory contains Request for Comments (RFC) documents that propose and document design decisions, integration patterns, and architectural changes for the Gematria analysis system. RFCs serve as design specifications before implementation and provide detailed technical guidance for complex features.

## Key Documents

### Active RFCs

- **RFC-074: Knowledge Sentinels** - Design for knowledge base monitoring and validation
- **RFC-077: Browser Verification Template** - Standardized browser-based verification workflow
- **RFC-078: Postgres Knowledge MCP** - Postgres-based knowledge catalog for MCP integration
- **RFC-079: Guarded Calls Naming** - Naming conventions for guarded function calls
- **RFC-080: LM Studio Control Plane Integration** - LM Studio adapter and health-aware routing design

### RFC Format

All RFCs follow a standard structure:

1. **Summary** - High-level overview of the proposal
2. **Motivation** - Problem statement and rationale
3. **Design** - Detailed technical design and approach
4. **Implementation Plan** - Phased implementation steps
5. **Verification** - How the design is validated
6. **Related Documents** - Links to ADRs, schemas, and related RFCs

## Documentation Standards

### RFC Naming Convention

- **Numbered RFCs**: `RFC-NNN-title.md` where NNN is sequential number
- **Examples**: `RFC-074-knowledge-sentinels.md`, `RFC-080-lm-studio-control-plane-integration.md`
- **Status**: Include status (Draft, Accepted, Implemented, Deprecated) in RFC header

### RFC Content Requirements

- **Clear motivation**: Explain the problem or need being addressed
- **Detailed design**: Provide sufficient technical detail for implementation
- **Implementation plan**: Break down into phases with acceptance criteria
- **Verification criteria**: Define how success is measured
- **Related documents**: Cross-reference ADRs, schemas, and related RFCs

### RFC Lifecycle

1. **Draft** - Initial proposal for review and discussion
2. **Accepted** - Design approved and ready for implementation
3. **Implemented** - Design has been implemented in code
4. **Deprecated** - Superseded by newer RFC or ADR

## Development Guidelines

### When to Create an RFC

Create an RFC when proposing:

- **New integrations**: External service integrations, API designs, protocol specifications
- **Architectural changes**: Significant system design modifications, new patterns
- **Complex features**: Multi-phase implementations requiring detailed planning
- **Control plane changes**: Monitoring, logging, health checks, operational tooling
- **Cross-cutting concerns**: Changes affecting multiple subsystems

### RFC Maintenance

- **Update status**: Mark RFCs as Accepted/Implemented when appropriate
- **Cross-reference**: Link related RFCs, ADRs, and implementation PRs
- **Keep current**: Update RFCs when designs evolve or are superseded
- **Archive evidence**: Store verification evidence in `share/evidence/` when applicable

### RFC Review Process

1. **Draft RFC**: Create RFC file with Summary/Motivation/Design/Implementation/Verification
2. **PR review**: Include RFC in PR that implements the design (or separate design PR)
3. **Update index**: Add RFC to relevant documentation indexes if applicable
4. **Archive evidence**: Store verification results in `share/evidence/` directory

## Related ADRs

| RFC | Related ADRs | Status |
|-----|--------------|--------|
| RFC-074 | ADR-013 (documentation sync), ADR-058 (GPT system prompt) | Draft |
| RFC-077 | Rule 067 (Atlas Webproof), ADR-023 (visualization API) | Accepted |
| RFC-078 | ADR-058 (GPT system prompt), Rule 046 (hermetic CI) | Accepted |
| RFC-079 | Rule 039 (execution contract), Rule 026 (system enforcement) | Accepted |
| RFC-080 | Rule 050 (OPS contract), Rule 051 (cursor insight) | Draft |

## Related Documentation

- **Root AGENTS.md**: Repository-wide agent framework
- **docs/ADRs/AGENTS.md**: Architecture Decision Records (may reference RFCs)
- **docs/SSOT/AGENTS.md**: Single Source of Truth documents (may reference RFC schemas)
- **MASTER_PLAN.md**: Project plan (may reference RFCs for implementation planning)

## Integration with Governance

### Rule 029 - ADR Coverage

RFCs that result in architectural decisions should be followed by ADRs documenting:
- **Context**: RFC provides the design context
- **Decision**: ADR documents the final decision
- **Consequences**: Implementation impacts and trade-offs
- **Verification**: How compliance is validated

### Rule 027 - Docs Sync Gate

RFCs must be updated when:
- **Design changes**: Modifications to the proposed approach
- **Implementation status**: Mark as Implemented when code is merged
- **Related documents**: Update cross-references when ADRs or schemas change

## Maintenance Notes

- **Keep RFCs current**: Update status when designs are implemented or superseded
- **Archive evidence**: Store verification results in `share/evidence/` with RFC references
- **Cross-reference**: Maintain links between RFCs, ADRs, and implementation PRs
- **Review periodically**: Audit RFCs for accuracy and relevance during governance reviews

