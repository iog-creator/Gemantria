---
originating_ADR: ADR-015
canonical: true
version: 1.0
---

# SSOT: WebUI Data Contract

## Overview

This document defines the contract between backend data exports and the React visualization frontend. This serves as the single source of truth for data format expectations, file locations, and API compatibility between the pipeline and web interface.

## File Locations and Formats

### Primary Data Sources

#### Graph Topology Data

- **File**: `exports/graph_latest.json`
- **Purpose**: Force-directed graph visualization
- **Format**: JSON with nodes and edges arrays
- **Update Frequency**: After each pipeline run

#### Semantic Web Data

- **File**: `exports/graph_latest.jsonld`
- **Purpose**: JSON-LD export for semantic web tools
- **Format**: JSON-LD with @context and @graph
- **Update Frequency**: After each pipeline run

#### Statistics Data

- **File**: Runtime generated (not persisted)
- **Purpose**: Dashboard metrics and health indicators
- **Format**: JSON statistics object
- **Endpoint**: `python scripts/export_stats.py` (stdout)

## Graph Data Format (`graph_latest.json`)

### Root Structure

```json
{
  "nodes": [...],
  "edges": [...],
  "metadata": {
    "node_count": 1250,
    "edge_count": 5432,
    "cluster_count": 8,
    "export_timestamp": "2024-01-15T10:30:45.123456"
  }
}
```

### Node Object Schema

```json
{
  "id": "uuid-string",
  "label": "אלהים",
  "cluster": 1,
  "degree": 0.85,
  "betweenness": 0.12,
  "eigenvector": 0.95
}
```

### Edge Object Schema

```json
{
  "source": "source-uuid",
  "target": "target-uuid",
  "strength": 0.92,
  "rerank": 0.88,
  "yes": true
}
```

## Property Mappings

### Node Properties

| Backend Field | Frontend Field | Type    | Required | Description                     |
| ------------- | -------------- | ------- | -------- | ------------------------------- |
| `concept_id`  | `id`           | string  | ✓        | Unique identifier (UUID)        |
| `label`       | `label`        | string  | ✓        | Display name (falls back to id) |
| `cluster_id`  | `cluster`      | integer | ✗        | Community assignment            |
| `degree`      | `degree`       | float   | ✗        | Degree centrality (0.0-1.0)     |
| `betweenness` | `betweenness`  | float   | ✗        | Betweenness centrality          |
| `eigenvector` | `eigenvector`  | float   | ✗        | Eigenvector centrality          |

### Edge Properties

| Backend Field  | Frontend Field | Type    | Required | Description           |
| -------------- | -------------- | ------- | -------- | --------------------- |
| `source_id`    | `source`       | string  | ✓        | Source concept UUID   |
| `target_id`    | `target`       | string  | ✓        | Target concept UUID   |
| `cosine`       | `strength`     | float   | ✓        | Edge weight (0.0-1.0) |
| `rerank_score` | `rerank`       | float   | ✗        | Reranker confidence   |
| `decided_yes`  | `yes`          | boolean | ✗        | Reranker approval     |

## Frontend Consumption Contract

### Data Loading

```typescript
interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: {
    node_count: number;
    edge_count: number;
    cluster_count: number;
    export_timestamp: string;
  };
}

interface GraphNode {
  id: string;
  label: string;
  cluster?: number;
  degree?: number;
  betweenness?: number;
  eigenvector?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  strength: number;
  rerank?: number;
  yes?: boolean;
}
```

### Visualization Mapping

#### Node Rendering

- **Size**: Proportional to `degree` (scaled 5-25px radius)
- **Color**: Categorical by `cluster` (11-color palette)
- **Label**: `label` truncated to 10 chars if longer
- **Position**: Force-directed layout (x,y calculated)

#### Edge Rendering

- **Width**: Proportional to `strength` (scaled 1-5px)
- **Opacity**: `strength` mapped to 0.1-1.0 alpha
- **Color**: Fixed gray (#999)
- **Style**: Directional particles for strong edges

### Interaction Handling

#### Node Selection

- **Trigger**: Click event on node
- **State**: Single node selection (null to deselect)
- **Feedback**: Stroke color change (selected: black, hover: gray)

#### Detail Display

- **Panel**: Right sidebar with selected node details
- **Fields**: All node properties formatted appropriately
- **Fallback**: "Click on a node to see details" when none selected

## Error Handling Contract

### File Not Found

- **Condition**: `exports/graph_latest.json` missing
- **Frontend Response**: Show loading error with retry button
- **Recovery**: Manual page refresh after data export

### Invalid JSON

- **Condition**: Malformed JSON in data files
- **Frontend Response**: Parse error display with details
- **Recovery**: Check pipeline export logs

### Empty Data

- **Condition**: Valid JSON but empty nodes/edges arrays
- **Frontend Response**: "No graph data available" message
- **Recovery**: Run pipeline to generate data

## Performance Contract

### Data Volume Expectations

- **Small Networks**: < 100 nodes (instant rendering)
- **Medium Networks**: 100-1000 nodes (< 2s rendering)
- **Large Networks**: 1000-10000 nodes (< 10s rendering)
- **Maximum Supported**: 10000 nodes (with performance warnings)

### Rendering Optimizations

- **Force Simulation**: 100 ticks cooldown
- **Batching**: Process nodes/edges in chunks if needed
- **Memory Management**: Clean up unused DOM elements
- **Responsive Updates**: Throttle resize and interaction events

## Version Compatibility

### Data Format Versions

- **v1.0**: Initial implementation (current)
- **Backwards Compatibility**: Frontend must handle missing optional fields
- **Forward Compatibility**: New fields ignored gracefully

### Breaking Changes

- **Field Removal**: Requires frontend update
- **Type Changes**: Requires frontend update
- **Required Field Addition**: Requires frontend update

## Testing Contract

### Frontend Tests

- **Data Loading**: Valid and invalid JSON handling
- **Rendering**: Node/edge visualization correctness
- **Interaction**: Selection and detail display
- **Performance**: Rendering time for various data sizes

### Integration Tests

- **Export Verification**: Frontend can load pipeline output
- **End-to-End**: Pipeline → Export → Frontend display
- **Data Consistency**: Frontend display matches database content

## Development Workflow

### Local Development

```bash
# Backend: Export test data
make exports.graph

# Frontend: Start dev server
make webui  # Opens localhost:5173
```

### Data Synchronization

1. Run pipeline to generate fresh data
2. Export graph data (`make exports.graph`)
3. Frontend automatically loads new data
4. Manual refresh if data changes during development

## Deployment Contract

### Build Process

1. **Frontend Build**: `npm run build` creates optimized bundle
2. **Static Assets**: Single-page app with no server requirements
3. **Data Access**: Fetches JSON from same domain (`/exports/*.json`)

### CDN Deployment

- **Cache Strategy**: Cache-bust on new deployments
- **CORS**: Must allow data fetch from export directory
- **HTTPS**: Required for production deployments

## Monitoring and Observability

### Frontend Metrics

- **Load Times**: Data fetch and rendering performance
- **Error Rates**: Failed data loads and parse errors
- **User Interactions**: Node selections and navigation patterns

### Data Quality Monitoring

- **Freshness**: Compare `export_timestamp` with current time
- **Completeness**: Validate required fields present
- **Consistency**: Cross-check counts with actual data

## Related Documentation

- **ADR-015**: JSON-LD & Visualization implementation details
- **JSON-LD Schema**: Linked data export format (jsonld-schema.md)
- **RDF Ontology**: Semantic web vocabulary (rdf-ontology.md)
- **Graph Stats API**: Statistics export format (graph-stats-api.md)
