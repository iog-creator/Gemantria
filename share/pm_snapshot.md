# pm_snapshot

**Generated**: 2025-12-07T19:20:06.318263+00:00
**Source**: `pm_snapshot.json`

---

- **overall_ok**: `true`
- **generated_at**: `2025-12-07T11:19:54-08:00`
- **db_health**:
  - **ok**: `true`
  - **mode**: `ready`
  - **checks**:
    - **driver_available**: `true`
    - **connection_ok**: `true`
    - **graph_stats_ready**: `true`
  - **details**:
    - **errors**:
- **system_health**:
  - **ok**: `true`
  - **db**:
    - **ok**: `true`
    - **mode**: `ready`
    - **checks**:
      - **driver_available**: `true`
      - **connection_ok**: `true`
      - **graph_stats_ready**: `true`
    - **details**:
      - **errors**:
  - **lm**:
    - **ok**: `true`
    - **mode**: `lm_ready`
    - **details**:
      - **endpoint**: `http://127.0.0.1:9994/v1`
      - **provider**: `lmstudio`
      - **errors**:
  - **graph**:
    - **ok**: `true`
    - **mode**: `db_on`
    - **stats**:
      - **nodes**: `null`
      - **edges**: `null`
      - **avg_degree**: `null`
      - **snapshot_count**: `null`
      - **last_import_at**: `null`
    - **reason**: `no snapshots found`
  - **system**:
    - **ok**: `true`
    - **components**:
      - **db**:
        - **ok**: `true`
        - **mode**: `ready`
        - **checks**:
          - **driver_available**: `true`
          - **connection_ok**: `true`
          - **graph_stats_ready**: `true`
        - **details**:
          - **errors**:
      - **lm**:
        - **ok**: `true`
        - **mode**: `lm_ready`
        - **details**:
          - **endpoint**: `http://127.0.0.1:9994/v1`
          - **provider**: `lmstudio`
          - **errors**:
      - **graph**:
        - **ok**: `true`
        - **mode**: `db_on`
        - **stats**:
          - **nodes**: `null`
          - **edges**: `null`
          - **avg_degree**: `null`
          - **snapshot_count**: `null`
          - **last_import_at**: `null`
        - **reason**: `no snapshots found`
- **status_explain**:
  - **level**: `OK`
  - **headline**: `All systems nominal`
  - **details**: `Database is ready and all checks passed. All 4 LM slot(s) are operational.`
  - **documentation**:
    - **available**: `true`
    - **total**: `1185`
    - **by_subsystem**:
      - **ops**: `555`
      - **gematria**: `38`
      - **pm**: `227`
      - **general**: `227`
      - **docs**: `5`
      - **root**: `48`
      - **webui**: `51`
      - **biblescholar**: `34`
    - **by_type**:
      - **other**: `1023`
      - **ssot**: `129`
      - **runbook**: `33`
    - **hints**:
      1. Item:
        - **level**: `WARN`
        - **code**: `KB_MISSING_DOCS`
        - **message**: `KB registry references 316 missing file(s)`
        - **missing_count**: `316`
        - **missing_files**:
          1. `agentpm/adapters/AGENTS.md (ID`
          2. `agentpm/AGENTS.md (ID`
          3. `agentpm/ai_docs/AGENTS.md (ID`
          4. `agentpm/atlas/AGENTS.md (ID`
          5. `agentpm/biblescholar/AGENTS.md (ID`
          6. `agentpm/biblescholar/tests/AGENTS.md (ID`
          7. `agentpm/bus/AGENTS.md (ID`
          8. `agentpm/control_plane/AGENTS.md (ID`
          9. `agentpm/control_widgets/AGENTS.md (ID`
          10. `agentpm/db/AGENTS.md (ID`
      2. Item:
        - **level**: `WARN`
        - **code**: `KB_VALIDATION_ISSUES`
        - **message**: `KB registry validation issue: Registry validation failed: 318 errors`
      3. Item:
        - **level**: `WARN`
        - **code**: `KB_VALIDATION_ISSUES`
        - **message**: `KB registry validation issue: Registry has 3 warnings`
      4. Item:
        - **level**: `WARN`
        - **code**: `KB_DOC_STALE`
        - **message**: `9 document(s) are stale (exceed refresh interval)`
        - **stale_count**: `9`
        - **stale_docs**:
          1. Item:
            - **id**: `ssot::docs/ssot/data-flow-visual.md`
            - **path**: `docs/SSOT/data_flow_visual.md`
            - **title**: `SSOT::docs/SSOT/data_flow_visual.md`
          2. Item:
            - **id**: `ssot::docs/ssot/epoch-ledger.md`
            - **path**: `docs/SSOT/EPOCH_LEDGER.md`
            - **title**: `SSOT::docs/SSOT/EPOCH_LEDGER.md`
          3. Item:
            - **id**: `ssot::docs/ssot/graph-metrics-api.md`
            - **path**: `docs/SSOT/graph-metrics-api.md`
            - **title**: `SSOT::docs/SSOT/graph-metrics-api.md`
          4. Item:
            - **id**: `ssot::docs/ssot/graph-stats-api.md`
            - **path**: `docs/SSOT/graph-stats-api.md`
            - **title**: `SSOT::docs/SSOT/graph-stats-api.md`
          5. Item:
            - **id**: `ssot::docs/ssot/jsonld-schema.md`
            - **path**: `docs/SSOT/jsonld-schema.md`
            - **title**: `SSOT::docs/SSOT/jsonld-schema.md`
    - **key_docs**:
      1. Item:
        - **id**: `master-plan`
        - **title**: `MASTER_PLAN`
        - **path**: `MASTER_PLAN.md`
        - **type**: `ssot`
      2. Item:
        - **id**: `rules-index`
        - **title**: `RULES_INDEX`
        - **path**: `RULES_INDEX.md`
        - **type**: `ssot`
      3. Item:
        - **id**: `ssot::docs/ssot/agentpm-gematria-module-plan.md`
        - **title**: `SSOT::docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md`
        - **path**: `docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md`
        - **type**: `ssot`
    - **freshness**:
      - **total**: `1185`
      - **stale_count**: `9`
      - **missing_count**: `316`
      - **out_of_sync_count**: `0`
      - **fresh_count**: `860`
