# Graph Processing & Pipeline Orchestration

This module implements the core LangGraph pipeline that orchestrates the entire Gemantria semantic network processing workflow. It coordinates the flow of data through various processing nodes, manages state persistence, and ensures deterministic execution of the text analysis pipeline.

## 🎯 Purpose

The graph module serves as the central coordinator for the Gemantria pipeline, implementing:

- **Pipeline Orchestration**: Coordinate execution of processing nodes
- **State Management**: Manage data flow and persistence between steps
- **Error Handling**: Graceful handling of pipeline failures and recovery
- **Batch Processing**: Handle large-scale text analysis in manageable chunks
- **Graph Construction**: Build semantic networks from processed data

## 🏗️ Architecture

### LangGraph Pipeline Structure

The pipeline is implemented as a directed acyclic graph (DAG) where each node represents a processing step:

```
Input → Extraction → Validation → Enrichment → Network → Analysis → Output
    ↓         ↓         ↓         ↓         ↓         ↓         ↓
  Error    Error     Error    Error    Error    Error    Error
 Handling Handling  Handling Handling Handling Handling Handling
```

### Key Components

#### Pipeline Orchestrator (`graph.py`)

- **Main Entry Point**: `python -m src.graph.graph --book Genesis`
- **Configuration Management**: Load and validate pipeline settings
- **Execution Control**: Start, monitor, and complete pipeline runs
- **Result Aggregation**: Collect and format final outputs

#### Node Coordination (`pipeline.py`)

- **LangGraph Setup**: Define the graph structure and node connections
- **Data Flow**: Manage state transitions between processing steps
- **Conditional Logic**: Handle branching based on data characteristics
- **Checkpointing**: Save progress for resumable execution

#### Processing Nodes (`nodes/`)

- **Individual Steps**: Modular processing components
- **State Updates**: Transform and enrich pipeline state
- **Validation Gates**: Ensure data quality at each step
- **Metrics Collection**: Track performance and quality metrics

## 🔄 Pipeline Flow

### Phase 1: Text Processing

1. **Input Validation**: Verify source text and parameters
2. **Noun Extraction**: Identify Hebrew nouns for analysis
3. **Basic Validation**: Check data integrity and format

### Phase 2: Semantic Enrichment

1. **Gematria Calculation**: Compute numerical values
2. **AI Enrichment**: Generate semantic insights via Qwen models
3. **Confidence Validation**: Verify AI-generated content quality

### Phase 3: Network Construction

1. **Embedding Generation**: Create vector representations
2. **Similarity Analysis**: Find relationships between concepts
3. **Graph Building**: Construct semantic network structure

### Phase 4: Analysis & Export

1. **Community Detection**: Identify concept clusters
2. **Centrality Analysis**: Calculate importance metrics
3. **Export Generation**: Create multiple output formats

## ⚙️ Configuration & Parameters

### Pipeline Settings

```python
# Core pipeline configuration
BATCH_SIZE = 50          # Nouns processed per batch
ALLOW_PARTIAL = False    # Require minimum batch size
WORKFLOW_ID = "gematria.v1"  # Pipeline version identifier

# Processing parameters
VECTOR_DIM = 1024        # Embedding dimensionality
EDGE_STRONG = 0.90       # Strong relationship threshold
EDGE_WEAK = 0.75         # Weak relationship threshold

# Quality gates
GEMATRIA_CONFIDENCE_THRESHOLD = 0.90
AI_CONFIDENCE_THRESHOLD = 0.95
```

### Execution Modes

- **Full Pipeline**: Complete end-to-end processing
- **Resume Mode**: Continue from last checkpoint
- **Validation Only**: Check existing data quality
- **Export Only**: Regenerate outputs from existing data

## 🛡️ Safety & Reliability

### Quality Gates

- **Batch Validation**: Minimum 50 nouns required (ALLOW_PARTIAL=1 to override)
- **Qwen Live Gate**: AI models must be verified operational
- **Data Integrity**: All processing steps include validation
- **Checkpoint Recovery**: Automatic recovery from failures

### Error Handling

- **Graceful Degradation**: Continue processing despite individual failures
- **Detailed Logging**: Comprehensive error tracking and reporting
- **Recovery Mechanisms**: Automatic retry for transient failures
- **Failure Isolation**: Contain errors to prevent pipeline-wide failure

## 📊 Performance & Scaling

### Execution Characteristics

- **Batch Processing**: Process large datasets in manageable chunks
- **Parallel Execution**: Concurrent processing where possible
- **Memory Management**: Efficient handling of large text volumes
- **Progress Tracking**: Real-time monitoring of pipeline progress

### Performance Metrics

- **Throughput**: Nouns processed per minute
- **Latency**: Time per processing batch
- **Success Rate**: Percentage of successful completions
- **Quality Score**: Average confidence and validation scores

## 🔧 Usage Examples

### Basic Pipeline Execution

```bash
# Run full pipeline for Genesis
python -m src.graph.graph --book Genesis

# Process with custom batch size
python -m src.graph.graph --book Genesis --batch-size 25

# Resume from checkpoint
python -m src.graph.graph --resume --run-id abc123

# Validate existing data
python -m src.graph.graph --validate-only
```

### Programmatic Usage

```python
from src.graph.pipeline import GemantriaPipeline

# Initialize pipeline
pipeline = GemantriaPipeline(
    book="Genesis",
    batch_size=50,
    allow_partial=False
)

# Execute pipeline
results = pipeline.run()

# Access results
print(f"Processed {results.node_count} nodes")
print(f"Created {results.edge_count} relationships")
```

## 📈 Monitoring & Observability

### Pipeline Metrics

- **Execution Time**: Total and per-step timing
- **Success Rates**: Completion rates for each processing step
- **Data Quality**: Validation scores and confidence metrics
- **Resource Usage**: Memory and CPU utilization

### Logging & Tracing

- **Structured Logging**: JSON-formatted logs for analysis
- **Progress Updates**: Real-time status reporting
- **Error Tracking**: Detailed error information and context
- **Audit Trail**: Complete record of pipeline execution

## 🧪 Testing & Validation

### Test Coverage

- **Unit Tests**: Individual pipeline components
- **Integration Tests**: End-to-end pipeline execution
- **Performance Tests**: Benchmarking under various loads
- **Reliability Tests**: Failure mode and recovery testing

### Validation Checks

- **Data Consistency**: Verify inputs and outputs match expectations
- **Algorithm Correctness**: Validate mathematical and logical operations
- **Performance Requirements**: Ensure acceptable execution times
- **Quality Standards**: Meet confidence and accuracy thresholds

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)**: AI assistant guide for pipeline development
- **[Parent](../README.md)**: Core source code overview
- **ADR-004**: LangGraph pipeline architecture decision

## 🔄 Development Workflow

### Adding New Pipeline Steps

1. **Design**: Define the processing step and its inputs/outputs
2. **Implement**: Create the processing node in `nodes/`
3. **Integrate**: Add the node to the pipeline graph
4. **Test**: Add comprehensive test coverage
5. **Document**: Update AGENTS.md and this README

### Modifying Pipeline Flow

1. **Analyze Impact**: Understand effects on downstream processing
2. **Update Graph**: Modify node connections and conditional logic
3. **Test Integration**: Verify end-to-end pipeline still works
4. **Update Documentation**: Reflect changes in all relevant docs

### Performance Optimization

1. **Profile**: Identify bottlenecks in pipeline execution
2. **Optimize**: Improve algorithms or parallelize where possible
3. **Test**: Verify performance improvements don't affect quality
4. **Document**: Record optimization decisions and results
