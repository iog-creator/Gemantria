# AGENTS.md - Testing Directory

## Directory Purpose
The `tests/` directory contains comprehensive test suites that validate the correctness, reliability, and performance of the Gemantria pipeline. Tests are organized by scope and testing strategy.

## Testing Strategy Overview

### Test Pyramid Structure
```
Unit Tests (70%) → Integration Tests (20%) → E2E Tests (10%)
```

### Test Categories

#### `unit/` - Unit Tests
**Purpose**: Test individual functions and classes in isolation
**Scope**: Single functions/methods with mocked dependencies
**Coverage**: ≥98% required for all modules
**Key Focus**:
- Pure function correctness
- Error handling edge cases
- Input validation
- Algorithm accuracy

#### `integration/` - Integration Tests
**Purpose**: Test component interactions with real dependencies
**Scope**: Multiple components working together
**Dependencies**: Real database, external services (mocked where appropriate)
**Key Focus**:
- Database operations
- API integrations
- Component contracts
- Data flow validation

#### `e2e/` - End-to-End Tests
**Purpose**: Test complete pipeline execution
**Scope**: Full pipeline from input to output
**Dependencies**: All external services (LM Studio, databases)
**Key Focus**:
- Pipeline completion
- Data integrity end-to-end
- Performance requirements
- Failure recovery

#### `contract/` - Contract Tests
**Purpose**: Validate interface compliance between modules
**Scope**: API contracts and data schemas
**Dependencies**: Minimal (interface definitions only)
**Key Focus**:
- Interface compatibility
- Data schema validation
- Breaking change detection

## Test Organization Principles

### Directory Structure
```
tests/
├── unit/           # Function-level isolation tests
├── integration/    # Component interaction tests
├── e2e/           # Full pipeline tests
└── contract/      # Interface compliance tests
```

### Naming Conventions
- `test_*.py` - Test modules
- `test_*()` - Individual test functions
- `*_test.py` - Alternative naming (less preferred)

### Test Data Management
- **Deterministic**: Same inputs produce same outputs
- **Isolated**: No test interdependencies
- **Minimal**: Smallest possible dataset for test case
- **Realistic**: Representative of production data

## Key Testing Areas

### Core Functionality Tests
- **Hebrew Processing**: Normalization, validation, gematria calculation
- **ID Generation**: Content hashing, UUID generation, determinism
- **Data Models**: State objects, pipeline configuration

### Infrastructure Tests
- **Database**: Connection management, transaction handling, read-only enforcement
- **External APIs**: LM Studio client, error handling, retry logic
- **Metrics**: Emission, collection, performance impact

### Pipeline Tests
- **Node Execution**: Individual node correctness
- **State Management**: Pipeline state transitions
- **Error Handling**: Failure scenarios and recovery
- **Performance**: Batch processing, resource usage

### Integration Tests
- **Database Persistence**: CRUD operations, constraint validation
- **External Services**: API call patterns, response handling
- **Component Contracts**: Interface compliance between modules

## Test Execution & Quality Gates

### Automated Testing
```bash
# Full test suite
make test

# Individual test categories
make test.unit
make test.integration
make test.e2e

# Coverage reporting
make coverage.report
```

### Quality Gates
- **Coverage**: ≥98% for all modules
- **Performance**: Tests complete within time limits
- **Reliability**: No flaky tests (3-run stability)
- **CI Integration**: All tests pass in automated pipeline

## Test Environment Management

### Test Databases
- **Isolated**: Separate test databases from production
- **Ephemeral**: Created/destroyed per test run
- **Seeded**: Known test data for reproducible results

### External Service Mocks
- **LM Studio**: HTTP request/response mocking
- **Database**: In-memory SQLite for unit tests
- **File System**: Temporary directories for I/O tests

### Configuration
- **Environment Variables**: Test-specific configuration
- **Timeouts**: Reasonable timeouts for external calls
- **Cleanup**: Automatic resource cleanup after tests

## Development Guidelines

### Writing New Tests
1. **Identify Scope**: unit/integration/e2e based on dependencies
2. **Mock External Dependencies**: Use fixtures for databases, APIs
3. **Test Edge Cases**: Error conditions, boundary values
4. **Assert Correctness**: Verify both success and failure paths

### Test Maintenance
1. **Update on Changes**: Modify tests when code changes
2. **Remove Obsolete Tests**: Delete tests for removed functionality
3. **Refactor Tests**: Improve readability and performance
4. **Add Missing Coverage**: Identify and test uncovered code

### Debugging Test Failures
1. **Isolate Issue**: Run individual failing tests
2. **Check Dependencies**: Verify test environment setup
3. **Review Assertions**: Ensure test expectations are correct
4. **Log Analysis**: Use debug logging for complex scenarios

## Performance Testing

### Benchmark Tests
- **Throughput**: Processing speed under load
- **Memory Usage**: Resource consumption monitoring
- **Database Performance**: Query optimization validation

### Load Testing
- **Batch Processing**: Large batch handling
- **Concurrent Operations**: Multiple pipeline instances
- **Resource Limits**: Memory and CPU constraints

## Continuous Integration

### Pre-commit Hooks
- **Linting**: Code style and quality checks
- **Type Checking**: Static type validation
- **Unit Tests**: Fast feedback on changes

### CI Pipeline
- **Multi-stage**: Lint → Test → Integration → E2E
- **Parallel Execution**: Speed up test runs
- **Artifact Collection**: Test reports and coverage data
- **Failure Analysis**: Detailed failure reports

## Test Data Management

### Fixtures & Factories
- **Data Builders**: Create test objects with known properties
- **Fixture Reuse**: Shared test data across multiple tests
- **Cleanup**: Automatic teardown and resource release

### Property-Based Testing
- **Input Generation**: Automated test case generation
- **Invariant Checking**: Mathematical property validation
- **Edge Case Discovery**: Automated boundary testing

## Documentation & Reporting

### Test Reports
- **Coverage Reports**: Line-by-line coverage analysis
- **Performance Metrics**: Test execution time tracking
- **Failure Analysis**: Detailed failure descriptions

### Test Documentation
- **README**: Testing strategy and guidelines
- **Fixture Docs**: Test data structure documentation
- **CI Docs**: Pipeline configuration and troubleshooting

