---
originating_ADR: ADR-015
canonical: true
version: 1.0
---

# SSOT: RDF Ontology for Concept Network

## Overview
This document defines the RDF ontology (vocabulary) for the Gematria concept network, providing the semantic foundation for RDF/Turtle exports. This serves as the single source of truth for RDF classes, properties, and relationships.

## Namespace Declarations

```turtle
@prefix gem: <https://gemantria.ai/concept/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix schema: <http://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

## Ontology Metadata

```turtle
gem: a owl:Ontology ;
  rdfs:label "Gematria Concept Network Ontology"@en ;
  rdfs:comment "Ontology for representing semantic relationships in Hebrew text analysis"@en ;
  owl:versionInfo "1.0" ;
  owl:imports schema: .
```

## Class Definitions

### Concept Class
```turtle
gem:Concept a owl:Class ;
  rdfs:label "Concept"@en ;
  rdfs:comment "A semantic concept extracted from Hebrew text analysis"@en ;
  rdfs:subClassOf schema:Thing .
```

### Relation Class
```turtle
gem:Relation a owl:Class ;
  rdfs:label "Relation"@en ;
  rdfs:comment "A semantic relationship between two concepts"@en ;
  rdfs:subClassOf schema:Thing .
```

## Property Definitions

### Core Properties

#### Label Property
```turtle
gem:label a owl:DatatypeProperty ;
  rdfs:label "label"@en ;
  rdfs:comment "Human-readable name of the concept"@en ;
  rdfs:domain gem:Concept ;
  rdfs:range xsd:string ;
  owl:equivalentProperty rdfs:label .
```

#### Cluster Property
```turtle
gem:cluster a owl:DatatypeProperty ;
  rdfs:label "cluster"@en ;
  rdfs:comment "Community/cluster assignment from graph analysis"@en ;
  rdfs:domain gem:Concept ;
  rdfs:range xsd:integer ;
  rdfs:subPropertyOf schema:category .
```

### Centrality Properties

#### Degree Centrality
```turtle
gem:degree a owl:DatatypeProperty ;
  rdfs:label "degree centrality"@en ;
  rdfs:comment "Degree centrality score (0.0-1.0)"@en ;
  rdfs:domain gem:Concept ;
  rdfs:range xsd:double .
```

#### Betweenness Centrality
```turtle
gem:betweenness a owl:DatatypeProperty ;
  rdfs:label "betweenness centrality"@en ;
  rdfs:comment "Betweenness centrality score"@en ;
  rdfs:domain gem:Concept ;
  rdfs:range xsd:double .
```

#### Eigenvector Centrality
```turtle
gem:eigenvector a owl:DatatypeProperty ;
  rdfs:label "eigenvector centrality"@en ;
  rdfs:comment "Eigenvector centrality score"@en ;
  rdfs:domain gem:Concept ;
  rdfs:range xsd:double .
```

### Relation Properties

#### Related To (Object Property)
```turtle
gem:relatedTo a owl:ObjectProperty ;
  rdfs:label "related to"@en ;
  rdfs:comment "Semantic relationship between concepts"@en ;
  rdfs:domain gem:Relation ;
  rdfs:range gem:Concept ;
  owl:equivalentProperty schema:relatedTo .
```

#### Cosine Similarity
```turtle
gem:cosine a owl:DatatypeProperty ;
  rdfs:label "cosine similarity"@en ;
  rdfs:comment "Cosine similarity score between concept embeddings (0.0-1.0)"@en ;
  rdfs:domain gem:Relation ;
  rdfs:range xsd:double ;
  rdfs:subPropertyOf schema:value .
```

#### Rerank Score
```turtle
gem:rerankScore a owl:DatatypeProperty ;
  rdfs:label "rerank score"@en ;
  rdfs:comment "Reranker confidence score for relation quality (0.0-1.0)"@en ;
  rdfs:domain gem:Relation ;
  rdfs:range xsd:double .
```

#### Decided Yes
```turtle
gem:decidedYes a owl:DatatypeProperty ;
  rdfs:label "decided yes"@en ;
  rdfs:comment "Whether the reranker approved this semantic relationship"@en ;
  rdfs:domain gem:Relation ;
  rdfs:range xsd:boolean .
