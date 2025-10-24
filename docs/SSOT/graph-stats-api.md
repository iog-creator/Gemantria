---
originating_ADR: ADR-015
canonical: true
version: 1.0
---

# SSOT: Graph Statistics API

## Overview

This document defines the canonical schema for graph statistics exports from the Gematria pipeline. This serves as the single source of truth for the JSON format used by dashboard components and monitoring systems.

## Response Format

### Root Structure

```json
{
  "nodes": 1250,
  "edges": 5432,
  "clusters": 8,
  "density": 0.0069,
  "centrality": {
    "avg_degree": 0.045,
    "max_degree": 0.234,
    "avg_betweenness": 0.0012,
    "max_betweenness": 0.089,
    "avg_eigenvector": 0.032,
    "max_eigenvector": 0.156
  },
  "edge_distribution": {
    "strong_edges": 1200,
    "weak_edges": 2800,
    "very_weak_edges": 1432,
    "avg_cosine": 0.76,
    "min_cosine": 0.15,
    "max_cosine": 0.98
  },
  "cluster_sizes": [
    { "cluster_id": 1, "size": 245 },
    { "cluster_id": 2, "size": 189 },
    { "cluster_id": 3, "size": 156 }
  ],
  "largest_cluster": {
    "id": 1,
    "size": 245
  },
  "health": {
    "has_nodes": true,
    "has_edges": true,
    "has_clusters": true,
    "density_reasonable": true
  },
  "export_timestamp": "2024-01-15T10:30:45.123456"
}
```

## Field Definitions

### Basic Counts

- **`nodes`** (integer): Total number of concept nodes in the network
- **`edges`** (integer): Total number of semantic relations between concepts
- **`clusters`** (integer): Number of distinct clusters/communities identified

### Network Properties

- **`density`** (float): Network density (actual edges / possible edges), 0.0-1.0

### Centrality Statistics

- **`centrality.avg_degree`** (float): Average degree centrality across all nodes
- **`centrality.max_degree`** (float): Maximum degree centrality score
- **`centrality.avg_betweenness`** (float): Average betweenness centrality
- **`centrality.max_betweenness`** (float): Maximum betweenness centrality score
- **`centrality.avg_eigenvector`** (float): Average eigenvector centrality
- **`centrality.max_eigenvector`** (float): Maximum eigenvector centrality score

### Edge Distribution

- **`edge_distribution.strong_edges`** (integer): Edges with cosine ≥ 0.90
- **`edge_distribution.weak_edges`** (integer): Edges with 0.75 ≤ cosine < 0.90
- **`edge_distribution.very_weak_edges`** (integer): Edges with cosine < 0.75
- **`edge_distribution.avg_cosine`** (float): Average cosine similarity across all edges
- **`edge_distribution.min_cosine`** (float): Minimum cosine similarity score
- **`edge_distribution.max_cosine`** (float): Maximum cosine similarity score

### Cluster Analysis

- **`cluster_sizes`** (array): Array of cluster size objects
  - **`cluster_id`** (integer): Cluster identifier
  - **`size`** (integer): Number of nodes in this cluster
- **`largest_cluster.id`** (integer): ID of the largest cluster
- **`largest_cluster.size`** (integer): Size of the largest cluster

### Health Indicators

- **`health.has_nodes`** (boolean): Whether the network contains any nodes
- **`health.has_edges`** (boolean): Whether the network contains any edges
- **`health.has_clusters`** (boolean): Whether clustering has been performed
- **`health.density_reasonable`** (boolean): Whether network density is in expected range (0.001-0.1)

### Metadata

- **`export_timestamp`** (string): ISO 8601 timestamp of when statistics were generated

## Validation Rules

### Required Fields

All fields except `export_timestamp` are required in successful responses.

### Type Constraints

- Integer fields: Must be non-negative integers
- Float fields: Must be valid floating-point numbers in expected ranges
- Boolean fields: Must be true/false
- String fields: Must be valid ISO 8601 timestamps
- Array fields: Must contain valid objects with required properties

