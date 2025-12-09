# Gemantria DB Schema (Phase-1, v6.2.3)

- **Schema**: `gematria`

- **Tables**:

  - `concepts(concept_id PK, name, hebrew_text, gematria_value, strong_number, primary_verse, book, chapter, freq, content_hash UNIQUE, created_at, updated_at)`

  - `concept_relations(relation_id PK, src_concept_id → concepts, dst_concept_id → concepts, relation_type, weight, evidence, created_at)`

  - `concept_centrality(concept_id PK → concepts, degree, betweenness, closeness, eigenvector, metrics_at)`

  - `concept_network(id PK, concept_id → concepts, embedding VECTOR(1024), created_at)`

  - `concept_clusters(concept_id PK → concepts, cluster_id, cluster_center, confidence, created_at)`

### Roles / DSNs

- `BIBLE_DSN` (read-only upstream; enforced in app layer), `GEMATRIA_DSN` (RW target for pipeline + exports).

### Migration Strategy

- **Sequential**: Migrations run in numerical order (001_schema.sql, 002_indexes.sql, then 003+)
- **Idempotent**: Safe to run multiple times
- **Transactional**: Each migration wrapped in BEGIN/COMMIT

### Existing Migrations

- **001_schema.sql**: Base tables and schema creation
- **002_indexes.sql**: Performance indexes and constraints
- **003_metrics_logging.sql**: Metrics storage and indexing
- **004_metrics_views.sql**: Observability views and aggregations
- **005_ai_metadata.sql**: LLM metadata storage
- **006_confidence_validation.sql**: Confidence validation structures
- **007_concept_network.sql**: Vector embeddings storage
- **008_add_concept_network_constraints.sql**: Network constraints
- **009_rerank_evidence.sql**: Reranking evidence storage
- **010_qwen_health_log.sql**: Model health tracking
- **011_concept_network_verification.sql**: Network verification views
- **012a_concept_network_dim_fix.sql**: Dimension corrections
- **013_fix_ai_enrichment_schema.sql**: AI enrichment fixes
- **014_relations_and_patterns.sql**: Relations and patterns
- **015_graph_metadata.sql**: Graph metadata storage
- **016_metrics.sql**: Metrics aggregation
- **037_create_concepts.sql**: Concepts table creation (legacy)
- **038_concept_correlations.sql**: Correlation analysis views
