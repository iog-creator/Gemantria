# ADR-008: Confidence-Aware Batch Validation

## Status

Accepted

## Context

The gematria pipeline processes Hebrew nouns through multiple stages: extraction, validation, AI enrichment, and confidence assessment. Without confidence validation, low-quality or incorrect results could propagate through the system, leading to unreliable theological insights.

## Decision

Implement confidence-aware batch validation with the following characteristics:

1. **Dual Confidence Metrics**: Separate thresholds for gematria calculation confidence (≥0.90) and AI insight confidence (≥0.95)
2. **Pipeline Abort Capability**: Confidence validation failures trigger immediate pipeline termination with detailed error reporting
3. **Database Audit Trail**: All confidence validations logged in `confidence_validation_log` table with reasons for pass/fail
4. **Post-Run Reporting**: Automated generation of Markdown and JSON reports with confidence metrics and recommendations

## Implementation Details

### Architecture Components

#### Confidence Validator Node

- Located: `src/nodes/confidence_validator.py`
- Function: `confidence_validator_node(state: dict) -> dict`
- Input: Enriched nouns with AI confidence scores
- Output: Validation results or ConfidenceValidationError

#### Database Schema

```sql
CREATE TABLE confidence_validation_log (
    id                    BIGSERIAL PRIMARY KEY,
    run_id                UUID NOT NULL,
    node                  TEXT NOT NULL,
    noun_id               UUID NOT NULL,
    gematria_confidence   NUMERIC(5,4),
    ai_confidence         NUMERIC(5,4),
    gematria_threshold    NUMERIC(5,4),
    ai_threshold          NUMERIC(5,4),
    validation_passed     BOOLEAN NOT NULL,
    abort_reason          TEXT,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);
```

#### Environment Variables

- `GEMATRIA_CONFIDENCE_THRESHOLD=0.90`
- `AI_CONFIDENCE_THRESHOLD=0.95`

### Pipeline Integration

#### Graph Structure

```
collect_nouns → validate_batch → enrichment → confidence_validator
```

#### Error Handling

- ConfidenceValidationError: Raised when any noun fails validation
- Error includes low_confidence_nouns list with detailed failure reasons
- Pipeline state updated with error information for downstream processing

### Report Generation

#### Automated Reports

- Script: `scripts/generate_report.py`
- Outputs: Markdown (human-readable) + JSON (machine-readable)
- Location: `./reports/` directory

#### Report Contents

- Executive summary with key metrics
- Node performance analysis
- AI enrichment statistics
- Confidence validation results
- Quality metrics and recommendations

## Consequences

### Positive

- **Quality Assurance**: Prevents propagation of low-confidence results
- **Auditability**: Complete confidence validation history
- **Observability**: Automated reporting for pipeline health
- **Fail-Fast**: Early termination prevents wasted compute resources

### Negative

- **Additional Latency**: Confidence validation adds processing time
- **Storage Overhead**: Validation logs increase database size
- **Complexity**: Additional error handling and state management

## Alternatives Considered

### Option 1: Post-Processing Validation Only

- Validate after complete pipeline execution
- Pro: No pipeline interruption
- Con: Wasted resources on low-confidence results

### Option 2: Single Confidence Threshold

- One threshold for all validation types
- Pro: Simpler configuration
- Con: Cannot distinguish between calculation vs AI confidence issues

### Option 3: Warning-Only Validation

- Log warnings but allow pipeline continuation
- Pro: Never blocks pipeline execution
- Con: Allows low-quality results to propagate

## Testing Strategy

### Unit Tests

- Confidence threshold calculations
- Error message formatting
- Database logging functionality

### Integration Tests

- Full pipeline execution with various confidence scenarios
- Report generation verification
- Database roundtrip testing

### Contract Tests

- Confidence validation behavior with edge cases
- Error handling verification
- Threshold boundary testing

## Future Considerations

### Dynamic Thresholds

Future versions could implement dynamic thresholds based on:

- Historical performance data
- Noun complexity metrics
- Model version confidence patterns

### Confidence Weighting

Advanced confidence scoring could weight different factors:

- Gematria calculation accuracy
- AI model confidence
- Historical validation patterns
- Cross-reference validation

### Alerting Integration

Confidence validation failures could trigger:

- Email/Slack notifications
- Dashboard alerts
- Automated remediation workflows