- **reality_check**:
  - **command**: `reality.check`
  - **mode**: `HINT`
  - **timestamp**: `2025-12-07T19:19:54.191432+00:00`
  - **env**:
    - **ok**: `true`
    - **dsn_ok**: `true`
    - **details**:
      - **dsns**:
        - **rw**: `true`
        - **ro**: `true`
        - **bible**: `true`
  - **db**:
    - **ok**: `true`
    - **control_schema**: `control`
    - **tables_expected**: `0`
    - **tables_present**: `0`
    - **generated_at**: `2025-12-07T19:19:54.191450+00:00`
    - **components**:
      - **status**:
        - **ok**: `true`
        - **mode**: `ready`
        - **reason**: `null`
        - **tables**:
          - **public.ai_interactions**:
            - **present**: `true`
            - **row_count**: `1`
            - **latest_created_at**: `2025-11-07T11:11:49.732991-08:00`
          - **public.governance_artifacts**:
            - **present**: `true`
            - **row_count**: `134`
            - **latest_created_at**: `2025-12-07T09:56:28.527430-08:00`
          - **control.agent_run**:
            - **present**: `true`
            - **row_count**: `2270`
            - **latest_created_at**: `2025-11-30T09:02:28.655100-08:00`
          - **control.agent_run_cli**:
            - **present**: `true`
            - **row_count**: `140`
            - **latest_created_at**: `2025-12-07T10:48:59.960977-08:00`
          - **control.kb_document**:
            - **present**: `true`
            - **row_count**: `4238`
            - **latest_created_at**: `2025-11-27T10:39:03.026669-08:00`
          - **control.doc_registry**:
            - **present**: `true`
            - **row_count**: `1203`
            - **latest_created_at**: `2025-12-07T10:46:19.978008-08:00`
          - **control.doc_version**:
            - **present**: `true`
            - **row_count**: `8808`
            - **latest_created_at**: `null`
          - **control.tool_catalog**:
            - **present**: `true`
            - **row_count**: `7`
            - **latest_created_at**: `2025-11-26T09:05:34.616631-08:00`
          - **gematria.graph_stats_snapshots**:
            - **present**: `true`
            - **row_count**: `0`
            - **latest_created_at**: `null`
      - **tables**:
        - **ok**: `true`
        - **mode**: `db_on`
        - **error**: `null`
        - **tables**:
          - **control.agent_run**: `2270`
          - **control.agent_run_cli**: `140`
          - **control.capability_rule**: `5`
          - **control.capability_session**: `5`
          - **control.doc_embedding**: `245898`
          - **control.doc_fragment**: `245903`
          - **control.doc_registry**: `1203`
          - **control.doc_sync_state**: `0`
          - **control.doc_version**: `8808`
          - **control.guard_definition**: `0`
          - **control.hint_registry**: `25`
          - **control.kb_document**: `4238`
          - **control.rule_definition**: `69`
          - **control.rule_source**: `138`
          - **control.system_state_ledger**: `462`
          - **control.tool_catalog**: `7`
          - **gematria.ai_embeddings**: `1`
          - **gematria.checkpoints**: `4`
          - **gematria.concept_centrality**: `0`
          - **gematria.concept_relations**: `0`
          - **gematria.concepts**: `0`
          - **gematria.edges**: `1`
          - **gematria.enrichment_crossrefs**: `0`
          - **gematria.graph_stats_snapshots**: `0`
          - **gematria.nodes**: `2`
          - **gematria.nouns**: `0`
          - **gematria.runs**: `2`
          - **gematria.runs_ledger**: `115`
          - **gematria.schema_migrations**: `2`
          - **gematria.word_cache**: `0`
          - **mcp.endpoints**: `10`
          - **mcp.logs**: `0`
          - **mcp.tools**: `6`
          - **ops.job_queue**: `0`
          - **public.ai_enrichment_log**: `13857`
          - **public.ai_interactions**: `1`
          - **public.ai_performance_insights**: `0`
          - **public.books**: `35`
          - **public.checkpointer_state**: `64`
          - **public.checkpointer_writes**: `2`
          - **public.checkpoints**: `22`
          - **public.cluster_metrics**: `0`
          - **public.code_generation_events**: `0`
          - **public.code_generation_patterns**: `0`
          - **public.concept_centrality**: `0`
          - **public.concept_clusters**: `1`
          - **public.concept_metadata**: `4399`
          - **public.concept_metrics**: `0`
          - **public.concept_network**: `4399`
          - **public.concept_relations**: `14330`
          - **public.concept_rerank_cache**: `0`
          - **public.concepts**: `4399`
          - **public.confidence_validation_log**: `35`
          - **public.connections**: `0`
          - **public.context_awareness_events**: `0`
          - **public.context_success_patterns**: `0`
          - **public.cross_references**: `0`
          - **public.doctrinal_links**: `0`
          - **public.document_access_log**: `1`
          - **public.document_sections**: `398`
          - **public.governance_artifacts**: `134`
          - **public.governance_compliance_log**: `243`
          - **public.hint_emissions**: `818`
          - **public.hypotheses**: `0`
          - **public.integration_log**: `0`
          - **public.isolation_patterns**: `0`
          - **public.learning_events**: `2`
          - **public.metrics_log**: `7969`
          - **public.model_performance_metrics**: `0`
          - **public.network_metrics**: `0`
          - **public.pattern_occurrences**: `9`
          - **public.patterns**: `9`
          - **public.prime_factors**: `0`
          - **public.qwen_health_log**: `15`
          - **public.runs**: `25`
          - **public.satisfaction_metrics**: `0`
          - **public.share_manifest_items**: `40`
          - **public.share_manifest_metadata**: `1`
          - **public.tool_usage_analytics**: `0`
          - **public.twin_patterns**: `0`
          - **public.user_feedback**: `0`
          - **public.verse_noun_occurrences**: `116960`
          - **staging.concept_metadata_norm**: `0`
          - **staging.concept_relations_norm**: `1855`
          - **staging.concepts_norm**: `710`
          - **telemetry.ai_interactions**: `0`
          - **telemetry.checkpointer_state**: `0`
          - **telemetry.metrics_log**: `0`
      - **schema**:
        - **ok**: `true`
        - **mode**: `db_on`
        - **reason**: `null`
        - **tables**:
          - **control.agent_run**:
            - **columns**:
              1. Item:
                - **name**: `id`
                - **data_type**: `uuid`
                - **is_nullable**: `false`
                - **default**: `gen_random_uuid()`
              2. Item:
                - **name**: `project_id`
                - **data_type**: `bigint`
                - **is_nullable**: `false`
                - **default**: `null`
              3. Item:
                - **name**: `session_id`
                - **data_type**: `uuid`
                - **is_nullable**: `true`
                - **default**: `null`
              4. Item:
                - **name**: `tool`
                - **data_type**: `text`
                - **is_nullable**: `false`
                - **default**: `null`
              5. Item:
                - **name**: `args_json`
                - **data_type**: `jsonb`
                - **is_nullable**: `false`
                - **default**: `null`
              6. Item:
                - **name**: `result_json`
                - **data_type**: `jsonb`
                - **is_nullable**: `false`
                - **default**: `null`
              7. Item:
                - **name**: `violations_json`
                - **data_type**: `jsonb`
                - **is_nullable**: `false`
                - **default**: `'[]'::jsonb`
              8. Item:
                - **name**: `created_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `false`
                - **default**: `now()`
            - **primary_key**:
              1. `id`
            - **indexes**:
              1. Item:
                - **name**: `idx_agent_run_created`
                - **columns**:
                  1. `created_at`
                - **unique**: `false`
              2. Item:
                - **name**: `idx_agent_run_project`
                - **columns**:
                  1. `project_id`
                - **unique**: `false`
              3. Item:
                - **name**: `idx_agent_run_session`
                - **columns**:
                  1. `session_id`
                - **unique**: `false`
              4. Item:
                - **name**: `idx_agent_run_tool`
                - **columns**:
                  1. `tool`
                - **unique**: `false`
              5. Item:
                - **name**: `idx_agent_run_violations`
                - **columns**:
                  1. `violations_json`
                - **unique**: `false`
          - **control.tool_catalog**:
            - **columns**:
              1. Item:
                - **name**: `id`
                - **data_type**: `uuid`
                - **is_nullable**: `false`
                - **default**: `gen_random_uuid()`
              2. Item:
                - **name**: `project_id`
                - **data_type**: `bigint`
                - **is_nullable**: `false`
                - **default**: `null`
              3. Item:
                - **name**: `name`
                - **data_type**: `text`
                - **is_nullable**: `false`
                - **default**: `null`
              4. Item:
                - **name**: `ring`
                - **data_type**: `integer`
                - **is_nullable**: `false`
                - **default**: `null`
              5. Item:
                - **name**: `io_schema`
                - **data_type**: `jsonb`
                - **is_nullable**: `false`
                - **default**: `null`
              6. Item:
                - **name**: `enabled`
                - **data_type**: `boolean`
                - **is_nullable**: `false`
                - **default**: `true`
              7. Item:
                - **name**: `created_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `false`
                - **default**: `now()`
            - **primary_key**:
              1. `id`
            - **indexes**:
              1. Item:
                - **name**: `idx_tool_catalog_enabled`
                - **columns**:
                  1. `enabled`
                - **unique**: `false`
              2. Item:
                - **name**: `idx_tool_catalog_project`
                - **columns**:
                  1. `project_id`
                - **unique**: `false`
              3. Item:
                - **name**: `idx_tool_catalog_ring`
                - **columns**:
                  1. `ring`
                - **unique**: `false`
              4. Item:
                - **name**: `tool_catalog_project_id_name_key`
                - **columns**:
                  1. `project_id`
                  2. `name`
                - **unique**: `true`
          - **control.capability_rule**:
            - **columns**:
              1. Item:
                - **name**: `id`
                - **data_type**: `uuid`
                - **is_nullable**: `false`
                - **default**: `gen_random_uuid()`
              2. Item:
                - **name**: `project_id`
                - **data_type**: `bigint`
                - **is_nullable**: `false`
                - **default**: `null`
              3. Item:
                - **name**: `name`
                - **data_type**: `text`
                - **is_nullable**: `false`
                - **default**: `null`
              4. Item:
                - **name**: `ring`
                - **data_type**: `integer`
                - **is_nullable**: `false`
                - **default**: `null`
              5. Item:
                - **name**: `allowlist`
                - **data_type**: `ARRAY`
                - **is_nullable**: `true`
                - **default**: `null`
              6. Item:
                - **name**: `denylist`
                - **data_type**: `ARRAY`
                - **is_nullable**: `true`
                - **default**: `null`
              7. Item:
                - **name**: `budgets`
                - **data_type**: `jsonb`
                - **is_nullable**: `false`
                - **default**: `'{}'::jsonb`
              8. Item:
                - **name**: `created_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `false`
                - **default**: `now()`
            - **primary_key**:
              1. `id`
            - **indexes**:
              1. Item:
                - **name**: `capability_rule_project_id_name_key`
                - **columns**:
                  1. `project_id`
                  2. `name`
                - **unique**: `true`
              2. Item:
                - **name**: `idx_capability_rule_project`
                - **columns**:
                  1. `project_id`
                - **unique**: `false`
              3. Item:
                - **name**: `idx_capability_rule_ring`
                - **columns**:
                  1. `ring`
                - **unique**: `false`
          - **control.doc_fragment**:
            - **columns**:
              1. Item:
                - **name**: `id`
                - **data_type**: `uuid`
                - **is_nullable**: `false`
                - **default**: `gen_random_uuid()`
              2. Item:
                - **name**: `project_id`
                - **data_type**: `bigint`
                - **is_nullable**: `true`
                - **default**: `null`
              3. Item:
                - **name**: `src`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              4. Item:
                - **name**: `anchor`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              5. Item:
                - **name**: `sha256`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              6. Item:
                - **name**: `created_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `false`
                - **default**: `now()`
              7. Item:
                - **name**: `doc_id`
                - **data_type**: `uuid`
                - **is_nullable**: `true`
                - **default**: `null`
              8. Item:
                - **name**: `version_id`
                - **data_type**: `bigint`
                - **is_nullable**: `true`
                - **default**: `null`
              9. Item:
                - **name**: `fragment_index`
                - **data_type**: `integer`
                - **is_nullable**: `true`
                - **default**: `null`
              10. Item:
                - **name**: `fragment_type`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              11. Item:
                - **name**: `content`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              12. Item:
                - **name**: `updated_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `true`
                - **default**: `now()`
              13. Item:
                - **name**: `meta`
                - **data_type**: `jsonb`
                - **is_nullable**: `true`
                - **default**: `'{}'::jsonb`
              14. Item:
                - **name**: `content_tsvector`
                - **data_type**: `tsvector`
                - **is_nullable**: `true`
                - **default**: `null`
            - **primary_key**:
              1. `id`
            - **indexes**:
              1. Item:
                - **name**: `doc_fragment_project_id_src_anchor_key`
                - **columns**:
                  1. `project_id`
                  2. `src`
                  3. `anchor`
                - **unique**: `true`
              2. Item:
                - **name**: `idx_doc_fragment_content_tsvector`
                - **columns**:
                  1. `content_tsvector`
                - **unique**: `false`
              3. Item:
                - **name**: `idx_doc_fragment_content_unique`
                - **columns**:
                  1. `doc_id`
                  2. `version_id`
                  3. `fragment_index`
                - **unique**: `true`
              4. Item:
                - **name**: `idx_doc_fragment_doc_id`
                - **columns**:
                  1. `doc_id`
                - **unique**: `false`
              5. Item:
                - **name**: `idx_doc_fragment_meta`
                - **columns**:
                  1. `meta`
                - **unique**: `false`
              6. Item:
                - **name**: `idx_doc_fragment_project`
                - **columns**:
                  1. `project_id`
                - **unique**: `false`
              7. Item:
                - **name**: `idx_doc_fragment_sha256`
                - **columns**:
                  1. `sha256`
                - **unique**: `false`
              8. Item:
                - **name**: `idx_doc_fragment_src`
                - **columns**:
                  1. `src`
                - **unique**: `false`
              9. Item:
                - **name**: `idx_doc_fragment_type`
                - **columns**:
                  1. `fragment_type`
                - **unique**: `false`
              10. Item:
                - **name**: `idx_doc_fragment_version_id`
                - **columns**:
                  1. `version_id`
                - **unique**: `false`
          - **control.capability_session**:
            - **columns**:
              1. Item:
                - **name**: `id`
                - **data_type**: `uuid`
                - **is_nullable**: `false`
                - **default**: `gen_random_uuid()`
              2. Item:
                - **name**: `project_id`
                - **data_type**: `bigint`
                - **is_nullable**: `false`
                - **default**: `null`
              3. Item:
                - **name**: `rule_id`
                - **data_type**: `uuid`
                - **is_nullable**: `false`
                - **default**: `null`
              4. Item:
                - **name**: `por_json`
                - **data_type**: `jsonb`
                - **is_nullable**: `false`
                - **default**: `null`
              5. Item:
                - **name**: `tiny_menu`
                - **data_type**: `ARRAY`
                - **is_nullable**: `false`
                - **default**: `null`
              6. Item:
                - **name**: `ttl_s`
                - **data_type**: `integer`
                - **is_nullable**: `false`
                - **default**: `null`
              7. Item:
                - **name**: `created_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `false`
                - **default**: `now()`
            - **primary_key**:
              1. `id`
            - **indexes**:
              1. Item:
                - **name**: `idx_capability_session_created`
                - **columns**:
                  1. `created_at`
                - **unique**: `false`
              2. Item:
                - **name**: `idx_capability_session_project`
                - **columns**:
                  1. `project_id`
                - **unique**: `false`
              3. Item:
                - **name**: `idx_capability_session_rule`
                - **columns**:
                  1. `rule_id`
                - **unique**: `false`
          - **public.ai_interactions**:
            - **columns**:
              1. Item:
                - **name**: `id`
                - **data_type**: `integer`
                - **is_nullable**: `false`
                - **default**: `nextval('ai_interactions_id_seq'::regclass)`
              2. Item:
                - **name**: `session_id`
                - **data_type**: `character varying`
                - **is_nullable**: `false`
                - **default**: `null`
              3. Item:
                - **name**: `interaction_type`
                - **data_type**: `character varying`
                - **is_nullable**: `false`
                - **default**: `null`
              4. Item:
                - **name**: `user_query`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              5. Item:
                - **name**: `ai_response`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              6. Item:
                - **name**: `tools_used`
                - **data_type**: `ARRAY`
                - **is_nullable**: `true`
                - **default**: `null`
              7. Item:
                - **name**: `context_provided`
                - **data_type**: `jsonb`
                - **is_nullable**: `true`
                - **default**: `null`
              8. Item:
                - **name**: `execution_time_ms`
                - **data_type**: `integer`
                - **is_nullable**: `true`
                - **default**: `null`
              9. Item:
                - **name**: `success`
                - **data_type**: `boolean`
                - **is_nullable**: `true`
                - **default**: `true`
              10. Item:
                - **name**: `error_details`
                - **data_type**: `text`
                - **is_nullable**: `true`
                - **default**: `null`
              11. Item:
                - **name**: `created_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `true`
                - **default**: `now()`
            - **primary_key**:
              1. `id`
            - **indexes**:
              1. Item:
                - **name**: `idx_ai_interactions_created`
                - **columns**:
                  1. `created_at`
                - **unique**: `false`
              2. Item:
                - **name**: `idx_ai_interactions_session`
                - **columns**:
                  1. `session_id`
                - **unique**: `false`
              3. Item:
                - **name**: `idx_ai_interactions_type`
                - **columns**:
                  1. `interaction_type`
                - **unique**: `false`
          - **public.governance_artifacts**:
            - **columns**:
              1. Item:
                - **name**: `id`
                - **data_type**: `integer`
                - **is_nullable**: `false`
                - **default**: `nextval('governance_artifacts_id_seq'::regclass)`
              2. Item:
                - **name**: `artifact_type`
                - **data_type**: `character varying`
                - **is_nullable**: `false`
                - **default**: `null`
              3. Item:
                - **name**: `artifact_name`
                - **data_type**: `character varying`
                - **is_nullable**: `false`
                - **default**: `null`
              4. Item:
                - **name**: `file_path`
                - **data_type**: `character varying`
                - **is_nullable**: `true`
                - **default**: `null`
              5. Item:
                - **name**: `rule_references`
                - **data_type**: `ARRAY`
                - **is_nullable**: `true`
                - **default**: `null`
              6. Item:
                - **name**: `agent_references`
                - **data_type**: `ARRAY`
                - **is_nullable**: `true`
                - **default**: `null`
              7. Item:
                - **name**: `last_updated`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `true`
                - **default**: `now()`
              8. Item:
                - **name**: `checksum`
                - **data_type**: `character varying`
                - **is_nullable**: `true`
                - **default**: `null`
              9. Item:
                - **name**: `validation_status`
                - **data_type**: `character varying`
                - **is_nullable**: `true`
                - **default**: `'pending'::character varying`
              10. Item:
                - **name**: `created_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `true`
                - **default**: `now()`
              11. Item:
                - **name**: `updated_at`
                - **data_type**: `timestamp with time zone`
                - **is_nullable**: `true`
                - **default**: `now()`
            - **primary_key**:
              1. `id`
            - **indexes**:
              1. Item:
                - **name**: `governance_artifacts_artifact_type_artifact_name_key`
                - **columns**:
                  1. `artifact_type`
                  2. `artifact_name`
                - **unique**: `true`
              2. Item:
                - **name**: `idx_governance_agent_refs`
                - **columns**:
                  1. `agent_references`
                - **unique**: `false`
              3. Item:
                - **name**: `idx_governance_rule_refs`
                - **columns**:
                  1. `rule_references`
                - **unique**: `false`
              4. Item:
                - **name**: `idx_governance_type`
                - **columns**:
                  1. `artifact_type`
                - **unique**: `false`
      - **pipeline_status**:
        - **ok**: `true`
        - **mode**: `db_on`
        - **reason**: `null`
        - **window_hours**: `24`
        - **summary**:
          - **total_runs**: `0`
          - **pipelines**:
  - **lm**:
    - **ok**: `true`
    - **provider**: `unknown`
    - **slots**:
      1. Item:
        - **slot**: `local_agent`
        - **provider**: `lmstudio`
        - **model**: `ibm/granite-4-h-tiny`
        - **service_status**: `OK`
      2. Item:
        - **slot**: `embedding`
        - **provider**: `lmstudio`
        - **model**: `text-embedding-bge-m3`
        - **service_status**: `OK`
      3. Item:
        - **slot**: `reranker`
        - **provider**: `lmstudio`
        - **model**: `ibm/granite-4-h-tiny (embedding_only)`
        - **service_status**: `OK`
      4. Item:
        - **slot**: `theology`
        - **provider**: `lmstudio`
        - **model**: `christian-bible-expert-v2.0-12b`
        - **service_status**: `OK`
    - **mode**: `lm_ready`
    - **details**:
      - **endpoint**: `http://127.0.0.1:9994/v1`
      - **provider**: `lmstudio`
      - **errors**:
  - **exports**:
    - **ok**: `true`
    - **lm_indicator**:
      - **status**: `unknown`
      - **lm_available**: `true`
      - **note**: `Recreated after share/ disaster; regenerate from LM health scripts when available.`
    - **compliance_head**: `null`
    - **kb_docs_head**: `null`
    - **mcp_catalog**: `null`
  - **eval_smoke**:
    - **ok**: `true`
    - **targets**:
      1. `ci.exports.smoke`
      2. `eval.graph.calibrate.adv`
    - **messages**:
      1. `ci.exports.smoke: OK`
      2. `eval.graph.calibrate.adv: OK`
  - **hints**:
    1. `DMS-REQUIRED: reality.green STRICT must pass all required checks before declaring system ready.`
    2. `KB: KB registry references 316 missing file(s)`
    3. `KB: KB registry validation issue: Registry validation failed: 318 errors`
    4. `KB: KB registry validation issue: Registry has 3 warnings`
    5. `KB: 9 document(s) are stale (exceed refresh interval)`
    6. `KB: Doc freshness: 9 stale, 0 out-of-sync`
  - **kb_hints**:
    1. Item:
      - **level**: `WARN`
      - **code**: `KB_MISSING_DOCS`
      - **message**: `KB registry references 316 missing file(s)`
      - **missing_count**: `316`
      - **missing_files**:
        1. `agentpm/adapters/AGENTS.md (ID`
        2. `agentpm/AGENTS.md (ID`
        3. `agentpm/ai_docs/AGENTS.md (ID`
        4. `agentpm/atlas/AGENTS.md (ID`
        5. `agentpm/biblescholar/AGENTS.md (ID`
        6. `agentpm/biblescholar/tests/AGENTS.md (ID`
        7. `agentpm/bus/AGENTS.md (ID`
        8. `agentpm/control_plane/AGENTS.md (ID`
        9. `agentpm/control_widgets/AGENTS.md (ID`
        10. `agentpm/db/AGENTS.md (ID`
    2. Item:
      - **level**: `WARN`
      - **code**: `KB_VALIDATION_ISSUES`
      - **message**: `KB registry validation issue: Registry validation failed: 318 errors`
    3. Item:
      - **level**: `WARN`
      - **code**: `KB_VALIDATION_ISSUES`
      - **message**: `KB registry validation issue: Registry has 3 warnings`
    4. Item:
      - **level**: `WARN`
      - **code**: `KB_DOC_STALE`
      - **message**: `9 document(s) are stale (exceed refresh interval)`
      - **stale_count**: `9`
      - **stale_docs**:
        1. Item:
          - **id**: `ssot::docs/ssot/data-flow-visual.md`
          - **path**: `docs/SSOT/data_flow_visual.md`
          - **title**: `SSOT::docs/SSOT/data_flow_visual.md`
        2. Item:
          - **id**: `ssot::docs/ssot/epoch-ledger.md`
          - **path**: `docs/SSOT/EPOCH_LEDGER.md`
          - **title**: `SSOT::docs/SSOT/EPOCH_LEDGER.md`
        3. Item:
          - **id**: `ssot::docs/ssot/graph-metrics-api.md`
          - **path**: `docs/SSOT/graph-metrics-api.md`
          - **title**: `SSOT::docs/SSOT/graph-metrics-api.md`
        4. Item:
          - **id**: `ssot::docs/ssot/graph-stats-api.md`
          - **path**: `docs/SSOT/graph-stats-api.md`
          - **title**: `SSOT::docs/SSOT/graph-stats-api.md`
        5. Item:
          - **id**: `ssot::docs/ssot/jsonld-schema.md`
          - **path**: `docs/SSOT/jsonld-schema.md`
          - **title**: `SSOT::docs/SSOT/jsonld-schema.md`
  - **overall_ok**: `true`
  - **required_hints**:
    1. Item:
      - **logical_name**: `reality.green.required_checks`
      - **injection_mode**: `PRE_PROMPT`
      - **payload**:
        - **text**: `reality.green STRICT must pass all required checks before declaring system ready.`
        - **commands**:
          1. `make reality.green STRICT`
        - **metadata**:
          - **source**: `Rule-050`
          - **section**: `5`
        - **constraints**:
          - **rule_ref**: `050`
          - **required_before**: `PR`
      - **priority**: `10`
  - **suggested_hints**:
