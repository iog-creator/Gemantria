# AGENTS.md - Schema Directory

## Directory Purpose

The `docs/schema/` directory contains database schema documentation, JSON schema definitions, and data contract specifications. This directory serves as the Single Source of Truth (SSOT) for data structure definitions used across the Gemantria pipeline.

## Key Documents

### Schema Documentation

- **SCHEMA.md** - Database schema documentation (Phase-1, v6.2.3)
  - Documents `gematria` schema tables and relationships
  - Includes migration strategy and existing migrations
  - Defines DSN roles and database contracts

### JSON Schemas

JSON schema files are stored in the `schemas/` directory (repository root) and define:

- **Graph output schemas**: Node/edge structures for graph exports
- **Export schemas**: Format specifications for pipeline artifacts
- **Envelope schemas**: SSOT envelope structures for data handoffs
- **Analytics schemas**: Statistics and pattern analysis formats

## Documentation Standards

### Schema Documentation Format

All schema documentation should include:

1. **Schema name and version**: Clear identification of schema version
2. **Table/object definitions**: Complete structure with field types and constraints
3. **Relationships**: Foreign keys and referential integrity rules
4. **Indexes**: Performance indexes and unique constraints
5. **Migration history**: Sequential migration files and their purposes

### JSON Schema Standards

- **Versioning**: Include schema version in `$schema` or `version` field
- **Validation**: All JSON exports validated against schemas when available
- **Documentation**: Include field descriptions and examples
- **Backward compatibility**: Document breaking changes and migration paths

### Schema Evolution

- **Additive changes**: Prefer adding fields over removing (forward compatibility)
- **Migration scripts**: All schema changes require migration files
- **Version tracking**: Increment schema versions for breaking changes
- **Deprecation**: Mark deprecated fields but maintain backward compatibility

## Development Guidelines

### Creating Schema Documentation

1. **Document structure**: Define all tables, fields, types, and constraints
2. **Add relationships**: Document foreign keys and referential integrity
3. **Include indexes**: Document performance indexes and unique constraints
4. **Version tracking**: Include schema version and migration history
5. **Update SCHEMA.md**: Add new tables/fields to main schema documentation

### Creating JSON Schemas

1. **Define structure**: Create JSON Schema file in `schemas/` directory
2. **Add validation**: Include field types, required fields, and constraints
3. **Document fields**: Add descriptions and examples for clarity
4. **Version schema**: Include version number in schema definition
5. **Update references**: Link schema in related documentation

### Schema Changes

1. **Create migration**: Add migration file for database schema changes
2. **Update documentation**: Modify SCHEMA.md to reflect changes
3. **Version increment**: Update schema version for breaking changes
4. **Test migration**: Verify migration applies and rolls back cleanly
5. **Update JSON schemas**: Modify JSON schemas if export formats change

## Database Schema Overview

### Core Tables (gematria schema)

- **concepts**: Core concept definitions with Hebrew text and gematria values
- **concept_relations**: Relationships between concepts with weights and evidence
- **concept_centrality**: Graph centrality metrics (degree, betweenness, closeness, eigenvector)
- **concept_network**: Vector embeddings (1024-dim) for semantic relationships
- **concept_clusters**: Cluster assignments and confidence scores

### Migration Strategy

- **Sequential numbering**: Migrations run in numerical order (001, 002, 003...)
- **Idempotent**: Safe to run multiple times (IF NOT EXISTS, ON CONFLICT DO NOTHING)
- **Transactional**: Each migration wrapped in BEGIN/COMMIT
- **Rollback support**: Migrations can be rolled back if needed

### DSN Roles

- **BIBLE_DB_DSN**: Read-only Bible database (enforced at connection level)
- **GEMATRIA_DSN**: Read/write application database for pipeline data
- **AI_AUTOMATION_DSN**: AI tracking database (must equal GEMATRIA_DSN per Rule 064)

## JSON Schema Locations

JSON schemas are stored in `schemas/` directory (repository root):

- **Graph schemas**: `graph_output.schema.json`, `graph_stats.schema.json`
- **Export schemas**: `envelope.schema.json`, `unified_envelope.schema.json`
- **Analytics schemas**: `temporal_patterns.schema.json`, `pattern_forecast.schema.json`
- **Control schemas**: `control_compliance.schema.json` (if applicable)

## Related Documentation

### Database Documentation

- **SCHEMA.md**: Complete database schema documentation
- **migrations/**: Migration files with schema evolution history
- **Rule 001**: DB Safety (read-only Bible DB, parameterized SQL)
- **Rule 037**: Data Persistence Completeness

### JSON Schema Documentation

- **schemas/**: JSON schema files for validation
- **Rule 038**: Exports Smoke Gate (schema validation)
- **Rule 020**: Ontology Forward Compatibility (add-only extensions)

### SSOT Documentation

- **docs/SSOT/**: Single Source of Truth documentation
- **Rule 018**: SSOT Linkage (cross-references between docs)
- **Rule 045**: Rerank Blend is SSOT (edge strength calculation)

## Integration with Governance

### Rule 001 - DB Safety

Schema documentation supports database safety requirements:

- **Read-only enforcement**: Documents Bible DB read-only contract
- **Parameterized SQL**: Schema docs reference parameterized query patterns
- **Migration safety**: Documents migration idempotency and rollback procedures

### Rule 037 - Data Persistence Completeness

Schema documentation ensures complete data persistence:

- **Table definitions**: All pipeline artifacts have corresponding tables
- **Field completeness**: All required fields documented with constraints
- **Relationship integrity**: Foreign keys and referential integrity documented

### Rule 038 - Exports Smoke Gate

JSON schemas support export validation:

- **Schema validation**: All exports validated against JSON schemas
- **Format compliance**: Schemas ensure export format consistency
- **Version tracking**: Schema versions track export format evolution

## Maintenance Notes

- **Keep current**: Update schema docs when database or JSON structures change
- **Version tracking**: Maintain clear version history for schema evolution
- **Migration documentation**: Document all migrations in SCHEMA.md
- **JSON schema updates**: Update JSON schemas when export formats change
- **Cross-reference**: Maintain links between schemas and related governance rules