### Value Ranges

- **Centrality scores**: 0.0 ≤ value ≤ 1.0 (typically much lower for betweenness)
- **Cosine similarity**: 0.0 ≤ value ≤ 1.0
- **Network density**: 0.0 ≤ value ≤ 1.0 (typically 0.001-0.1 for semantic networks)
- **Counts**: ≥ 0

### Consistency Checks

- `strong_edges + weak_edges + very_weak_edges = edges`
- `largest_cluster.size` should equal max value in `cluster_sizes`
- `sum(cluster_sizes[].size) = nodes`

## Calculation Methods

### Basic Counts

```sql
SELECT COUNT(*) FROM concept_network;  -- nodes
SELECT COUNT(*) FROM concept_relations;  -- edges
SELECT COUNT(DISTINCT cluster_id) FROM concept_clusters;  -- clusters
```

### Network Density

```
density = edges / (nodes * (nodes - 1) / 2)
```

### Centrality Statistics

```sql
SELECT
  AVG(degree), MAX(degree),
  AVG(betweenness), MAX(betweenness),
  AVG(eigenvector), MAX(eigenvector)
FROM concept_centrality;
```

### Edge Distribution

```sql
SELECT
  SUM(CASE WHEN cosine >= 0.90 THEN 1 ELSE 0 END) as strong_edges,
  SUM(CASE WHEN cosine >= 0.75 AND cosine < 0.90 THEN 1 ELSE 0 END) as weak_edges,
  SUM(CASE WHEN cosine < 0.75 THEN 1 ELSE 0 END) as very_weak_edges,
  AVG(cosine), MIN(cosine), MAX(cosine)
FROM concept_relations;
```

## Health Thresholds

### Network Health

- **has_nodes**: `nodes > 0`
- **has_edges**: `edges > 0`
- **has_clusters**: `clusters > 0`
- **density_reasonable**: `0.001 ≤ density ≤ 0.1`

### Warning Conditions

- `density < 0.001`: Network may be too sparse
- `density > 0.1`: Network may be too dense (over-connected)
- `strong_edges < edges * 0.1`: Too few high-confidence relations

## Consumer Guidelines

### Dashboard Integration

1. Display basic counts prominently (nodes, edges, clusters)
2. Show network density as percentage with health indicator
3. Visualize centrality distributions as histograms
4. Chart edge distribution as stacked bar chart
5. Display cluster sizes as sorted bar chart

### Monitoring Integration

1. Alert when `has_nodes`, `has_edges`, or `has_clusters` become false
2. Monitor density trends for network evolution
3. Track centrality score changes over time
4. Alert on unusual edge distributions

### API Consumption

1. Parse as standard JSON
2. Validate required fields exist
3. Check value ranges for data quality
4. Use `export_timestamp` for freshness validation

## Extensions and Evolution

### Optional Fields

Future versions may add optional fields without breaking existing consumers.

### Versioning

- API follows semantic versioning
- Breaking changes increment major version
- New optional fields increment minor version

### Backwards Compatibility

- Required fields cannot be removed
- Field types cannot change
- New fields must be optional

## Implementation Notes

### Export Process

1. Execute SQL queries for all statistics
2. Aggregate results into response structure
3. Validate against schema constraints
4. Add export timestamp
5. Output as formatted JSON

### Performance Considerations

- All queries use efficient indexes
- Calculations performed in single database round-trip
- Results cached for dashboard refresh cycles

### Error Handling

- Database connection failures return error objects
- Invalid data triggers validation warnings
- Export failures logged with detailed error information

## Related Documentation

- **ADR-015**: JSON-LD & Visualization implementation details
- **JSON-LD Schema**: Linked data export format (jsonld-schema.md)
- **RDF Ontology**: Semantic web vocabulary (rdf-ontology.md)
- **WebUI Contract**: Frontend consumption specification (webui-contract.md)