```

## Example Instance Data

### Concept Instance
```turtle
gem:123e4567-e89b-12d3-a456-426614174000 a gem:Concept ;
  gem:label "אלהים" ;
  gem:cluster 1 ;
  gem:degree 0.85 ;
  gem:betweenness 0.12 ;
  gem:eigenvector 0.95 ;
  schema:description "Hebrew word for God or gods"@en ;
  schema:source "genesis" ;
  schema:inLanguage "he" .
```

### Relation Instance
```turtle
gem:edge/123e4567-e89b-12d3-a456-426614174000/987fcdeb-51a2-43d7-8f9e-123456789abc a gem:Relation ;
  gem:relatedTo gem:123e4567-e89b-12d3-a456-426614174000 ;
  gem:relatedTo gem:987fcdeb-51a2-43d7-8f9e-123456789abc ;
  gem:cosine 0.92 ;
  gem:rerankScore 0.88 ;
  gem:decidedYes true .
```

## Constraints and Validation

### Class Constraints
```turtle
# Concepts must have labels
gem:Concept owl:equivalentClass [
  a owl:Restriction ;
  owl:onProperty gem:label ;
  owl:cardinality "1"^^xsd:nonNegativeInteger
] .

# Relations must relate exactly two concepts
gem:Relation owl:equivalentClass [
  a owl:Restriction ;
  owl:onProperty gem:relatedTo ;
  owl:cardinality "2"^^xsd:nonNegativeInteger
] .
```

### Property Constraints
```turtle
# Cosine similarity range constraint
gem:cosine rdfs:range [
  a rdfs:Datatype ;
  owl:onDatatype xsd:double ;
  owl:withRestrictions (
    [ xsd:minInclusive "0.0"^^xsd:double ]
    [ xsd:maxInclusive "1.0"^^xsd:double ]
  )
] .

# Rerank score range constraint
gem:rerankScore rdfs:range [
  a rdfs:Datatype ;
  owl:onDatatype xsd:double ;
  owl:withRestrictions (
    [ xsd:minInclusive "0.0"^^xsd:double ]
    [ xsd:maxInclusive "1.0"^^xsd:double ]
  )
] .
```

## Reasoning and Inference Rules

### Transitivity Rules
```turtle
# Symmetric relations (if A related to B, then B related to A)
gem:relatedTo a owl:SymmetricProperty .

# Related concepts should be in same cluster (soft constraint)
# Note: This is a suggestion, not a hard rule
```

### Inference Capabilities
- **Symmetric Relations**: If concept A is related to concept B, then concept B is related to concept A
- **Transitive Clustering**: Concepts in same cluster may be transitively related
- **Centrality Propagation**: High-centrality concepts influence related concepts

## Extensions and Evolution

### Versioning Strategy
- Ontology versions follow semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes increment MAJOR version
- New properties increment MINOR version
- Bug fixes increment PATCH version

### Extension Points
- **Domain-specific vocabularies**: Can import additional ontologies
- **Property extensions**: New relation types can extend gem:Relation
- **Class hierarchies**: Subclasses can be defined for specific concept types

### Deprecation Policy
- Deprecated terms marked with `owl:deprecated true`
- Deprecated terms maintained for backwards compatibility
- Migration guides provided for major version changes

## Implementation Guidelines

### Export Process
1. Query database for concepts and relations
2. Generate RDF triples according to this ontology
3. Serialize as Turtle format
4. Validate against ontology constraints
5. Write to `exports/graph_latest.ttl`

### Consumption Guidelines
1. Import this ontology namespace
2. Use OWL reasoners for inference
3. Validate instances against class/property constraints
4. Handle deprecated terms gracefully

## Tooling Support

### Validation Tools
- **RDF Validators**: Check syntax and schema compliance
- **OWL Reasoners**: Perform logical inference and consistency checking
- **SPARQL Engines**: Query and analyze the knowledge graph

### Conversion Tools
- **JSON-LD to RDF**: Convert between serialization formats
- **Ontology Editors**: Protégé, TopBraid Composer for ontology development
- **Triple Stores**: Blazegraph, Jena for storage and querying

## Related Documentation

- **ADR-015**: JSON-LD & Visualization implementation details
- **JSON-LD Schema**: JSON-LD serialization specification (jsonld-schema.md)
- **WebUI Contract**: Frontend consumption specification (webui-contract.md)
- **Graph Stats API**: Statistics export format (graph-stats-api.md)
