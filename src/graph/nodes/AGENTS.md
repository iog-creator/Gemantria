# AGENTS.md - src/graph/nodes Directory

## Directory Purpose

The `src/graph/nodes/` directory contains base classes and validation utilities for graph node implementations used in the LangGraph pipeline.

## Key Components

### `base.py` - Base Node Classes

**Purpose**: Provides base classes for graph nodes in the LangGraph pipeline

**Key Classes**:
- Base node classes for pipeline node implementations
- Common node functionality and interfaces

### `validation.py` - Node Validation

**Purpose**: Validation utilities for graph nodes and pipeline state

**Key Functions**:
- Node validation logic
- State validation helpers
- Schema validation for node inputs/outputs

## Integration

These components are used by:
- Main graph pipeline (`src/graph/graph.py`)
- Pipeline orchestrator (`scripts/pipeline_orchestrator.py`)
- Node implementations throughout the pipeline

## Testing

Node validation is tested through:
- Integration tests in `tests/integration/`
- Pipeline smoke tests (`make book.smoke`)

