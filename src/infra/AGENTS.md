# AGENTS.md - Infrastructure Directory

## Directory Purpose

The `src/infra/` directory provides cross-cutting infrastructure concerns including database connectivity, metrics collection, structured logging, and external service integration. These components enable observability and reliability across the entire pipeline.

## Key Components

### `db.py` - Database Connection Management (Critical Safety - Always Apply)

**Purpose**: Type-safe database connections with built-in safety guarantees
**Key Classes**:

- `GematriaRW` - Read/write access to gematria database with auto-transactions
- `BibleReadOnly` - Enforced read-only access to Bible database
  **Requirements** (DB Safety Rules):
- **Bible DB is READ-ONLY** - enforced at connection level; raises ReadOnlyViolation on INSERT/UPDATE/DELETE/MERGE/CREATE/ALTER/DROP/TRUNCATE/GRANT/REVOKE
- **Parameterized SQL Only** - all SQL uses `%s` parameters; f-strings forbidden in `.execute(...)` calls
- **Indices for Query Patterns** - unique(content_hash) constraints where applicable
- **Migration Tests** - apply and rollback cleanly; include contract tests
- Connection pooling for performance
- Automatic transaction management for writes

### `metrics.py` - Metrics Collection & Emission

**Purpose**: Collect and emit pipeline performance and health metrics
**Key Functions**:

- `get_metrics_client()` - Singleton metrics emitter
- `emit()` - Send metrics to configured sinks (Postgres + stdout)
- `timer()` - Performance timing decorators
  **Requirements**:
- **Fail-open** - metrics failures never block pipeline
- Structured JSON format for all metrics
- Configurable sinks (Postgres table + stdout JSON)

### `structured_logger.py` - Centralized Logging

**Purpose**: Consistent JSON logging with correlation IDs and structured data
**Key Functions**:

- `get_logger()` - Get named logger instance
- `log_json()` - Emit structured JSON log entries
- `with_correlation_id()` - Request tracing context
  **Requirements**:
- Consistent field naming across all logs
- Correlation IDs for request tracing
- Configurable log levels and outputs

### `checkpointer.py` - LangGraph Persistence

**Purpose**: Enable resumable pipeline execution via state persistence
**Key Classes**:

- `PostgresCheckpointer` - Production-grade persistence
- `MemoryCheckpointer` - Development/testing persistence
  **Requirements**:
- **CHECKPOINTER=postgres|memory** configuration
- Atomic state snapshots
- Efficient storage and retrieval

## Architecture Patterns

### Connection Management

```python
# Write operations (auto-transaction)
with get_gematria_rw() as db:
    db.execute("INSERT INTO table VALUES (%s)", (value,))

# Read operations (Bible DB enforced read-only)
bible_data = get_bible_ro().execute("SELECT * FROM verses WHERE book = %s", (book,))
```

### Metrics Emission

```python
metrics = get_metrics_client()
metrics.emit({
    "run_id": run_id,
    "node": "enrichment",
    "event": "batch_processed",
    "batch_size": len(batch),
    "latency_ms": processing_time
})
```

### Structured Logging

```python
LOG = get_logger("gemantria.enrichment")
log_json(LOG, 20, "enrichment_start", noun_count=len(nouns), run_id=str(run_id))
```

## Safety Guarantees

### Database Safety

- **Bible DB Read-Only**: Connection-level enforcement prevents writes
- **Transaction Management**: Automatic commit/rollback for write operations
- **Connection Pooling**: Efficient resource usage

### Operational Safety

- **Metrics Fail-Open**: Pipeline continues even if metrics collection fails
- **Logging Reliability**: Structured logging with fallbacks
- **Resource Management**: Proper connection cleanup and pooling

## Configuration Integration

### Environment Variables

- `GEMATRIA_DSN` - Application database connection
- `BIBLE_DB_DSN` - Bible database connection (read-only)
- `CHECKPOINTER` - postgres|memory persistence mode
- `METRICS_ENABLED` - Enable/disable metrics collection

### Service Dependencies

- **PostgreSQL**: Primary data storage and metrics sink
- **LM Studio**: External AI model serving (verified via health checks)
- **File System**: Log file outputs and configuration files

## Development Guidelines

### Adding New Metrics

1. Define metric schema in documentation
2. Add emission points in appropriate pipeline locations
3. Update metrics queries for reporting
4. Add validation for metric data quality

### Database Schema Changes

1. Create migration files in `migrations/` directory
2. Update connection classes if needed
3. Test with both read-only and read-write scenarios
4. Update documentation with new schema expectations

### Logging Improvements

1. Use consistent field naming conventions
2. Include correlation IDs for distributed tracing
3. Add structured context for debugging
4. Consider log volume and performance impact

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


## Testing Strategy

### Infrastructure Testing

- **Connection Tests**: Verify database connectivity and permissions
- **Metrics Tests**: Ensure metrics emission works without blocking
- **Logging Tests**: Validate structured log output formats
- **Checkpointer Tests**: Verify state persistence and resumption

### Integration Testing

- **Full Pipeline**: End-to-end with real infrastructure
- **Failure Scenarios**: Network outages, DB unavailability
- **Performance**: Load testing with metrics validation

## Performance Considerations

- Connection pooling reduces overhead
- Metrics emission is asynchronous where possible
- Logging uses efficient JSON serialization
- Checkpointer optimizes state storage size

## Monitoring & Alerting

- Database connection health checks
- Metrics emission success rates
- Log volume and error rate monitoring
- Checkpointer performance and storage usage
