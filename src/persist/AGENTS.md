# AGENTS.md - Persistence Directory

## Directory Purpose

The `src/persist/` directory contains persistence utilities for tracking pipeline execution runs. This module provides lightweight run tracking functionality for monitoring and auditing pipeline operations.

## Key Components

### `runs_ledger.py` - Pipeline Run Tracking

**Purpose**: Track pipeline execution runs in the database for monitoring, auditing, and debugging purposes. Provides simple start/finish markers for pipeline runs.

**Key Functions**:

- `mark_run_started(run_id: str, book: str, notes: str = "") -> None` - Record pipeline run start
  - Inserts run record into `gematria.runs_ledger` table
  - Uses `ON CONFLICT DO NOTHING` for idempotency
  - Records run_id, book, optional notes, and timestamp
- `mark_run_finished(run_id: str, notes: str = "") -> None` - Record pipeline run completion
  - Updates existing run record with finish timestamp
  - Optionally updates notes (preserves existing if new notes empty)
  - Records completion timestamp

**Requirements**:
- **DSN Access**: Uses centralized DSN loader (`scripts.config.env.get_rw_dsn()`)
- **Idempotent**: Safe to call multiple times with same run_id
- **Transaction Safety**: Uses connection context managers for automatic commit/rollback
- **Error Handling**: Raises `RuntimeError` with helpful message if DSN not configured

## API Contracts

### Run Tracking

```python
def mark_run_started(run_id: str, book: str, notes: str = "") -> None:
    """Record pipeline run start in database.
    
    Args:
        run_id: Unique identifier for the pipeline run (UUID recommended)
        book: Book name being processed (e.g., "Genesis")
        notes: Optional notes about the run
        
    Raises:
        RuntimeError: If GEMATRIA_DSN not configured in environment
    """

def mark_run_finished(run_id: str, notes: str = "") -> None:
    """Record pipeline run completion in database.
    
    Args:
        run_id: Unique identifier for the pipeline run (must match started run)
        notes: Optional completion notes (preserves existing if empty)
        
    Raises:
        RuntimeError: If GEMATRIA_DSN not configured in environment
    """
```

## Database Schema

### `gematria.runs_ledger` Table

Expected schema (created by migrations):

```sql
CREATE TABLE gematria.runs_ledger (
    run_id TEXT PRIMARY KEY,
    book TEXT NOT NULL,
    notes TEXT,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP
);
```

## Usage Patterns

### Basic Run Tracking

```python
from src.persist.runs_ledger import mark_run_started, mark_run_finished
import uuid

# Start a pipeline run
run_id = str(uuid.uuid7())
mark_run_started(run_id, book="Genesis", notes="Initial extraction run")

# ... pipeline execution ...

# Mark run as finished
mark_run_finished(run_id, notes="Completed successfully with 150 nouns")
```

### Integration with Pipeline

```python
# In pipeline orchestration
from src.persist.runs_ledger import mark_run_started, mark_run_finished

def run_pipeline(book: str):
    run_id = generate_run_id()
    try:
        mark_run_started(run_id, book)
        # ... execute pipeline ...
        mark_run_finished(run_id, notes="Pipeline completed")
    except Exception as e:
        mark_run_finished(run_id, notes=f"Pipeline failed: {str(e)}")
        raise
```

## Testing Strategy

### Unit Tests

- **DSN Configuration**: Test error handling when DSN not configured
- **Idempotency**: Verify multiple calls with same run_id are safe
- **Transaction Safety**: Test rollback behavior on errors
- **Notes Handling**: Verify notes preservation logic

### Integration Tests

- **Database Operations**: Test actual database insert/update operations
- **Concurrent Runs**: Test multiple simultaneous run tracking
- **Schema Validation**: Verify table structure matches expectations

### Coverage Requirements

- ≥98% code coverage
- Test both success and failure paths
- Test edge cases (empty notes, duplicate run_ids)

## Development Guidelines

### Adding New Persistence Functions

1. **DSN Access**: Always use centralized DSN loader (`scripts.config.env.get_rw_dsn()`)
2. **Error Messages**: Provide helpful error messages with remediation steps
3. **Idempotency**: Design functions to be safe when called multiple times
4. **Transaction Safety**: Use connection context managers for automatic cleanup

### Code Standards

- **Parameterized Queries**: Always use `%s` placeholders (no f-strings in SQL)
- **Type Hints**: Complete type annotations for all functions
- **Documentation**: Clear docstrings with usage examples
- **Error Handling**: Graceful error handling with informative messages

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `runs_ledger.py` | ADR-001 (Two-DB Safety), ADR-037 (Data Persistence Completeness) |

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Infrastructure**: [../infra/AGENTS.md](../infra/AGENTS.md) - Database connection management
- **Rules**: [.cursor/rules/001-db-safety.mdc](../../.cursor/rules/001-db-safety.mdc), [.cursor/rules/037-data-persistence-completeness.mdc](../../.cursor/rules/037-data-persistence-completeness.mdc)
