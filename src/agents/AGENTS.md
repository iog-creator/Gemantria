# AGENTS.md - src/agents Directory

## Directory Purpose

The `src/agents/` directory contains agentic planning and orchestration components for the LangGraph-based pipeline. Provides intelligent workflow coordination and decision-making capabilities for complex analysis tasks.

## Key Components

### `planner.py` - Agentic Planner

**Purpose**: Intelligent planning and orchestration agent that coordinates complex analysis workflows using LangGraph state management and decision-making capabilities.

**Key Functions**:
- `plan_analysis_workflow()` - Creates optimized execution plans for analysis tasks
- `coordinate_pipeline_steps()` - Manages inter-step dependencies and resource allocation
- `handle_pipeline_failures()` - Intelligent error recovery and alternative path selection

**Requirements**:
- **State Management**: Full LangGraph state persistence and resumption
- **Decision Intelligence**: Context-aware planning based on pipeline state
- **Resource Optimization**: Efficient allocation of computational resources
- **Failure Resilience**: Graceful handling of partial failures with recovery strategies

## API Contracts

### Planner Interface
```python
def plan_analysis_workflow(state: PipelineState) -> AnalysisPlan:
    """Create intelligent execution plan for analysis tasks."""

def coordinate_pipeline_steps(plan: AnalysisPlan, state: PipelineState) -> ExecutionResult:
    """Coordinate execution of planned pipeline steps."""

def handle_pipeline_failures(error: PipelineError, state: PipelineState) -> RecoveryAction:
    """Determine appropriate recovery action for pipeline failures."""
```

## Testing Strategy

- **Unit Tests**: Individual planning algorithm validation
- **Integration Tests**: End-to-end pipeline orchestration
- **Failure Tests**: Error handling and recovery scenario validation
- **Performance Tests**: Planning algorithm efficiency under load

## Development Guidelines

- Always use typed interfaces for state management
- Include comprehensive error handling and recovery logic
- Document decision criteria and planning algorithms
- Provide clear execution plan serialization for debugging
- Maintain backwards compatibility with existing pipeline steps

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| planner.py | ADR-032 (Organic AI Discovery) |
| Agent orchestration | ADR-019 (Pipeline Architecture) |
