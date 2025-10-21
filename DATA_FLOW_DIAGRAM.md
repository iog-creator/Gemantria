# Gemantria Data Flow Architecture

## Complete Pipeline Overview

```mermaid
flowchart TD
    %% External Data Sources
    Bible[(Bible DB<br/>Read-Only<br/>KJV Text)]
    LMStudio[/LM Studio<br/>Qwen Models<br/>Live API/]
    
    %% Pipeline Stages
    Collect[📖 Collect Nouns<br/>Hebrew Extraction<br/>+ Deduplication]
    Validate[✅ Validate Batch<br/>Size Gates<br/>Quality Checks]
    Enrich[🤖 AI Enrichment<br/>Theological Insights<br/>Confidence Scores]
    Confidence[🎯 Confidence Validation<br/>AI + Gematria<br/>Quality Gates]
    Network[🕸️ Network Aggregation<br/>Embeddings + Relations<br/>Community Detection]
    
    %% Storage Layer
    Concepts[(concepts<br/>noun metadata)]
    Embeddings[(concept_network<br/>1024-dim vectors)]
    Relations[(concept_relations<br/>similarity edges)]
    Clusters[(concept_clusters<br/>communities)]
    Centrality[(concept_centrality<br/>node importance)]
    Metrics[(metrics_log<br/>performance data)]
    Health[(qwen_health_log<br/>model verification)]
    
    %% Output Generation
    Reports[📊 Report Generation<br/>Markdown + JSON<br/>Pipeline Analytics]
    GraphJSON[📈 Graph Export<br/>JSON for WebUI<br/>Force-directed viz]
    JSONLD[🔗 JSON-LD Export<br/>Semantic Web<br/>Knowledge Graphs]
    RDF[🗂️ RDF/Turtle Export<br/>Linked Data<br/>Ontology Standards]
    Stats[📈 Statistics Export<br/>Dashboard Metrics<br/>Health Indicators]
    
    %% Data Flow
    Bible --> Collect
    Collect --> Validate
    Validate --> Enrich
    LMStudio --> Enrich
    Enrich --> Confidence
    Confidence --> Network
    LMStudio --> Network
    
    Network --> Concepts
    Network --> Embeddings
    Network --> Relations
    Network --> Clusters
    Network --> Centrality
    
    Enrich --> Metrics
    Network --> Metrics
    LMStudio --> Health
    
    Relations --> Reports
    Metrics --> Reports
    Health --> Reports
    
    Concepts --> GraphJSON
    Relations --> GraphJSON
    Clusters --> GraphJSON
    Centrality --> GraphJSON
    
    GraphJSON --> JSONLD
    GraphJSON --> RDF
    
    Embeddings --> Stats
    Relations --> Stats
    Clusters --> Stats
    Centrality --> Stats
    
    %% Styling
    classDef input fill:#e1f5fe
    classDef process fill:#fff3e0
    classDef storage fill:#f3e5f5
    classDef output fill:#e8f5e8
    
    class Bible,LMStudio input
    class Collect,Validate,Enrich,Confidence,Network process
    class Concepts,Embeddings,Relations,Clusters,Centrality,Metrics,Health storage
    class Reports,GraphJSON,JSONLD,RDF,Stats output
```

## Key Data Transformations

### 1. Collection Stage
**Input**: Raw KJV Bible text  
**Process**: Hebrew noun extraction, deduplication, normalization  
**Output**: Structured noun objects with IDs and metadata

### 2. Validation Stage  
**Input**: Noun list with metadata  
**Process**: Batch size checks, quality gates, ALLOW_PARTIAL logic  
**Output**: Validated batch or detailed error manifest

### 3. Enrichment Stage
**Input**: Validated nouns  
**Process**: AI prompt engineering, LM Studio API calls, response parsing  
**Output**: Nouns with theological insights and confidence scores

### 4. Confidence Validation Stage
**Input**: AI-enriched nouns  
**Process**: Multi-gate validation (gematria ≥90%, AI ≥85% soft/95% hard)  
**Output**: Filtered noun list with validation evidence

### 5. Network Aggregation Stage
**Input**: Confidence-validated nouns  
**Process**: Embedding generation (1024-dim), KNN relations, community detection  
**Output**: Semantic network with relations, clusters, and centrality measures

## Storage Schema Overview

```mermaid
erDiagram
    concepts ||--o{ concept_network : "embeds into"
    concept_network ||--o{ concept_relations : "connects via"
    concept_relations ||--o{ concept_clusters : "groups into"
    concept_relations ||--o{ concept_centrality : "measures for"
    
    concepts {
        uuid id PK
        string name "noun name"
        string hebrew_text "original Hebrew"
        integer gematria_value "calculated value"
        string content_hash "SHA-256 identity"
    }
    
    concept_network {
        uuid id PK
        uuid concept_id FK
        vector embedding "1024-dim normalized"
        jsonb metadata "processing info"
    }
    
    concept_relations {
        uuid id PK
        uuid source_id FK
        uuid target_id FK
        float cosine "similarity score"
        float rerank_score "semantic relevance"
        boolean decided_yes "quality filter"
    }
    
    concept_clusters {
        uuid relation_id FK
        integer cluster_id "community ID"
        string algorithm "detection method"
    }
    
    concept_centrality {
        uuid relation_id FK
        float degree "connection count"
        float betweenness "bridge importance"
        float eigenvector "influence measure"
    }
```

## Quality Gates & Safety

### Pre-Processing
- ✅ **Qwen Live Gate**: All models verified before pipeline starts
- ✅ **Batch Size Gate**: ≥50 nouns unless ALLOW_PARTIAL=1 explicit
- ✅ **Hebrew Normalization**: NFKD→strip→NFC verified

### Processing
- ✅ **Confidence Gates**: AI soft≥85%, hard≥95%; Gematria≥90%
- ✅ **Embedding Quality**: 1024-dim vectors, L2 normalized
- ✅ **Relation Thresholds**: Strong≥0.90, weak≥0.75

### Post-Processing
- ✅ **Real Data Verification**: Reports contain actual metrics
- ✅ **Export Completeness**: All fields populated
- ✅ **Schema Compliance**: JSON-LD/RDF validation

## Performance Characteristics

| Stage | Throughput | Bottleneck |
|-------|------------|------------|
| Collection | ~1000 nouns/sec | Database queries |
| Enrichment | ~5 nouns/min | LM Studio API |
| Network | ~500 embeddings/sec | Vector operations |
| Validation | ~1000 items/sec | In-memory processing |

**Total Pipeline**: ~30-45 minutes for 1000 nouns (API-limited)

## Failure Recovery

- 🔄 **Transactional Safety**: All DB writes wrapped in transactions
- 🔄 **Checkpointer Resume**: Pipeline state survives restarts
- 🔄 **ALLOW_PARTIAL Override**: Processes incomplete batches when needed
- 🔄 **Node Isolation**: Individual failures don't stop entire pipeline

This architecture ensures **deterministic, resumable, observable** processing with **comprehensive quality gates** throughout the entire data pipeline.
