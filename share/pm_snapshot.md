# pm_snapshot

**Generated**: 2025-11-30T03:25:26.187576+00:00
**Source**: `pm_snapshot.json`

---

- **overall_ok**: `true`
- **generated_at**: `2025-11-29T19:25:15-08:00`
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
    - **available**: `false`
    - **total**: `0`
    - **by_subsystem**:
    - **by_type**:
    - **hints**:
      1. Item:
        - **level**: `INFO`
        - **code**: `KB_REGISTRY_UNAVAILABLE`
        - **message**: `KB registry file not found (registry may not be seeded yet)`
    - **key_docs**:
    - **freshness**:
- **reality_check**:
  - **command**: `reality.check`
  - **mode**: `HINT`
  - **timestamp**: `2025-11-30T03:25:15.745239+00:00`
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
    - **generated_at**: `2025-11-30T03:25:15.745261+00:00`
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
            - **row_count**: `131`
            - **latest_created_at**: `2025-11-29T17:34:39.838318-08:00`
          - **control.agent_run**:
            - **present**: `true`
            - **row_count**: `2159`
            - **latest_created_at**: `2025-11-27T09:10:02.584405-08:00`
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
          - **control.agent_run**: `2159`
          - **control.agent_run_cli**: `36`
          - **control.capability_rule**: `5`
          - **control.capability_session**: `5`
          - **control.doc_embedding**: `2963`
          - **control.doc_fragment**: `2968`
          - **control.doc_registry**: `193`
          - **control.doc_sync_state**: `0`
          - **control.doc_version**: `758`
          - **control.guard_definition**: `0`
          - **control.hint_registry**: `5`
          - **control.kb_document**: `4238`
          - **control.rule_definition**: `69`
          - **control.rule_source**: `138`
          - **control.system_state_ledger**: `360`
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
          - **public.concept_clusters**: `0`
          - **public.concept_metadata**: `0`
          - **public.concept_metrics**: `0`
          - **public.concept_network**: `1733`
          - **public.concept_relations**: `14330`
          - **public.concept_rerank_cache**: `0`
          - **public.concepts**: `25`
          - **public.confidence_validation_log**: `35`
          - **public.connections**: `0`
          - **public.context_awareness_events**: `0`
          - **public.context_success_patterns**: `0`
          - **public.cross_references**: `0`
          - **public.doctrinal_links**: `0`
          - **public.document_access_log**: `1`
          - **public.document_sections**: `397`
          - **public.governance_artifacts**: `131`
          - **public.governance_compliance_log**: `226`
          - **public.hint_emissions**: `719`
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
          - **public.verse_noun_occurrences**: `0`
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
                - **name**: `idx_doc_fragment_content_unique`
                - **columns**:
                  1. `doc_id`
                  2. `version_id`
                  3. `fragment_index`
                - **unique**: `true`
              3. Item:
                - **name**: `idx_doc_fragment_doc_id`
                - **columns**:
                  1. `doc_id`
                - **unique**: `false`
              4. Item:
                - **name**: `idx_doc_fragment_project`
                - **columns**:
                  1. `project_id`
                - **unique**: `false`
              5. Item:
                - **name**: `idx_doc_fragment_sha256`
                - **columns**:
                  1. `sha256`
                - **unique**: `false`
              6. Item:
                - **name**: `idx_doc_fragment_src`
                - **columns**:
                  1. `src`
                - **unique**: `false`
              7. Item:
                - **name**: `idx_doc_fragment_type`
                - **columns**:
                  1. `fragment_type`
                - **unique**: `false`
              8. Item:
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
      - **db_off**: `false`
      - **error_rate**: `0.6744186046511628`
      - **generated_at**: `2025-11-30T03:10:33.295305+00:00`
      - **reason**: `high_error_rate`
      - **status**: `degraded`
      - **success_rate**: `0.32558139534883723`
      - **top_error_reason**: `lm_studio_error`
      - **total_calls**: `2150`
      - **window_days**: `7`
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
    2. `KB: KB registry file not found (registry may not be seeded yet)`
  - **kb_hints**:
    1. Item:
      - **level**: `INFO`
      - **code**: `KB_REGISTRY_UNAVAILABLE`
      - **message**: `KB registry file not found (registry may not be seeded yet)`
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
      - **total**: `2159`
      - **last_24h**: `0`
      - **last_7d**: `2154`
    - **agent_run_cli**:
      - **total**: `36`
      - **last_24h**: `15`
      - **last_7d**: `36`
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
  - **available**: `false`
  - **total**: `0`
  - **valid**: `true`
  - **errors_count**: `0`
  - **warnings_count**: `0`
- **kb_hints**:
  1. Item:
    - **level**: `INFO`
    - **code**: `KB_REGISTRY_UNAVAILABLE`
    - **message**: `KB registry file not found (registry may not be seeded yet)`
- **kb_doc_health**:
  - **available**: `false`
  - **metrics**:
    - **kb_fresh_ratio**:
      - **overall**: `null`
      - **by_subsystem**:
    - **kb_missing_count**:
      - **overall**: `0`
      - **by_subsystem**:
    - **kb_stale_count_by_subsystem**:
    - **kb_fixes_applied_last_7d**: `0`
    - **kb_debt_burned_down**:
      - **overall**: `null`
      - **by_subsystem**:
      - **note**: `insufficient_history`
    - **notes**:
      1. `KB registry not found; metrics unavailable`
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
