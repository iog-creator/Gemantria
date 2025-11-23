# AGENTS.md - agentpm/tests/atlas Directory

## Directory Purpose

The `agentpm/tests/atlas/` directory contains Atlas integration tests that validate end-to-end system behavior and readiness gates. These tests ensure the system meets production requirements before deployment and provide comprehensive validation of critical system components.

## Key Test Categories

### Tagproof Bundle Tests

**Purpose**: Validate Phase-2 tagproof bundle generation and guard validation for automated PR/merge gates.

**Coverage**:
- Bundle component aggregation (TV coverage, gatekeeper coverage, regeneration, browser screenshots, MCP catalog)
- Dynamic component requirements based on STRICT/HINT mode
- MCP catalog integration and error handling
- Component health validation and missing component detection

**Key Tests**:
- `test_e100_tagproof_phase2.py` - Complete tagproof bundle validation suite (PLAN-080 E100)
  - Tests bundle generation script execution and output structure
  - Validates guard script validation logic
  - Tests hermetic mode with fixture-based evidence
  - Validates component aggregation and health checks
  - Tests STRICT vs HINT mode behavior

### E-Series Test Pattern

**Purpose**: Execute specific implementation phases (E100, E101, E102, etc.) with comprehensive validation.

**Test Structure**:
- **E87**: Compliance time-series and heatmap generation validation (PLAN-092)
  - Tests compliance_timeseries.json export existence and structure
  - Validates dashboard HTML generation and functionality
  - Tests heatmap data structure and visualization
  - Validates evidence file generation
- **E100**: Phase-2 tagproof bundle generation and validation (PLAN-080)
  - Tests bundle generation script execution and output structure
  - Validates guard script validation logic
  - Tests hermetic mode with fixture-based evidence
- **E101**: Guarded tool calls implementation (P0 schemas, PoR enforcement, MCP adapter)
- **E102**: Tagproof/Atlas wiring and MCP RO proof guard integration

## Test Fixtures

### Evidence Fixtures

**E100 Fixtures** (`fixtures/e100/`):
- `tv_coverage_ok.json` - TV coverage evidence
- `gatekeeper_coverage_ok.json` - Gatekeeper coverage evidence
- `regeneration_guard_ok.json` - Regeneration guard verdict
- `regeneration_guard_failed.json` - Failed regeneration guard verdict
- `browser_screenshot_ok.json` - Browser screenshot evidence
- `guard_mcp_db_ro_ok.json` - MCP DB RO guard verdict

**E95 Fixtures** (`fixtures/e95/`):
- HTML test files for Atlas links guard validation
- `test_absolute.html`, `test_broken.html`, `test_whitelisted.html`

**E98/E99 Fixtures** (`fixtures/e98/`, `fixtures/e99/`):
- Sample receipts and guard evidence for browser verification and Atlas links validation

## API Contracts

### Bundle Generation Contract

```python
def generate_tagproof_bundle() -> dict[str, Any]:
    """Generate Phase-2 tagproof bundle with all evidence components.

    Returns:
        {
            "version": 1,
            "timestamp": "ISO-8601",
            "components": {
                "tv_coverage": {...},
                "gatekeeper_coverage": {...},
                "regeneration_receipt": {...},
                "browser_screenshot": {...},
                "mcp_catalog_summary": {
                    "available": bool,
                    "tools_count": int,
                    "error": str | None
                },
                "mcp_db_ro_guard": {...}
            },
            "meta": {"phase": 2, "plan": "PLAN-080"}
        }
    """
```

### Guard Validation Contract

```python
def validate_tagproof_bundle(bundle: dict) -> dict[str, Any]:
    """Validate Phase-2 tagproof bundle completeness.

    Args:
        bundle: Tagproof bundle from generate_tagproof_bundle()

    Returns:
        {
            "ok": bool,
            "counts": {
                "components_total": int,
                "components_missing": int,
                "components_ok": int,
                "components_failed": int
            },
            "details": {
                "mode": "STRICT" | "HINT",
                "missing_components": List[str],
                "component_errors": dict[str, str]
            }
        }
    """
```

## Testing Strategy

### Hermetic Testing

- **Evidence-Based**: Uses pre-generated evidence files to avoid external dependencies
- **Fixture-Driven**: Consistent test data for reproducible results
- **Error Simulation**: Tests error conditions with controlled fixture data

### Integration Validation

- **End-to-End**: Tests complete workflows from evidence generation to validation
- **Component Interaction**: Validates how components work together in the bundle
- **Mode-Aware**: Tests both STRICT and HINT modes for different deployment scenarios

## Development Guidelines

### Adding New E-Series Tests

1. **Phase Definition**: Clearly define what the E-series phase accomplishes
2. **Evidence Generation**: Create appropriate fixture files for hermetic testing
3. **Comprehensive Coverage**: Test both success and failure paths
4. **Mode Testing**: Validate behavior in both STRICT and HINT modes

### Fixture Management

1. **Consistent Naming**: Use `fixtures/e{phase}/` directory structure
2. **Evidence Format**: Match actual evidence file formats and schemas
3. **Error Cases**: Include fixtures for common error conditions

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| Tagproof bundle generation | PLAN-080 (Verification Sweep and Tagproof) |
| Guarded tool calls | PLAN-091 (Guarded Tool Calls P0 Execution) |
| MCP catalog integration | ADR-066 (LM Studio Control Plane Integration) |
