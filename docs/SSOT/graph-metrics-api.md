---
originating_ADR: ADR-016
canonical: true
version: 1.0
---

# Graph Metrics API (Canonical)

## Per-Cluster Metrics

### density: float [0..1]
- **Definition**: Proportion of possible edges that exist within the cluster
- **Formula**: `actual_edges / (node_count * (node_count - 1) / 2)`
- **Interpretation**: Higher values indicate tightly connected communities
- **Use Case**: Identify cohesive vs sparse communities

### semantic_diversity: float [0..1]
- **Definition**: Semantic spread within cluster (1 - average cosine similarity)
- **Formula**: `1 - mean(cosine_similarity(concept_embeddings))`
- **Interpretation**: Higher values indicate diverse semantic content
- **Use Case**: Evaluate cluster homogeneity vs heterogeneity

### top_examples: UUID[]
- **Definition**: Most representative concepts by average similarity to cluster
- **Formula**: Sort by `mean(cosine_to_all_other_concepts)` descending, take top K
- **Interpretation**: Exemplar concepts that best represent cluster semantics
- **Use Case**: Cluster labeling and content summarization

## Per-Concept Metrics

### semantic_cohesion: float [0..1]
- **Definition**: Average similarity to other concepts in same cluster
- **Formula**: `mean(cosine_to_cluster_members_excluding_self)`
- **Interpretation**: How well concept fits within its community
- **Use Case**: Identify peripheral vs central concepts within clusters

### bridge_score: float [0..1]
- **Definition**: Average similarity to concepts outside cluster
- **Formula**: `mean(cosine_to_outside_cluster_concepts)`
- **Interpretation**: Potential for cross-cluster connectivity
- **Use Case**: Identify concepts that bridge different semantic areas

### diversity_local: float [0..1]
- **Definition**: Semantic variety in concept's neighborhood (1 - average similarity to neighbors)
- **Formula**: `1 - mean(cosine_to_direct_neighbors)`
- **Interpretation**: Local semantic diversity around concept
- **Use Case**: Find concepts in diverse semantic contexts

## JSON-LD Keys

When metrics are available, they appear in JSON-LD exports with these keys:
- `semanticCohesion` (per-concept)
- `bridgeScore` (per-concept)
- `diversityLocal` (per-concept)
- `clusterDensity` (attached to all concepts in cluster)
- `clusterDiversity` (attached to all concepts in cluster)
- `topExamples` (attached to all concepts in cluster)

## Contract

- **Omit nulls**: Metrics with null values are not included in exports
- **Sampling may apply**: Large clusters use sampling for diversity calculations
- **Values are snapshots**: Metrics reflect computation time, not real-time state
- **Optional presence**: Metrics tables may not exist in all deployments
- **Float precision**: Values are stored as PostgreSQL FLOAT (double precision)

## Computation Order

Metrics should be computed after graph analysis:
1. `analyze_graph.py` → clusters + centrality
2. `analyze_metrics.py` → insight metrics
3. Export scripts → include metrics in outputs

## Storage Schema

```sql
-- Per-concept metrics
CREATE TABLE concept_metrics (
  concept_id UUID PRIMARY KEY,
  cluster_id INTEGER,
  semantic_cohesion FLOAT,
  bridge_score FLOAT,
  diversity_local FLOAT,
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Per-cluster aggregations
CREATE TABLE cluster_metrics (
  cluster_id INTEGER PRIMARY KEY,
  size INTEGER NOT NULL,
  density FLOAT,
  semantic_diversity FLOAT,
  top_examples UUID[],
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Overview view for dashboards
CREATE VIEW v_metrics_overview AS
SELECT
  COUNT(*)::int AS node_ct,
  (SELECT COUNT(*) FROM concept_relations)::int AS edge_ct,
  (SELECT COUNT(DISTINCT cluster_id) FROM concept_clusters)::int AS cluster_ct,
  COALESCE((SELECT AVG(density) FROM cluster_metrics),0)::float AS avg_cluster_density,
  COALESCE((SELECT AVG(semantic_diversity) FROM cluster_metrics),0)::float AS avg_cluster_diversity;
```