- **ai_tracking**:
  - **ok**: `true`
  - **mode**: `db_on`
  - **summary**:
    - **agent_run**:
      - **total**: `2270`
      - **last_24h**: `0`
      - **last_7d**: `0`
    - **agent_run_cli**:
      - **total**: `140`
      - **last_24h**: `4`
      - **last_7d**: `91`
      - **success_count**: `3`
      - **error_count**: `0`
- **share_manifest**:
  - **ok**: `false`
  - **count**: `0`
  - **error**: `Manifest file not found: /home/mccoy/Projects/docs/SSOT/SHARE_MANIFEST.json`
- **eval_insights**:
  - **lm_indicator**:
    - **note**: `LM indicator export not available (file missing)`
    - **available**: `false`
  - **db_health**:
    - **note**: `DB health snapshot not available (file missing; run `make pm.snapshot`)`
    - **available**: `false`
  - **edge_class_counts**:
    - **note**: `Edge class counts export not available (file missing)`
    - **available**: `false`
- **kb_registry**:
  - **available**: `true`
  - **total**: `1185`
  - **valid**: `false`
  - **errors_count**: `318`
  - **warnings_count**: `3`
- **kb_hints**:
  1. Item:
    - **level**: `WARN`
    - **code**: `KB_MISSING_DOCS`
    - **message**: `KB registry references 316 missing file(s)`
    - **missing_count**: `316`
    - **missing_files**:
      1. `agentpm/adapters/AGENTS.md (ID`
      2. `agentpm/AGENTS.md (ID`
      3. `agentpm/ai_docs/AGENTS.md (ID`
      4. `agentpm/atlas/AGENTS.md (ID`
      5. `agentpm/biblescholar/AGENTS.md (ID`
      6. `agentpm/biblescholar/tests/AGENTS.md (ID`
      7. `agentpm/bus/AGENTS.md (ID`
      8. `agentpm/control_plane/AGENTS.md (ID`
      9. `agentpm/control_widgets/AGENTS.md (ID`
      10. `agentpm/db/AGENTS.md (ID`
  2. Item:
    - **level**: `WARN`
    - **code**: `KB_VALIDATION_ISSUES`
    - **message**: `KB registry validation issue: Registry validation failed: 318 errors`
  3. Item:
    - **level**: `WARN`
    - **code**: `KB_VALIDATION_ISSUES`
    - **message**: `KB registry validation issue: Registry has 3 warnings`
  4. Item:
    - **level**: `WARN`
    - **code**: `KB_DOC_STALE`
    - **message**: `9 document(s) are stale (exceed refresh interval)`
    - **stale_count**: `9`
    - **stale_docs**:
      1. Item:
        - **id**: `ssot::docs/ssot/data-flow-visual.md`
        - **path**: `docs/SSOT/data_flow_visual.md`
        - **title**: `SSOT::docs/SSOT/data_flow_visual.md`
      2. Item:
        - **id**: `ssot::docs/ssot/epoch-ledger.md`
        - **path**: `docs/SSOT/EPOCH_LEDGER.md`
        - **title**: `SSOT::docs/SSOT/EPOCH_LEDGER.md`
      3. Item:
        - **id**: `ssot::docs/ssot/graph-metrics-api.md`
        - **path**: `docs/SSOT/graph-metrics-api.md`
        - **title**: `SSOT::docs/SSOT/graph-metrics-api.md`
      4. Item:
        - **id**: `ssot::docs/ssot/graph-stats-api.md`
        - **path**: `docs/SSOT/graph-stats-api.md`
        - **title**: `SSOT::docs/SSOT/graph-stats-api.md`
      5. Item:
        - **id**: `ssot::docs/ssot/jsonld-schema.md`
        - **path**: `docs/SSOT/jsonld-schema.md`
        - **title**: `SSOT::docs/SSOT/jsonld-schema.md`
