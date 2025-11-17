# Control Schema Runbook

## Purpose

The `pmagent control schema` command provides DDL/schema introspection for control-plane tables. It helps operators understand the database structure, column definitions, primary keys, and indexes without requiring direct database access or SQL knowledge.

## Quick Start

### CLI Usage (Primary Interface)

The `pmagent` CLI is the primary interface for control-plane operations:

```bash
# Introspect control-plane table schemas
pmagent control schema

# Or using Python module directly
python -m pmagent.cli control schema
```

### Make Target (Convenience Wrapper)

The Make target is a thin wrapper around `pmagent`:

```bash
make control.schema.smoke
```

Both methods output:
- **JSON** to stdout (machine-friendly)
- **Human-readable summary** to stderr

## Example Outputs

### DB-Off Example

When the database is unavailable (driver missing, connection failed, etc.):

```json
{
  "ok": false,
  "mode": "db_off",
  "reason": "Postgres database driver not available",
  "tables": {}
}
```

```
CONTROL_SCHEMA: mode=db_off (Postgres database driver not available)
```

### DB-On Example (With Schema Information)

When the database is ready and tables are present:

```json
{
  "ok": true,
  "mode": "db_on",
  "reason": null,
  "tables": {
    "control.agent_run": {
      "columns": [
        {
          "name": "id",
          "data_type": "uuid",
          "is_nullable": false,
          "default": "gen_random_uuid()"
        },
        {
          "name": "project_id",
          "data_type": "bigint",
          "is_nullable": false,
          "default": null
        },
        {
          "name": "session_id",
          "data_type": "uuid",
          "is_nullable": true,
          "default": null
        },
        {
          "name": "tool",
          "data_type": "text",
          "is_nullable": false,
          "default": null
        },
        {
          "name": "args_json",
          "data_type": "jsonb",
          "is_nullable": false,
          "default": null
        },
        {
          "name": "result_json",
          "data_type": "jsonb",
          "is_nullable": false,
          "default": null
        },
        {
          "name": "violations_json",
          "data_type": "jsonb",
          "is_nullable": false,
          "default": "[]::jsonb"
        },
        {
          "name": "created_at",
          "data_type": "timestamp with time zone",
          "is_nullable": false,
          "default": "now()"
        }
      ],
      "primary_key": ["id"],
      "indexes": [
        {
          "name": "idx_agent_run_project",
          "columns": ["project_id"],
          "unique": false
        },
        {
          "name": "idx_agent_run_session",
          "columns": ["session_id"],
          "unique": false
        },
        {
          "name": "idx_agent_run_created",
          "columns": ["created_at"],
          "unique": false
        },
        {
          "name": "idx_agent_run_tool",
          "columns": ["tool"],
          "unique": false
        }
      ]
    },
    "public.ai_interactions": {
      "columns": [
        {
          "name": "id",
          "data_type": "integer",
          "is_nullable": false,
          "default": "nextval('ai_interactions_id_seq'::regclass)"
        },
        {
          "name": "session_id",
          "data_type": "character varying",
          "is_nullable": false,
          "default": null
        },
        {
          "name": "interaction_type",
          "data_type": "character varying",
          "is_nullable": false,
          "default": null
        },
        {
          "name": "user_query",
          "data_type": "text",
          "is_nullable": true,
          "default": null
        },
        {
          "name": "ai_response",
          "data_type": "text",
          "is_nullable": true,
          "default": null
        },
        {
          "name": "tools_used",
          "data_type": "ARRAY",
          "is_nullable": true,
          "default": null
        },
        {
          "name": "context_provided",
          "data_type": "jsonb",
          "is_nullable": true,
          "default": null
        },
        {
          "name": "execution_time_ms",
          "data_type": "integer",
          "is_nullable": true,
          "default": null
        },
        {
          "name": "success",
          "data_type": "boolean",
          "is_nullable": true,
          "default": "true"
        },
        {
          "name": "error_details",
          "data_type": "text",
          "is_nullable": true,
          "default": null
        },
        {
          "name": "created_at",
          "data_type": "timestamp with time zone",
          "is_nullable": true,
          "default": "now()"
        }
      ],
      "primary_key": ["id"],
      "indexes": [
        {
          "name": "idx_ai_interactions_session",
          "columns": ["session_id"],
          "unique": false
        },
        {
          "name": "idx_ai_interactions_type",
          "columns": ["interaction_type"],
          "unique": false
        },
        {
          "name": "idx_ai_interactions_created",
          "columns": ["created_at"],
          "unique": false
        }
      ]
    }
  }
}
```

```
CONTROL_SCHEMA: mode=db_on tables=2 columns=19
```

