---
originating_ADR: ADR-015
canonical: true
version: 1.0
---

# SSOT: JSON-LD Schema for Concept Network Exports

## Overview

This document defines the canonical JSON-LD schema used for exporting semantic concept networks from the Gematria pipeline. This serves as the single source of truth for JSON-LD structure, @context definitions, and semantic web compliance.

## @Context Definition

```json
{
  "@context": {
    "@version": 1.1,
    "@vocab": "https://gemantria.ai/concept/",
    "@base": "https://gemantria.ai/concept/",
    "label": {
      "@id": "http://www.w3.org/2000/01/rdf-schema#label",
      "@container": "@language"
    },
    "relatedTo": {
      "@id": "http://schema.org/relatedTo",
      "@type": "@id"
    },
    "cosine": {
      "@id": "http://schema.org/value",
      "@type": "http://www.w3.org/2001/XMLSchema#double"
    },
    "rerankScore": {
      "@id": "https://gemantria.ai/concept/rerankScore",
      "@type": "http://www.w3.org/2001/XMLSchema#double"
    },
    "cluster": {
      "@id": "http://schema.org/category",
      "@type": "http://www.w3.org/2001/XMLSchema#integer"
    },
    "degree": {
      "@id": "https://gemantria.ai/concept/degree",
      "@type": "http://www.w3.org/2001/XMLSchema#double"
    },
    "betweenness": {
      "@id": "https://gemantria.ai/concept/betweenness",
      "@type": "http://www.w3.org/2001/XMLSchema#double"
    },
    "eigenvector": {
      "@id": "https://gemantria.ai/concept/eigenvector",
      "@type": "http://www.w3.org/2001/XMLSchema#double"
    },
    "description": {
      "@id": "http://schema.org/description",
      "@container": "@language"
    },
    "source": {
      "@id": "http://schema.org/source",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "language": {
      "@id": "http://schema.org/inLanguage",
      "@type": "http://www.w3.org/2001/XMLSchema#string"
    },
    "decidedYes": {
      "@id": "https://gemantria.ai/concept/decidedYes",
      "@type": "http://www.w3.org/2001/XMLSchema#boolean"
    }
  }
}
```

## Graph Structure

### Root Level Properties

- **`@context`**: Required. The JSON-LD context defining namespaces and terms
- **`@graph`**: Required. Array of all RDF resources (nodes and edges)

### Concept Node Schema

```json
{
  "@id": "https://gemantria.ai/concept/uuid-string",
  "@type": "https://gemantria.ai/concept/Concept",
  "label": "אלהים",
  "cluster": 1,
  "degree": 0.85,
  "betweenness": 0.12,
  "eigenvector": 0.95,
  "description": "Hebrew word for God or gods",
  "source": "genesis",
  "language": "he"
}
```

### Relation Edge Schema

```json
{
  "@id": "https://gemantria.ai/concept/edge/source-uuid-target-uuid",
  "@type": "https://gemantria.ai/concept/Relation",
  "relatedTo": [
    "https://gemantria.ai/concept/source-uuid",
    "https://gemantria.ai/concept/target-uuid"
  ],
  "cosine": 0.92,
  "rerankScore": 0.88,
  "decidedYes": true
}
```

## Property Definitions

### Required Properties

- **`@id`**: Unique IRI identifier for the resource
- **`@type`**: RDF type/class of the resource

### Concept Properties

- **`label`**: Human-readable name (string, required)
- **`cluster`**: Community/cluster assignment (integer, optional)
- **`degree`**: Degree centrality score (double, optional)
- **`betweenness`**: Betweenness centrality score (double, optional)
- **`eigenvector`**: Eigenvector centrality score (double, optional)

### Metadata Properties (Optional)

- **`description`**: Detailed description of the concept (string)
- **`source`**: Source text/document (string, e.g., "genesis", "exodus")
- **`language`**: ISO language code (string, default "he")

### Relation Properties

- **`relatedTo`**: Array of exactly 2 IRIs being related (required)
- **`cosine`**: Cosine similarity score (double, 0.0-1.0, required)
- **`rerankScore`**: Reranker confidence score (double, 0.0-1.0, optional)
- **`decidedYes`**: Whether reranker approved this relation (boolean, optional)

## Validation Rules

### Node Validation

1. `@id` must be valid IRI format: `https://gemantria.ai/concept/{uuid}`
2. `@type` must be `"https://gemantria.ai/concept/Concept"`
3. `label` is required and non-empty
4. `cluster` must be non-negative integer if present
5. Centrality scores must be non-negative doubles if present

### Edge Validation

1. `@id` must be valid IRI format: `https://gemantria.ai/concept/edge/{source-uuid}-{target-uuid}`
2. `@type` must be `"https://gemantria.ai/concept/Relation"`
3. `relatedTo` must contain exactly 2 valid concept IRIs
4. `cosine` must be between 0.0 and 1.0
5. `rerankScore` must be between 0.0 and 1.0 if present

## IRI Namespace Conventions

### Base Namespace

- **Prefix**: `https://gemantria.ai/concept/`
- **Purpose**: All concept network resources

### Concept IRIs

- **Format**: `https://gemantria.ai/concept/{uuid}`
- **Example**: `https://gemantria.ai/concept/123e4567-e89b-12d3-a456-426614174000`

### Relation IRIs

- **Format**: `https://gemantria.ai/concept/edge/{source-uuid}-{target-uuid}`
- **Note**: Source UUID comes first lexicographically

## Extensions and Future Compatibility

### Versioning

- **`@version`** in context indicates schema version
- Current version: 1.1 (supports language containers)

### Backwards Compatibility

- New optional properties can be added without breaking existing consumers
- Required properties cannot be removed or changed
- Context can be extended with new terms

### Custom Extensions

- Project-specific terms use `https://gemantria.ai/concept/` namespace
- Standard vocabularies preferred over custom terms
- Extensions must be documented here

## Implementation Notes

### Export Process

1. Query concept_network and concept_relations tables
2. Transform database rows to JSON-LD structure
3. Validate against this schema
4. Write to `exports/graph_latest.jsonld`

### Consumption Guidelines

1. Always process `@context` first
2. Validate `@id` and `@type` fields
3. Handle optional properties gracefully
4. Use standard JSON-LD processors for expansion/compaction

## Related Documentation

- **ADR-015**: JSON-LD & Visualization implementation details
- **RDF Ontology**: Turtle serialization schema (rdf-ontology.md)
- **WebUI Contract**: Frontend consumption specification (webui-contract.md)
