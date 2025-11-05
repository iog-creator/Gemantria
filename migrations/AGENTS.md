# AGENTS.md - Database Migrations Directory

## Directory Purpose

The `migrations/` directory contains SQL migration scripts that evolve the database schema over time. Migrations ensure controlled, versioned database changes with rollback capability.

## Migration Types

### Schema Migrations

**Purpose**: Create, modify, or remove database tables, indexes, and constraints
**Examples**:

- `002_create_checkpointer.sql` - LangGraph state persistence
- `007_concept_network.sql` - Semantic network storage
- `010_qwen_health_log.sql` - Model health verification

### Data Migrations

**Purpose**: Transform or populate data as part of schema changes
**Examples**:

- Backfilling computed columns
- Migrating data between table structures
- Populating new required fields

### Index & Performance Migrations

**Purpose**: Optimize query performance and data access patterns
**Examples**:

- `003_metrics_logging.sql` - Metrics storage and indexing
- `004_metrics_views.sql` - Observability views and aggregations

## Migration Naming Convention

### Format: `XXX_description.sql`

- **XXX**: Zero-padded sequential number (001, 002, 003, etc.)
- **description**: Hyphen-separated, descriptive name
- **Examples**:
  - `007_concept_network.sql`
  - `010_qwen_health_log.sql`
  - `013_fix_ai_enrichment_schema.sql`

### Special Suffixes

- **a, b, c**: Sub-migrations for complex changes
  - `012a_concept_network_dim_fix.sql` - Optional dimension correction
- **rollback**: Reverse migration scripts (rarely used)

## Migration Workflow

### Development Process

1. **Identify Change**: Database schema requirement identified
2. **Create Migration**: Write SQL script with proper transactions
3. **Test Locally**: Apply to development database
4. **Peer Review**: SQL review and validation
5. **Deploy**: Apply to staging, then production

### Execution Order

- **Sequential**: Migrations run in numerical order
- **Idempotent**: Safe to run multiple times
- **Transactional**: Wrapped in BEGIN/COMMIT blocks

## Migration Standards

### SQL Best Practices

- **Transactions**: All changes wrapped in explicit transactions
- **Idempotency**: Scripts safe to run multiple times
- **Rollback**: Consider reverse migration path
- **Comments**: Clear documentation of changes and rationale

### Schema Design

- **Naming**: Consistent table/column naming conventions
- **Constraints**: Appropriate primary keys, foreign keys, check constraints
- **Indexes**: Performance-optimized indexing strategy
- **Types**: PostgreSQL-specific types where beneficial

## Migration Categories

### Core Schema (001-005)

- Fundamental tables and relationships
- Checkpointer and metrics infrastructure
- Basic pipeline state storage

### AI & Enrichment (005-006)

- LLM metadata storage
- Confidence validation structures
- Enrichment result persistence

### Semantic Network (007-012)

- Vector embeddings storage
- Concept relationships and similarity
- Network health verification views

### Health & Monitoring (010+)

- Qwen model health tracking
- Performance metrics and logging
- Operational monitoring views

## Migration Safety

### Pre-deployment Checks

- **Backup**: Database backup before migration
- **Testing**: Migration tested on staging environment
- **Rollback Plan**: Reverse migration strategy prepared
- **Monitoring**: Query performance impact assessment

### Risk Mitigation

- **Small Batches**: Break large changes into smaller migrations
- **Feature Flags**: Use feature flags for risky changes
- **Gradual Rollout**: Phased deployment with monitoring
- **Quick Rollback**: Fast reversion capability

## Migration Tools & Automation

### Manual Execution

```bash
# Apply specific migration
psql "$GEMATRIA_DSN" -f migrations/007_concept_network.sql

# Apply all pending migrations (requires migration tool)
# Migration tools like Flyway, Liquibase, or custom scripts
```

### CI/CD Integration

- **Automated Testing**: Migrations tested in CI pipeline
- **Schema Validation**: Post-migration schema verification
- **Data Integrity**: Check data consistency after migration

## Migration Documentation

### Inline Comments

```sql
-- Migration: Add Concept Network Verification Views
-- Purpose: Provide SQL views to verify persistence and dimensional health of embeddings
-- Created: PR-012 Fix Network Persistence (Dims Check, Auto-Commit, Verification View)

BEGIN;
-- View implementation here
COMMIT;
```

### ADR Integration

- **ADR References**: Link migrations to architectural decisions
- **Rationale**: Explain why migration was necessary
- **Impact**: Document performance and functionality changes

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

**DO NOT SKIP ANY STEP.** See [Rule 058](../.cursor/rules/058-auto-housekeeping.mdc) for complete checklist.


## Testing & Validation

### Migration Testing

- **Unit Tests**: Migration logic validation
- **Integration Tests**: Full pipeline with migrated schema
- **Data Tests**: Verify data integrity post-migration

### Schema Validation

- **Consistency**: Foreign key and constraint validation
- **Performance**: Query performance regression testing
- **Compatibility**: Application compatibility with new schema

## Troubleshooting

### Common Issues

- **Lock Conflicts**: Handle concurrent migration execution
- **Data Type Mismatches**: Ensure type compatibility
- **Constraint Violations**: Handle existing data conflicts
- **Performance Degradation**: Monitor query performance impact

### Recovery Procedures

- **Rollback**: Reverse migration when possible
- **Data Repair**: Fix data inconsistencies
- **Schema Repair**: Correct schema drift
- **Communication**: Notify stakeholders of issues

## Migration Maintenance

### Version Control

- **Git History**: Migration evolution tracking
- **Branch Strategy**: Migration scripts with feature branches
- **Review Process**: SQL code review requirements

### Lifecycle Management

- **Deprecation**: Mark old migrations as obsolete
- **Consolidation**: Merge related migrations when safe
- **Archiving**: Move completed migrations to archive
- **Documentation**: Update migration catalog

## Future Considerations

### Migration Tool Adoption

- **Flyway/Liquibase**: Consider adopting migration tools
- **Version Tracking**: Automated migration state management
- **Dependency Management**: Handle migration interdependencies

### Advanced Features

- **Blue-Green**: Zero-downtime migration strategies
- **Canary Deployments**: Gradual migration rollout
- **Automated Testing**: Enhanced migration validation