### Partial Schema Example

When some tables exist but others are missing:

```json
{
  "ok": true,
  "mode": "db_on",
  "reason": null,
  "tables": {
    "control.agent_run": {
      "columns": [...],
      "primary_key": ["id"],
      "indexes": [...]
    }
  }
}
```

```
CONTROL_SCHEMA: mode=db_on tables=1 columns=8
```

## Interpreting Results

### Status Fields

- **`ok`**: `true` if database is ready and queries succeeded; `false` if database is unavailable or queries failed
- **`mode`**: Database posture:
  - `"db_on"`: Database is available and queries succeeded
  - `"db_off"`: Database driver missing or connection failed
- **`reason`**: Human-readable explanation of the status (null if ok)

### Table Schema Fields

For each table in the `tables` dictionary:

- **`columns`**: Array of column definitions, each with:
  - **`name`**: Column name
  - **`data_type`**: PostgreSQL data type (e.g., `uuid`, `bigint`, `text`, `jsonb`, `timestamp with time zone`)
  - **`is_nullable`**: `true` if column allows NULL, `false` if NOT NULL
  - **`default`**: Default value expression (as string) or `null` if no default

- **`primary_key`**: Array of column names that form the primary key

- **`indexes`**: Array of index definitions (excluding primary key), each with:
  - **`name`**: Index name
  - **`columns`**: Array of column names in the index
  - **`unique`**: `true` if unique index, `false` otherwise

### Monitored Tables

The command introspects these control-plane tables:

1. **`control.agent_run`**: Agent run audit log (Migration 040)
2. **`control.tool_catalog`**: Tool catalog (Migration 040)
3. **`control.capability_rule`**: Capability rules (Migration 040)
4. **`control.doc_fragment`**: Document fragments (Migration 040)
5. **`control.capability_session`**: Capability sessions (Migration 040)
6. **`public.ai_interactions`**: AI interaction tracking (Rule-061, Migration 016)
7. **`public.governance_artifacts`**: Governance artifacts tracking (Rule-026, Rule-058, Migration 015)

## JSON-Only Output

For machine-readable output only (no human summary):

```bash
pmagent control schema --json-only
```

This outputs only JSON to stdout, with no summary to stderr.

## Use Cases

### Understanding Table Structure

Use this command to:
- Understand column types and constraints
- Identify primary keys and indexes
- Verify schema changes after migrations
- Generate documentation from live schema

### Schema Validation

Compare schema output against expected structure:
```bash
pmagent control schema --json-only | jq '.tables["control.agent_run"].columns[] | select(.name == "id")'
```

### Migration Verification

After running migrations, verify schema changes:
```bash
pmagent control schema --json-only | jq '.tables["control.agent_run"]'
```

## Troubleshooting

### Database is Off

If `mode=db_off`:

1. **Check database driver**: Ensure `psycopg3` is installed
   ```bash
   pip install psycopg[binary]
   ```

2. **Check DSN configuration**: Verify `GEMATRIA_DSN` is set
   ```bash
   make dsns.echo
   ```

3. **Check database connection**: Use `pmagent health db` to diagnose connection issues
   ```bash
   pmagent health db
   ```

4. **Refer to**: [DB_HEALTH.md](DB_HEALTH.md) for detailed database health troubleshooting

### Tables Missing

If some tables don't appear in the output:

1. **Check migrations**: Ensure all migrations have been applied
   ```bash
   psql "$GEMATRIA_DSN" -c "\dt control.*"
   ```

2. **Verify table existence**: Use `pmagent control tables` to see which tables exist
   ```bash
   pmagent control tables
   ```

3. **Check schema permissions**: Ensure the database user has SELECT permissions on `information_schema` and `pg_catalog`

### Schema Information Incomplete

If column or index information is missing:

1. **Check permissions**: The database user needs SELECT on system catalogs
2. **Verify table access**: Use `pmagent control status` to verify table presence
3. **Check for materialized views**: Materialized views are not included (only base tables)

## Related Commands

- **`pmagent control status`**: Check control-plane table row counts and presence
- **`pmagent control tables`**: List all schema-qualified tables with row counts
- **`pmagent health db`**: Check database health and connectivity

## Related Documentation

- **Database Architecture**: See `docs/ADRs/ADR-001-database-architecture.md` for DB design
- **Control Plane Schema**: See `migrations/040_control_plane_schema.sql` for control schema definition
- **AI Tracking**: See `migrations/016_create_ai_learning_tracking.sql` for AI interaction schema
- **Governance Tracking**: See `migrations/015_create_governance_tracking.sql` for governance schema

