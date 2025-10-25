# Utility Scripts & Export Tools

This directory contains utility scripts that support the Gemantria pipeline operations, including data export, analysis, and maintenance tasks. These scripts provide command-line interfaces for common operations and automation.

## 🎯 Purpose

The scripts directory serves as the command-line interface for:

- **Data Export**: Generate various output formats from pipeline results
- **Analysis Tools**: Perform graph analysis and metrics calculation
- **Maintenance Tasks**: Database operations and system health checks
- **Automation**: CI/CD integration and scheduled operations

## 📋 Available Scripts

### Data Export Scripts

#### `export_graph.py`

**Purpose**: Export semantic concept networks to visualization-ready JSON

**Features**:

- Node-link format for graph visualization libraries
- Cluster membership and centrality metrics
- Relationship strengths and types
- Metadata export with timestamps

**Usage**:

```bash
python scripts/export_graph.py
# Outputs: exports/graph_latest.json
```

#### `export_jsonld.py`

**Purpose**: Export semantic networks as JSON-LD and RDF/Turtle

**Features**:

- W3C JSON-LD standard compliance
- RDF/Turtle serialization for knowledge graphs
- Global URIs using gematria.ai namespace
- Schema.org vocabulary integration

**Usage**:

```bash
python scripts/export_jsonld.py
# Outputs: exports/graph_latest.jsonld, exports/graph_latest.ttl
```

#### `export_stats.py`

**Purpose**: Generate graph statistics for dashboards and monitoring

**Features**:

- Node and edge counts
- Cluster distribution analysis
- Centrality metrics aggregation
- Performance and quality indicators

**Usage**:

```bash
python scripts/export_stats.py
# Outputs: JSON metrics for dashboard consumption
```

### Analysis Scripts

#### `analyze_graph.py`

**Purpose**: Perform advanced graph analysis on semantic networks

**Features**:

- Community detection algorithms
- Centrality calculations (degree, betweenness, eigenvector)
- Pattern discovery and motif analysis
- Statistical summaries and distributions

**Usage**:

```bash
python scripts/analyze_graph.py
# Performs comprehensive graph analysis
```

### Maintenance Scripts

#### `generate_report.py`

**Purpose**: Generate comprehensive pipeline execution reports

**Features**:

- Markdown and JSON report formats
- Pipeline metrics and performance data
- Quality validation results
- Health check summaries

**Usage**:

```bash
python scripts/generate_report.py
python scripts/generate_report.py --run-id abc123
# Outputs: reports/run_*.md, reports/run_*.json
```

#### `test_docs_sync_rule.sh`

**Purpose**: Validate documentation synchronization requirements

**Features**:

- Comprehensive documentation coverage checking
- AGENTS.md and README.md presence validation
- Cross-reference verification
- ADR and rule linkage validation

**Usage**:

```bash
./scripts/test_docs_sync_rule.sh
# Returns: PASS/FAIL with detailed coverage report
```

## 🏗️ Script Architecture

### Common Patterns

All scripts follow consistent patterns:

```python
#!/usr/bin/env python3
"""
Script description and purpose.

Usage:
    python scripts/script_name.py [options]
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infra.db import get_gematria_rw
from src.infra.structured_logger import get_logger

LOG = get_logger(__name__)

def main():
    """Main script execution"""
    # Implementation here
    pass

if __name__ == "__main__":
    main()
```

### Error Handling

Scripts implement robust error handling:

- **Argument Validation**: Check required parameters and formats
- **Database Connection**: Graceful handling of connection failures
- **File Operations**: Safe file creation with backup handling
- **Logging**: Structured logging with appropriate levels

### Configuration

Scripts respect environment configuration:

```bash
# Database connections
export GEMATRIA_DSN=postgresql://...

# Output directories
export EXPORT_DIR=exports

# Logging levels
export LOG_LEVEL=INFO
```

## 🚀 Usage Examples

### Complete Export Pipeline

```bash
# Generate all export formats
make exports.graph     # JSON for visualization
make exports.jsonld    # JSON-LD + RDF for semantic web
python scripts/export_stats.py  # Metrics for dashboards

# Analyze the results
python scripts/analyze_graph.py

# Generate reports
python scripts/generate_report.py
```

