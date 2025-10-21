# Test Suites & Quality Assurance

This directory contains the comprehensive test suite for the Gemantria pipeline, ensuring code quality, correctness, and reliability through automated testing. The tests are organized by scope and type to provide thorough coverage of all system components.

## 🎯 Purpose

The test suite serves multiple critical purposes:

- **Quality Assurance**: Verify correctness of algorithms and logic
- **Regression Prevention**: Catch breaking changes before deployment
- **Documentation**: Serve as executable examples of expected behavior
- **Refactoring Safety**: Enable confident code modifications
- **CI/CD Integration**: Automated quality gates for deployments

## 📁 Test Organization

### Directory Structure

```
tests/
├── unit/              # Unit tests for individual functions/classes
├── integration/       # Integration tests for component interactions
├── e2e/              # End-to-end pipeline tests
└── contract/         # Interface contract validation tests
```

### Test Categories

#### Unit Tests (`unit/`)
- **Scope**: Individual functions, methods, and classes
- **Isolation**: Mock external dependencies
- **Speed**: Fast execution (< 100ms per test)
- **Coverage**: 98%+ line and branch coverage required

#### Integration Tests (`integration/`)
- **Scope**: Component interactions and data flow
- **Dependencies**: Use real databases and services where safe
- **Focus**: Interface compliance and data consistency
- **Performance**: Medium execution time (100ms - 10s)

#### End-to-End Tests (`e2e/`)
- **Scope**: Complete pipeline execution
- **Environment**: Full system with external dependencies
- **Validation**: End-to-end correctness and performance
- **Frequency**: Run on major changes and releases

#### Contract Tests (`contract/`)
- **Scope**: Interface compliance between modules
- **Validation**: API contracts and data schemas
- **Automation**: Prevent interface drift between versions

## 🧪 Testing Framework

### Technology Stack

- **pytest**: Test runner and framework
- **pytest-cov**: Coverage reporting and enforcement
- **pytest-mock**: Mocking and patching utilities
- **pytest-asyncio**: Async test support for AI services

### Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=98
```

## 🔧 Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run specific test categories
make test.unit          # Unit tests only
make test.integration   # Integration tests only
make test.e2e          # End-to-end tests only

# Run with coverage
make coverage.report

# Run specific test file
python -m pytest tests/unit/test_gematria.py

# Run specific test function
python -m pytest tests/unit/test_gematria.py::test_calculate_basic_value
```

### Development Workflow

```bash
# Run tests in watch mode during development
pytest-watch tests/unit/

# Run failed tests only
pytest --lf

# Run tests with detailed output
pytest -v -s

# Generate coverage report
pytest --cov=src --cov-report=html
```

## 📊 Quality Gates

### Coverage Requirements

- **Overall Coverage**: ≥98% across all modules
- **Branch Coverage**: ≥95% for conditional logic
- **Exclusion Rules**: Generated code and test utilities excluded

### Performance Benchmarks

- **Unit Tests**: Complete in < 30 seconds
- **Integration Tests**: Complete in < 5 minutes
- **E2E Tests**: Complete in < 15 minutes (with AI services)

### Quality Metrics

- **Zero Failures**: All tests must pass in CI/CD
- **No Flakes**: Tests must be deterministic
- **Clean Code**: No linting violations in test code
- **Documentation**: All tests include clear docstrings

## 🏗️ Test Architecture

### Test Fixtures

Common test fixtures provide consistent test environments:

```python
@pytest.fixture
def sample_hebrew_text():
    """Provide sample Hebrew text for testing"""
    return "בראשית ברא אלהים את השמים ואת הארץ"

@pytest.fixture
def mock_db_session():
    """Provide mocked database session"""
    session = Mock()
    session.execute.return_value = Mock()
    return session

@pytest.fixture
async def mock_ai_client():
    """Provide mocked AI service client"""
    client = Mock()
    client.embed_texts.return_value = [[0.1] * 1024]
    return client
```

### Test Data Management

- **Static Test Data**: Known good inputs and expected outputs
- **Generated Test Data**: Programmatically created test cases
- **Edge Cases**: Boundary conditions and error scenarios
- **Regression Data**: Historical failures converted to tests

## 🎯 Key Test Areas

### Core Algorithm Testing

#### Gematria Calculations
```python
def test_gematria_basic_values():
    """Test fundamental gematria value calculations"""
    assert calculate_gematria("אב") == 3  # Aleph + Bet = 1 + 2
    assert calculate_gematria("ה׳") == 5   # He = 5
    assert calculate_gematria("תש״פ") == 780  # Year 5780 in gematria
```

