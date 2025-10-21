# External Service Integrations

This module manages all integrations with external services and APIs that the Gemantria pipeline depends on. It provides clean interfaces for database connections, AI model access, and configuration management while ensuring safety, reliability, and proper error handling.

## 🎯 Purpose

The services module acts as the boundary between the Gemantria pipeline and external dependencies:

- **Database Access**: Safe, parameterized connections to PostgreSQL databases
- **AI Model Integration**: Client for LM Studio and Qwen model interactions
- **Configuration Management**: Centralized environment variable handling
- **Health Monitoring**: Service availability and performance tracking

## 🏗️ Architecture

### Service Layer Design

Each service follows a consistent interface pattern:

```python
class ServiceName:
    def __init__(self, config: Config) -> None:
        """Initialize with configuration"""

    def health_check(self) -> HealthStatus:
        """Verify service availability"""

    def execute_operation(self, *args) -> Result:
        """Perform the primary service operation"""
```

### Dependency Injection

Services are injected into pipeline components rather than imported directly:

```python
# In pipeline setup
db_service = DatabaseService(config)
ai_service = LMStudioService(config)

# Injected into processing nodes
node = EnrichmentNode(ai_service, db_service)
```

## 🔧 Key Services

### Database Service (`db.py`)

**Purpose**: Manage connections to PostgreSQL databases with pgvector support

**Key Features**:
- **Connection Pooling**: Efficient connection reuse with configurable limits
- **Read-Only Enforcement**: Bible database protected from writes
- **Parameterized Queries**: SQL injection prevention
- **Transaction Management**: Proper commit/rollback handling

**Configuration**:
```python
# Primary database (read-write)
GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gematria

# Reference database (read-only)
BIBLE_DB_DSN=postgresql://user:pass@localhost:5432/bible_db
```

### LM Studio Service (`lmstudio_client.py`)

**Purpose**: Interface with local LLM models via LM Studio API

**Key Features**:
- **Qwen Live Gate**: Health checks before AI operations
- **Model Validation**: Verify embedding and reranker availability
- **Timeout Handling**: Configurable request timeouts and retries
- **Response Parsing**: Structured handling of AI model outputs

**Supported Models**:
- **Embedding**: `text-embedding-qwen3-embedding-0.6b`
- **Reranker**: `qwen.qwen3-reranker-0.6b`
- **Theology**: `christian-bible-expert-v2.0-12b`
- **Math**: `self-certainty-qwen3-1.7b-base-math`

### Configuration Service (`config.py`)

**Purpose**: Centralized management of environment variables and settings

**Key Features**:
- **Type Safety**: Strongly typed configuration objects
- **Validation**: Required fields and value range checking
- **Defaults**: Sensible defaults with override capability
- **Environment Detection**: Automatic environment-specific behavior

## 🛡️ Safety & Reliability

### Database Safety

- **Connection Limits**: Prevent resource exhaustion
- **Query Logging**: Audit trail for all database operations
- **Error Recovery**: Automatic reconnection on failures
- **Schema Validation**: Verify database structure matches expectations

### AI Service Safety

- **Health Verification**: Qwen Live Gate requires live models
- **Fallback Handling**: Graceful degradation when AI unavailable
- **Rate Limiting**: Respect API limits and avoid overload
- **Response Validation**: Verify AI outputs meet quality standards

### Configuration Safety

- **Required Validation**: Fail fast on missing critical settings
- **Type Checking**: Prevent configuration-related runtime errors
- **Security**: Sensitive data handling and masking in logs

## 📊 Service Monitoring

### Health Checks

Each service implements health verification:

```python
# Database health
db_status = db_service.health_check()
# Returns: connection status, query latency, schema version

# AI service health
ai_status = ai_service.health_check()
# Returns: model availability, embedding dimensions, response time
```

### Metrics Collection

Services contribute to observability:

- **Request Counts**: Number of operations performed
- **Latency Measurements**: Response time percentiles
- **Error Rates**: Failure frequency and types
- **Resource Usage**: Memory and connection pool utilization

## 🔧 Usage Examples

### Database Operations

```python
from src.services.db import get_gematria_rw, get_bible_ro

# Get read-write connection to primary database
with get_gematria_rw() as conn:
    result = conn.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,))
    concept = result.fetchone()

# Get read-only connection to bible database
with get_bible_ro() as conn:
    verses = conn.execute("SELECT text FROM verses WHERE book = ?", ("Genesis",))
```

### AI Model Interaction

```python
from src.services.lmstudio_client import LMStudioClient

client = LMStudioClient()

# Generate embeddings
embeddings = await client.embed_texts([
    "אלהים ברא את השמים ואת הארץ",  # Hebrew text
    "In the beginning God created heaven and earth"  # English translation
])

# Get semantic similarity
similarity = await client.rerank_pairs([
    ("אלהים", "God"),
    ("ברא", "created"),
    ("שמים", "heaven")
])
```

### Configuration Access

```python
from src.services.config import get_config

config = get_config()

# Access typed configuration
batch_size = config.pipeline.batch_size
db_url = config.database.gematria_dsn
model_name = config.ai.embedding_model

# Environment-specific settings
is_production = config.environment.is_production
log_level = config.logging.level
```

## 🧪 Testing & Mocking

### Service Interfaces

All services implement mockable interfaces for testing:

```python
from unittest.mock import Mock

# Mock database service
mock_db = Mock(spec=DatabaseService)
mock_db.health_check.return_value = HealthStatus.HEALTHY

# Mock AI service
mock_ai = Mock(spec=LMStudioService)
mock_ai.embed_texts.return_value = [[0.1, 0.2, 0.3, ...]]
```

### Integration Testing

Services are tested both in isolation and integration:

- **Unit Tests**: Individual service method testing
- **Integration Tests**: End-to-end service interaction
- **Contract Tests**: Verify service interface compliance
- **Performance Tests**: Load and latency benchmarking

## 📈 Performance Optimization

### Connection Pooling

Database connections are pooled for efficiency:

```python
# Connection pool configuration
pool_size = 5
max_overflow = 10
pool_timeout = 30

# Automatic connection reuse
# No connection overhead for consecutive operations
```

### Request Batching

AI requests are batched where possible:

```python
# Batch embedding requests
batch_size = 50
embeddings = await client.embed_batch(texts, batch_size=batch_size)
```

### Caching Strategies

Frequently accessed data is cached:

- **Configuration**: Cached after first load
- **Model Metadata**: Cached model information
- **Health Status**: Cached health check results

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)**: AI assistant guide for service development
- **[Parent](../README.md)**: Core source code overview
- **ADR-001**: Database architecture and safety decisions
- **ADR-010**: LM Studio integration and Qwen Live Gate

## 🤝 Development Guidelines

### Adding New Services

1. **Define Interface**: Create abstract base class for the service
2. **Implement Service**: Follow established patterns and safety measures
3. **Add Configuration**: Extend config.py with new settings
4. **Implement Health Checks**: Provide service availability verification
5. **Add Tests**: Comprehensive unit and integration test coverage
6. **Update Documentation**: AGENTS.md and this README

### Service Contract Changes

Any changes to service interfaces require:

- **Version Compatibility**: Backward compatibility where possible
- **Migration Path**: Clear upgrade instructions
- **Testing Updates**: All dependent tests updated
- **Documentation Updates**: Interface changes documented

### Error Handling Standards

All services must handle errors consistently:

- **Specific Exceptions**: Custom exception types for different failure modes
- **Error Context**: Include relevant information for debugging
- **Recovery Logic**: Automatic retry for transient failures
- **Logging**: Structured error logging with appropriate levels