### CI/CD Integration

```bash
# In CI/CD pipeline
./scripts/test_docs_sync_rule.sh
python scripts/generate_report.py --run-id $CI_RUN_ID
python scripts/export_graph.py
```

### Development Workflow

```bash
# During development
python scripts/export_graph.py --debug
python scripts/analyze_graph.py --sample-only

# Maintenance tasks
python scripts/generate_report.py --cleanup-old
```

## 📊 Output Formats

### Graph Export (JSON)

```json
{
  "nodes": [
    {
      "id": "concept_123",
      "label": "אלהים",
      "cluster": 1,
      "degree": 0.85,
      "betweenness": 0.12,
      "eigenvector": 0.67
    }
  ],
  "edges": [
    {
      "source": "concept_123",
      "target": "concept_456",
      "strength": 0.92,
      "rerank_score": 0.88
    }
  ],
  "metadata": {
    "node_count": 1250,
    "edge_count": 5432,
    "export_timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Statistics Export (JSON)

```json
{
  "nodes": 1250,
  "edges": 5432,
  "clusters": 8,
  "density": 0.0069,
  "centrality": {
    "avg_degree": 0.045,
    "max_degree": 0.234,
    "avg_betweenness": 0.0012
  }
}
```

### JSON-LD Export

```json
{
  "@context": {
    "@base": "https://gemantria.ai/concept/",
    "label": "http://www.w3.org/2000/01/rdf-schema#label",
    "relatedTo": {
      "@id": "http://schema.org/relatedTo",
      "@type": "@id"
    }
  },
  "@graph": [
    {
      "@id": "concept_123",
      "@type": "Concept",
      "label": "אלהים",
      "relatedTo": "concept_456"
    }
  ]
}
```

## 🔧 Development Guidelines

### Adding New Scripts

1. **Purpose Definition**: Clearly define script's role and scope
2. **Interface Design**: Design command-line interface and options
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Add structured logging throughout
5. **Testing**: Create unit tests for script functionality
6. **Documentation**: Update this README and AGENTS.md

### Script Standards

- **Shebang Line**: `#!/usr/bin/env python3`
- **Executable**: `chmod +x scripts/script_name.py`
- **Path Handling**: Use `pathlib` for cross-platform compatibility
- **Configuration**: Respect environment variables
- **Help Text**: Provide `--help` option with usage information

### Testing Scripts

```python
# Example test structure
def test_export_graph_basic():
    """Test basic graph export functionality"""
    # Setup test data
    # Run script
    # Verify outputs
    pass

def test_export_graph_error_handling():
    """Test error handling in export script"""
    # Test with invalid inputs
    # Verify error messages
    # Check graceful failure
    pass
```

## 📈 Performance Considerations

### Large Dataset Handling

- **Streaming Processing**: Process large graphs without loading entirely in memory
- **Batch Operations**: Handle database operations in configurable batches
- **Progress Indication**: Provide feedback for long-running operations
- **Resource Limits**: Respect memory and time constraints

### Optimization Techniques

- **Database Indexing**: Ensure queries use appropriate indexes
- **Connection Pooling**: Reuse database connections efficiently
- **Caching**: Cache expensive computations where appropriate
- **Parallel Processing**: Utilize multiple cores for CPU-intensive tasks

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)**: AI assistant guide for script development
- **ADR-013**: Documentation synchronization requirements
- **ADR-015**: JSON-LD and RDF export specifications

## 🔄 Maintenance

### Regular Tasks

- **Dependency Updates**: Keep Python packages current
- **Performance Monitoring**: Track execution times and resource usage
- **Error Log Analysis**: Review and address common failure modes
- **Documentation Updates**: Keep usage examples current

### Version Compatibility

- **Python Version**: Support Python 3.11+
- **Database Compatibility**: Work with supported PostgreSQL versions
- **File Format Stability**: Maintain backward compatibility in outputs
- **API Stability**: Avoid breaking changes in script interfaces
