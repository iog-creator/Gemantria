# Database Migrations

This directory contains SQL migration scripts for the Gemantria database schema.

## Migration Files

### Schema Migrations
- `001_initial_schema.sql` - Initial database schema (referenced in docs)
- `002_create_checkpointer.sql` - LangGraph checkpointer tables
- `003_metrics_logging.sql` - Pipeline metrics and logging tables
- `004_metrics_views.sql` - Database views for metrics analysis
- `005_ai_metadata.sql` - AI enrichment metadata tables
- `006_confidence_validation.sql` - Confidence validation logging
- `007_concept_network.sql` - Semantic network concept tables
- `008_add_concept_network_constraints.sql` - Network table constraints
- `009_rerank_evidence.sql` - Reranking evidence tables
- `010_qwen_health_log.sql` - Qwen model health logging
- `011_concept_network_verification.sql` - Network verification tables
- `012a_concept_network_dim_fix.sql` - Vector dimension fixes
- `013_fix_ai_enrichment_schema.sql` - AI enrichment schema fixes
- `014_relations_and_patterns.sql` - Concept relations and patterns
- `015_graph_metadata.sql` - Graph metadata tables

## Usage

Migrations should be applied in numerical order using psql:

```bash
# Apply specific migration
psql "$GEMATRIA_DSN" -f migrations/001_initial_schema.sql

# Apply all migrations (ensure order)
for f in migrations/*.sql; do
    echo "Applying $f..."
    psql "$GEMATRIA_DSN" -f "$f"
done
```

## Schema Dependencies

- **pgvector extension** required for semantic embeddings
- **Postgres 13+** recommended for performance
- **Proper permissions** for creating tables and extensions

## Rollback

⚠️ **Migrations are not designed for rollback.** Schema changes are additive. For development/testing, recreate the database:

```bash
dropdb gematria && createdb gematria
# Reapply all migrations
```

## Validation

After applying migrations, verify with:

```bash
# Check tables exist
psql "$GEMATRIA_DSN" -c "\dt"

# Check pgvector extension
psql "$GEMATRIA_DSN" -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

## Related Documentation

- [Database Schema](../docs/SSOT/database_schema.md)
- [Infrastructure Setup](../AGENTS.md#runbook-postgres-checkpointer)
- [Qwen Integration](../docs/qwen_integration.md)