#### Text Processing
```python
def test_hebrew_normalization():
    """Test Hebrew text normalization and cleaning"""
    input_text = "וַיִּקְרָא אֶל־מֹשֶׁה"
    normalized = normalize_hebrew(input_text)
    assert "־" not in normalized  # Maqaf removed
    assert "ּ" not in normalized   # Dagesh removed
```

### AI Service Testing

#### Mock vs Live Testing
```python
@pytest.mark.parametrize("use_mock", [True, False])
def test_ai_enrichment(use_mock):
    """Test AI enrichment with both mock and live services"""
    if use_mock:
        # Test with mocked AI service
        pass
    else:
        # Test with live AI service (requires ALLOW_MOCKS_FOR_TESTS=0)
        pass
```

#### Health Check Validation
```python
def test_qwen_live_gate():
    """Test Qwen Live Gate enforcement"""
    with pytest.raises(QwenUnavailableError):
        # Test behavior when AI service is unavailable
        pass
```

### Database Testing

#### Schema Validation
```python
def test_database_schema():
    """Validate database schema matches expectations"""
    with get_gematria_rw() as conn:
        # Check table existence and structure
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        assert "concepts" in [row[0] for row in tables]
```

#### Data Integrity
```python
def test_data_integrity():
    """Test data consistency and referential integrity"""
    with get_gematria_rw() as conn:
        # Verify foreign key relationships
        # Check data type constraints
        # Validate computed fields
```

## 🚨 Test Environments

### Development Environment

- **Fast Feedback**: Quick test execution during development
- **Mock Services**: Use mocked external dependencies
- **In-Memory DB**: SQLite for rapid testing

### CI/CD Environment

- **Full Coverage**: All tests run on every commit
- **Real Services**: Integration with actual databases and AI services
- **Performance Validation**: Benchmarking against performance baselines

### Production Validation

- **Pre-Deployment**: Full test suite before releases
- **Smoke Tests**: Critical path validation in production
- **Monitoring**: Test result tracking and alerting

## 📈 Test Maintenance

### Adding New Tests

1. **Identify Coverage Gap**: Determine what needs testing
2. **Write Test Case**: Follow naming conventions and patterns
3. **Add Fixtures**: Use or create appropriate test fixtures
4. **Verify Coverage**: Ensure new code is adequately tested
5. **Update Documentation**: Document test purpose and scope

### Test Refactoring

1. **Identify Patterns**: Look for duplicated test code
2. **Extract Fixtures**: Create reusable test setup
3. **Parameterize Tests**: Use pytest.mark.parametrize for similar cases
4. **Improve Readability**: Clear test names and documentation
5. **Performance Optimization**: Reduce test execution time

## 🔍 Debugging Test Failures

### Common Issues

- **Flaky Tests**: Non-deterministic test behavior
- **Mock Inconsistencies**: Incorrect mock setup or expectations
- **Environment Differences**: Tests pass locally but fail in CI/CD
- **Race Conditions**: Async code timing issues

### Debugging Tools

```bash
# Run test with detailed output
pytest -v -s tests/unit/test_failing.py::test_specific_case

# Debug with pdb
pytest --pdb tests/unit/test_failing.py

# Run with coverage details
pytest --cov=src --cov-report=term-missing tests/unit/

# Profile test performance
pytest --durations=10 tests/
```

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)**: AI assistant guide for test development
- **ADR-008**: Confidence validation and quality gates
- **ADR-013**: Documentation synchronization requirements

## 🤝 Development Guidelines

### Test Writing Standards

- **Descriptive Names**: `test_calculate_gematria_with_final_forms`
- **Single Responsibility**: Each test validates one behavior
- **Independent Execution**: Tests can run in any order
- **Clear Assertions**: Obvious what the test is checking

### Test Organization

- **Logical Grouping**: Related tests in same test class/module
- **Fixture Usage**: Maximize fixture reuse for consistency
- **Marker Usage**: Use pytest markers for test categorization
- **Documentation**: Every test includes docstring explaining purpose

### CI/CD Integration

- **Automated Execution**: Tests run on every pull request
- **Failure Blocking**: Test failures prevent merges
- **Result Reporting**: Detailed reports available in CI/CD interface
- **Performance Tracking**: Historical test execution metrics
