# ADR-015: JSON-LD & RDF Graph Exports + Visualization Interface

## Status

Proposed

## Context

Phase 4 delivers verified embeddings, relations, clusters, and centrality from the semantic concept network. To surface insights and support downstream semantic web tools and GraphRAG systems, we need to export this graph data as JSON-LD and RDF, and provide an interactive web-based visualization.

The current `exports/graph_latest.json` provides basic graph structure but lacks semantic web standards compliance and interactive exploration capabilities.

## Decision

We will implement comprehensive graph exports and visualization:

### Export Formats

- **JSON-LD**: Semantic web standard for linked data with proper @context
- **RDF/Turtle**: W3C standard serialization for knowledge graph interoperability
- **Graph Stats**: Quick metrics for dashboard consumption

### Visualization Interface

- **React-based UI**: Using Visx for D3-powered graph visualization
- **Interactive Features**: Node selection, cluster coloring, centrality highlighting
- **Real-time Loading**: Dynamic import from exported JSON-LD data

### Technical Implementation

- **RDF Library**: Use `rdflib` for semantic web standards compliance
- **URI Scheme**: `https://gemantria.ai/concept/` namespace for global identifiers
- **Ontology**: Basic schema.org relations with custom gematria extensions

## Decision Details

### JSON-LD Structure

```json
{
  "@context": {
    "@vocab": "https://gemantria.ai/concept/",
    "label": "http://www.w3.org/2000/01/rdf-schema#label",
    "relatedTo": "http://schema.org/relatedTo",
    "cosine": "http://schema.org/value",
    "cluster": "http://schema.org/category",
    "degree": "https://gemantria.ai/concept/degree",
    "betweenness": "https://gemantria.ai/concept/betweenness",
    "eigenvector": "https://gemantria.ai/concept/eigenvector"
  },
  "@graph": [
    {
      "@id": "https://gemantria.ai/concept/uuid-here",
      "@type": "Concept",
      "label": "אלהים",
      "cluster": 1,
      "degree": 0.85,
      "betweenness": 0.12,
      "eigenvector": 0.95
    },
    {
      "@id": "https://gemantria.ai/concept/edge/uuid1-uuid2",
      "@type": "Relation",
      "relatedTo": [
        "https://gemantria.ai/concept/uuid1",
        "https://gemantria.ai/concept/uuid2"
      ],
      "cosine": 0.92,
      "rerank_score": 0.88
    }
  ]
}
```

### RDF/Turtle Export

```turtle
@prefix gem: <https://gemantria.ai/concept/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <http://schema.org/> .

gem:uuid-here a gem:Concept ;
  rdfs:label "אלהים" ;
  schema:category 1 ;
  gem:degree 0.85 ;
  gem:betweenness 0.12 ;
  gem:eigenvector 0.95 .

gem:edge/uuid1-uuid2 a gem:Relation ;
  schema:relatedTo gem:uuid1, gem:uuid2 ;
  schema:value 0.92 ;
  gem:rerankScore 0.88 .
```

## Consequences

### Positive

- **Semantic Web Compliance**: Standards-based exports enable integration with knowledge graph tools
- **Interoperability**: JSON-LD and RDF formats work with GraphRAG systems and semantic search
- **Visualization**: Interactive UI provides immediate insight into network structure
- **Future Extensibility**: RDF foundation supports ontology expansion in PR-016

### Negative

- **Dependency Addition**: `rdflib` library increases package size
- **Export Complexity**: Multiple serialization formats require maintenance
- **UI Maintenance**: Additional frontend code to maintain

### Risks

- **Performance**: Large graph serialization may be slow for massive networks
- **Browser Limits**: Very large graphs may exceed browser rendering capabilities

## Alternatives Considered

### Single Format Only

**Option**: Just JSON-LD without RDF/Turtle
**Rejected**: RDF/Turtle provides better semantic web ecosystem integration

### External Visualization Tools

**Option**: Export data and recommend third-party tools (Gephi, GraphXR)
**Rejected**: Custom UI provides better integration with gematria-specific features

### No URI Scheme

**Option**: Use relative identifiers instead of global URIs
**Rejected**: Global URIs enable cross-system linking and semantic web compliance

## Implementation Plan

### Phase 1: Export Infrastructure

1. Create `scripts/export_jsonld.py` with rdflib integration
2. Add RDF/Turtle serialization alongside JSON-LD
3. Create `scripts/export_stats.py` for metrics
4. Update Makefile with export targets

### Phase 2: Visualization UI

1. Create React application structure in `webui/graph/`
2. Implement Visx-based graph visualization
3. Add node details panel and interaction
4. Configure development server and build process

### Phase 3: Integration & Testing

1. Update AGENTS.md documentation
2. Add comprehensive tests for export formats
3. Verify visualization with sample data
4. Document usage in runbook

## Related Decisions

- **ADR-013**: Report generation verification - influences export validation
- **ADR-014**: Relations and patterns - provides graph data structure
- **Future ADR-016**: Metrics expansion and ontology enrichment

## Related Rules

- **015-semantic-export-compliance.mdc**: Enforces JSON-LD and RDF/Turtle format compliance
- **016-visualization-contract-sync.mdc**: Validates frontend-backend data contract consistency
- **017-agent-docs-presence.mdc**: Ensures AGENTS.md presence in all modules
- **018-ssot-linkage.mdc**: Maintains bidirectional ADR-SSOT documentation links

## Related SSOT

- **docs/SSOT/jsonld-schema.md**: Canonical JSON-LD export format specification
- **docs/SSOT/rdf-ontology.md**: RDF vocabulary and ontology definitions
- **docs/SSOT/graph-stats-api.md**: Graph statistics JSON API schema
- **docs/SSOT/webui-contract.md**: Frontend-backend data contract specification
- **docs/SSOT/visualization-config.md**: Visualization configuration parameters

## Verification Criteria

### Export Verification

- [ ] JSON-LD validates against schema.org context
- [ ] RDF/Turtle parses correctly with standard tools
- [ ] All nodes and edges exported with proper metadata
- [ ] URIs resolve to meaningful identifiers

### Visualization Verification

- [ ] Graph renders with proper node positioning
- [ ] Clusters display with distinct colors
- [ ] Node details show on selection
- [ ] Performance acceptable for large graphs (>1000 nodes)

### Integration Verification

- [ ] Exports work with sample pipeline output
- [ ] WebUI loads exported data correctly
- [ ] Makefile targets execute without errors