- **kb_doc_health**:
  - **available**: `true`
  - **metrics**:
    - **kb_fresh_ratio**:
      - **overall**: `72.57383966244726`
      - **by_subsystem**:
        - **ops**: `57.117117117117125`
        - **gematria**: `31.57894736842105`
        - **pm**: `91.62995594713657`
        - **general**: `93.83259911894272`
        - **docs**: `20.0`
        - **root**: `62.5`
        - **webui**: `96.07843137254902`
        - **biblescholar**: `88.23529411764706`
    - **kb_missing_count**:
      - **overall**: `316`
      - **by_subsystem**:
        - **ops**: `238`
        - **gematria**: `26`
        - **pm**: `19`
        - **general**: `6`
        - **docs**: `4`
        - **root**: `18`
        - **webui**: `1`
        - **biblescholar**: `4`
    - **kb_stale_count_by_subsystem**:
      - **general**: `8`
      - **webui**: `1`
    - **kb_fixes_applied_last_7d**: `0`
    - **kb_debt_burned_down**:
      - **overall**: `null`
      - **by_subsystem**:
      - **note**: `insufficient_history`
    - **notes**:
- **mcp_catalog**:
  - **available**: `false`
  - **tools_count**: `0`
  - **error**:

```
column "id" does not exist
LINE 1: SELECT id, name, ring FROM mcp.v_catalog ORDER BY id
               ^
```

- **control_widgets**:
  - **graph_compliance**:
    - **status**: `unknown`
    - **label**: `Graph compliance unknown (offline-safe mode)`
    - **metrics**:
      - **totalRunsWithViolations**: `0`
      - **windowDays**: `30`
  - **biblescholar_reference**:
    - **status**: `unknown`
    - **label**: `BibleScholar reference data unknown (offline-safe mode)`
    - **metrics**:
      - **totalQuestions**: `0`
      - **windowDays**: `30`
- **required_hints**:
  1. Item:
    - **logical_name**: `status.local_gates_first`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **text**: `Local gates are primary; CI is a mirror only. Never block on CI.`
      - **commands**:
        1. `ruff format --check . && ruff check .`
        2. `make book.smoke`
      - **metadata**:
        - **source**: `Rule-050`
        - **section**: `5.5`
      - **constraints**:
        - **rule_ref**: `050`
        - **local_first**: `true`
    - **priority**: `0`
- **suggested_hints**:
