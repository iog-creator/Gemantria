# AGENTS.md - Scripts Directory

## Directory Purpose
The `scripts/` directory contains executable scripts for pipeline operations, reporting, testing, and maintenance tasks. These scripts provide command-line interfaces for common development and operational workflows.

## Key Scripts

### `generate_report.py` - Pipeline Reporting (Critical - Always Apply)
**Purpose**: Generate comprehensive markdown and JSON reports from pipeline execution data
**Requirements** (Report Generation Verification):
- **Automatic Execution**: Run after every pipeline execution
- **Template Validation**: Exact markdown/JSON templates with no missing sections
- **Real Data Only**: Actual pipeline data (enrichments, metrics, network stats) - never zeros/empty
- **File Creation**: Proper timestamps and naming conventions in `reports/` directory
- **No Trust Tests**: Manual verification required; tests insufficient for accuracy
- **Database Integrity**: All required tables exist; column names match schemas
**Capabilities**:
- Aggregated metrics from recent pipeline runs
- Qwen health verification status (live inference proof)
- Network aggregation statistics and edge analysis
- Performance and throughput analysis
**Usage**:
```bash
python scripts/generate_report.py --run-id <uuid>  # Specific run report
python scripts/generate_report.py                 # Recent aggregated report
```
**Verification Checklist**:
- [ ] Reports contain non-zero enrichment data (not "0 enrichments")
- [ ] JSON reports have complete metrics data structures
- [ ] Timestamps match actual pipeline execution times
- [ ] All template sections populated with real database data
- [ ] Qwen health verification shows verified=true with latencies

### `ci-no-mocks.sh` - CI Quality Gate
**Purpose**: Ensure production readiness by running tests without mocks
**Requirements**:
- All external services available (LM Studio, databases)
- No mock data or simulated responses
- Full end-to-end pipeline validation
**Execution**:
```bash
./scripts/ci-no-mocks.sh  # Sets USE_QWEN_EMBEDDINGS=true, etc.
```

### `analyze_graph.py` - Graph Pattern Analysis (NEW)
**Purpose**: Analyze semantic concept network for communities and centrality patterns
**Requirements**:
- Builds NetworkX graph from database relations
- Computes Louvain communities and centrality measures
- Persists results to `concept_clusters` and `concept_centrality` tables
- Integrates with pipeline for automated pattern discovery
**Capabilities**:
- Community detection using Louvain algorithm
- Centrality analysis (degree, betweenness, eigenvector)
- Database persistence for reporting and visualization
**Usage**:
```bash
python scripts/analyze_graph.py  # Analyze current network and persist patterns
make analyze.graph              # Same via Makefile target
```

### `export_graph.py` - Graph Visualization Export (NEW)
**Purpose**: Export semantic concept network as viz-ready JSON for UI consumption
**Requirements**:
- Creates graph_latest.json with nodes, edges, clusters, and centrality
- Includes cluster assignments and centrality scores
- Proper error handling and logging
- Configurable export directory via EXPORT_DIR environment variable
**Capabilities**:
- Full graph topology export
- Cluster and centrality metadata inclusion
- Timestamped file naming for versioning
- Integration with visualization tools and dashboards
**Usage**:
```bash
python scripts/export_graph.py   # Export current network to JSON
make exports.graph              # Same via Makefile target
```

### `export_jsonld.py` - Semantic Web Graph Export (NEW)
**Purpose**: Export semantic concept network as JSON-LD and RDF/Turtle for knowledge graph interoperability
**Requirements**:
- **JSON-LD Export**: Creates `graph_latest.jsonld` with proper @context and linked data structure
- **RDF/Turtle Export**: Creates `graph_latest.ttl` with W3C standard serialization
- **URI Namespace**: Uses `https://gemantria.ai/concept/` namespace for global identifiers
- **Metadata Integration**: Optionally includes concept metadata from `concept_metadata` table
- **Semantic Compliance**: Follows schema.org and custom gematria ontologies
**Capabilities**:
- JSON-LD with proper @context for semantic web tools
- RDF/Turtle serialization using rdflib for knowledge graph ingestion
- Global URIs for cross-system linking and GraphRAG compatibility
- Optional rich metadata (descriptions, sources, languages)
- Cluster and centrality data as RDF properties
**Usage**:
```bash
python scripts/export_jsonld.py  # Export current network to JSON-LD and RDF/Turtle
make exports.jsonld             # Same via Makefile target
```
**Output Files**:
- `exports/graph_latest.jsonld` - JSON-LD format for web standards
- `exports/graph_latest.ttl` - RDF/Turtle format for knowledge graphs
**Verification Checklist**:
- [ ] JSON-LD validates against schema.org context
- [ ] RDF/Turtle parses correctly with standard tools
- [ ] All nodes and edges exported with proper URIs
- [ ] Metadata included when `concept_metadata` table exists

