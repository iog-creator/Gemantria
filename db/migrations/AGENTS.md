# AGENTS.md - Migrations Directory

## Directory Purpose

The `migrations/` directory contains database schema migration scripts for the Gematria analysis system.
These migrations ensure consistent database schema evolution across development and production environments.

## Migration Scripts

<!-- Document migration files and their purposes here -->

## Migration Standards

### File Naming
- Format: `NNN_description.sql` where NNN is sequential number
- Examples: `001_initial_schema.sql`, `002_create_checkpointer.sql`

### Content Standards
- **Transactional**: Each migration should be wrapped in a transaction
- **Idempotent**: Safe to run multiple times
- **Rollback**: Include rollback instructions in comments
- **Tested**: Verified against clean database state

### Execution Order
- Migrations run in numerical order
- No gaps in numbering allowed
- Each migration depends on the previous state

## Development Guidelines

### Creating New Migrations
1. **Check Current State**: Review existing migrations
2. **Sequential Numbering**: Use next available number
3. **Clear Description**: Descriptive name for the change
4. **Test Locally**: Apply and rollback on development database
5. **Document Changes**: Update this AGENTS.md file

### Migration Testing
1. **Clean Apply**: Test on empty database
2. **Incremental Apply**: Test on database with previous migrations
3. **Rollback Test**: Verify rollback works correctly
4. **Data Preservation**: Ensure no data loss during migration

## Related ADRs

| Migration | Related ADRs | Description |
|-----------|--------------|-------------|
<!-- Add migration to ADR mappings here -->
