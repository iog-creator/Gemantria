# ADR-011: Concept Network Health Verification Views

## Status
Accepted

## Context
The semantic network functionality requires persistent storage of high-dimensional vector embeddings and their relationships. With the introduction of pgvector for concept network storage, we need mechanisms to verify:

1. **Data Persistence**: Ensure embeddings are properly stored with correct dimensions
2. **Data Integrity**: Validate that stored vectors have consistent dimensionality
3. **Operational Health**: Provide monitoring capabilities for network state
4. **Debugging Support**: Enable quick verification of network storage issues

The pipeline generates embeddings and relationships that must be verified for correctness before being used in downstream analysis.

## Decision
Implement SQL views (`v_concept_network_health` and `v_concept_relations_health`) that provide real-time verification of concept network data integrity and dimensional consistency.

## Rationale
This decision ensures:
- **Reliability**: Immediate detection of storage or dimensional issues
- **Observability**: SQL-based health checks integrated with existing monitoring
- **Debugging**: Quick identification of data quality problems
- **Maintenance**: Proactive monitoring of network health

The views complement the existing database schema by providing read-only verification interfaces that don't impact write performance.

## Alternatives Considered

### Alternative 1: Application-Level Verification
- **Pros**: Flexible validation logic, can be updated without schema changes
- **Cons**: Requires additional application code, increases pipeline complexity
- **Reason Rejected**: Violates separation of concerns; database should own data integrity verification

### Alternative 2: No Verification Views
- **Pros**: Simpler schema, fewer objects to maintain
- **Cons**: No proactive monitoring, harder to debug issues, potential silent failures
- **Reason Rejected**: Essential for production reliability; network data quality is critical

## Consequences

### Positive
- Immediate detection of embedding storage issues
- SQL-based health monitoring integrated with existing observability
- Faster debugging of network persistence problems
- Proactive identification of dimensional inconsistencies

### Negative
- Additional database views to maintain
- Slight increase in schema complexity

### Implementation Requirements
- Create `v_concept_network_health` view for embedding verification
- Create `v_concept_relations_health` view for relationship verification
- Update report generation to use these views
- Add view queries to observability dashboards

## Related ADRs
- ADR-009: Semantic Aggregation (concept network foundation)
- ADR-010: Qwen Integration (embedding generation)
- ADR-006: Observability Dashboards (monitoring integration)

## Notes
Views use pgvector functions (`vector_dims`, `<#>`) for dimensional analysis. Designed to work with existing concept_network and concept_relations tables from ADR-009.