### `export_stats.py` - Graph Statistics Export (NEW)
**Purpose**: Export quick graph statistics for dashboard consumption and monitoring
**Requirements**:
- **Aggregated Metrics**: Computes comprehensive network statistics
- **Health Indicators**: Provides network health and quality metrics
- **Dashboard Ready**: JSON output formatted for UI consumption
- **Real-time Data**: Direct database queries for current state
**Capabilities**:
- Node/edge/cluster counts and distributions
- Centrality averages and distributions
- Edge strength analysis (strong/weak connection counts)
- Network density and health indicators
- Largest cluster identification
**Usage**:
```bash
python scripts/export_stats.py   # Export current network statistics
```
**Output Format**:
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
  },
  "edge_distribution": {
    "strong_edges": 1200,
    "weak_edges": 2800,
    "avg_cosine": 0.76
  }
}
```

### verify_pr016_pr017.py — Metrics Contract Verifier
**Purpose:** Ensures exported statistics reflect live DB and UI contracts.  
**Rule References:** 021 (Stats Proof), 022 (Visualization Contract Sync), 006 (AGENTS.md Governance), 013 (Report Verification)  
**Usage:**
```bash
python scripts/verify_pr016_pr017.py --dsn "$GEMATRIA_DSN" \
  --stats exports/graph_stats.json \
  --graph exports/graph_latest.json
```

**Outputs:** `VERIFIER_PASS` on success; fails closed otherwise.

### generate_forest.py — Forest Overview Generator
**Purpose:** Auto-rebuilds high-level project map from ADRs, rules, and CI files.
**Rule References:** 025 (Phase Gate & Forest Sync), 006 (AGENTS.md Governance)
**Capabilities:**
- Scans `.cursor/rules/` for active rules
- Lists CI workflows from `.github/workflows/`
- Catalogs ADRs from `docs/ADRs/`
- Generates `docs/forest/overview.md`
- Updates `docs/VERIFICATION_MATRIX.md`
**Usage:**
```bash
python scripts/generate_forest.py  # Rebuild forest overview
make generate.forest              # Same via Makefile target
```
**Outputs:**
- `docs/forest/overview.md` - Human-readable project map
- `docs/VERIFICATION_MATRIX.md` - Rule ↔ script ↔ CI ↔ evidence mappings
- Console summary of changes

## Script Categories

### Pipeline Operations
- **Execution**: Run pipeline with various configurations
- **Monitoring**: Health checks and status reporting
- **Maintenance**: Database migrations and cleanup
- **Analysis**: Graph pattern discovery and community detection (`analyze_graph.py`)
- **Export**: Visualization data export (`export_graph.py`)

### Development Tools
- **Testing**: Automated test execution and reporting
- **Linting**: Code quality and style validation
- **Documentation**: Generate API docs and reports
- **Quality Gates**: CI validation without mocks (`ci-no-mocks.sh`)

### Deployment Scripts
- **Setup**: Environment preparation and configuration
- **Migration**: Database schema updates and data migration
- **Validation**: Post-deployment verification

## Script Standards

### Command-Line Interface
- **Help**: `--help` for all scripts
- **Arguments**: Clear parameter naming and validation
- **Output**: Consistent formatting and error codes
- **Logging**: Structured logging with appropriate verbosity

### Error Handling
- **Graceful Failures**: Clear error messages and exit codes
- **Recovery**: Where possible, suggest remediation steps
- **Logging**: Detailed error information for debugging

### Configuration
- **Environment**: Use environment variables for configuration
- **Defaults**: Sensible defaults with override capability
- **Validation**: Input validation with helpful error messages

## Development Guidelines

### Adding New Scripts
1. **Purpose**: Clear, single responsibility
2. **Interface**: Command-line arguments and help
3. **Error Handling**: Robust error handling and logging
4. **Testing**: Unit tests for script logic
5. **Documentation**: Inline help and README updates

### Script Maintenance
1. **Updates**: Keep scripts current with API changes
2. **Testing**: Automated testing of script execution
3. **Documentation**: Update usage examples and parameters
4. **Deprecation**: Clear migration path for replaced scripts

## Execution Environment

### Dependencies
- **Python**: Required version and virtual environment
- **System Tools**: bash, make, git for CI/CD integration
- **External Services**: Database, LM Studio for full functionality

### Security Considerations
- **Input Validation**: Sanitize all user inputs
- **Credentials**: Secure handling of API keys and passwords
- **Permissions**: Appropriate file and database permissions
- **Audit Trail**: Logging of script execution and changes

## Testing Strategy

### Script Testing
- **Unit Tests**: Test script logic in isolation
- **Integration Tests**: Test with real dependencies
- **End-to-End**: Full workflow validation

### CI/CD Integration
- **Automated Execution**: Scripts run in CI pipelines
- **Artifact Generation**: Reports and logs as CI artifacts
- **Quality Gates**: Script success as merge requirements

## Maintenance & Operations

### Monitoring
- **Execution Logs**: Track script runs and performance
- **Failure Alerts**: Notification for script failures
- **Performance Metrics**: Execution time and resource usage

### Troubleshooting
- **Debug Mode**: Verbose logging for issue diagnosis
- **Dry Run**: Preview changes without execution
- **Rollback**: Safe reversal of script actions

### Documentation
- **README**: Script catalog with usage examples
- **Inline Help**: `--help` for all scripts
- **Runbooks**: Operational procedures using scripts
