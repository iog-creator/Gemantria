# schema_snapshot

**Generated**: 2025-12-01T16:48:20.323588+00:00
**Source**: `schema_snapshot.json`

---

- **schema**: `control`
- **generated_at**: `2025-12-01T16:48:09.002563+00:00`
- **tables**:
  1. Item:
    - **name**: `agent_run`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `project_id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `session_id`
        - **type**: `uuid`
        - **nullable**: `true`
        - **default**: `null`
      4. Item:
        - **name**: `tool`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `args_json`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `result_json`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `null`
      7. Item:
        - **name**: `violations_json`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `'[]'::jsonb`
      8. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `idx_agent_run_created`
        - **columns**:
          1. `created_at`
      2. Item:
        - **name**: `idx_agent_run_project`
        - **columns**:
          1. `project_id`
      3. Item:
        - **name**: `idx_agent_run_session`
        - **columns**:
          1. `session_id`
      4. Item:
        - **name**: `idx_agent_run_tool`
        - **columns**:
          1. `tool`
      5. Item:
        - **name**: `idx_agent_run_violations`
        - **columns**:
          1. `violations_json`
    - **foreign_keys**:
      1. Item:
        - **constraint**: `agent_run_session_id_fkey`
        - **column**: `session_id`
        - **references**: `control.capability_session`
        - **referenced_column**: `id`
  2. Item:
    - **name**: `agent_run_cli`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      3. Item:
        - **name**: `updated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      4. Item:
        - **name**: `command`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `status`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `request_json`
        - **type**: `jsonb`
        - **nullable**: `true`
        - **default**: `null`
      7. Item:
        - **name**: `response_json`
        - **type**: `jsonb`
        - **nullable**: `true`
        - **default**: `null`
      8. Item:
        - **name**: `error_text`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `idx_agent_run_cli_command`
        - **columns**:
          1. `command`
      2. Item:
        - **name**: `idx_agent_run_cli_created_at`
        - **columns**:
          1. `created_at`
      3. Item:
        - **name**: `idx_agent_run_cli_status`
        - **columns**:
          1. `status`
    - **foreign_keys**:
  3. Item:
    - **name**: `capability_rule`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `project_id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `ring`
        - **type**: `integer`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `allowlist`
        - **type**: `ARRAY`
        - **nullable**: `true`
        - **default**: `null`
      6. Item:
        - **name**: `denylist`
        - **type**: `ARRAY`
        - **nullable**: `true`
        - **default**: `null`
      7. Item:
        - **name**: `budgets`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `'{}'::jsonb`
      8. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `capability_rule_project_id_name_key`
        - **columns**:
          1. `project_id`
          2. `name`
      2. Item:
        - **name**: `idx_capability_rule_project`
        - **columns**:
          1. `project_id`
      3. Item:
        - **name**: `idx_capability_rule_ring`
        - **columns**:
          1. `ring`
    - **foreign_keys**:
  4. Item:
    - **name**: `capability_session`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `project_id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `rule_id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `por_json`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `tiny_menu`
        - **type**: `ARRAY`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `ttl_s`
        - **type**: `integer`
        - **nullable**: `false`
        - **default**: `null`
      7. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `idx_capability_session_created`
        - **columns**:
          1. `created_at`
      2. Item:
        - **name**: `idx_capability_session_project`
        - **columns**:
          1. `project_id`
      3. Item:
        - **name**: `idx_capability_session_rule`
        - **columns**:
          1. `rule_id`
    - **foreign_keys**:
      1. Item:
        - **constraint**: `capability_session_rule_id_fkey`
        - **column**: `rule_id`
        - **references**: `control.capability_rule`
        - **referenced_column**: `id`
  5. Item:
    - **name**: `doc_embedding`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `nextval('control.doc_embedding_id_seq'::regclass)`
      2. Item:
        - **name**: `fragment_id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `model_name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `embedding`
        - **type**: `USER-DEFINED`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `idx_doc_embedding_fragment_id`
        - **columns**:
          1. `fragment_id`
      2. Item:
        - **name**: `idx_doc_embedding_fragment_model_unique`
        - **columns**:
          1. `fragment_id`
          2. `model_name`
      3. Item:
        - **name**: `idx_doc_embedding_model_name`
        - **columns**:
          1. `model_name`
    - **foreign_keys**:
      1. Item:
        - **constraint**: `doc_embedding_fragment_id_fkey`
        - **column**: `fragment_id`
        - **references**: `control.doc_fragment`
        - **referenced_column**: `id`
  6. Item:
    - **name**: `doc_fragment`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `project_id`
        - **type**: `bigint`
        - **nullable**: `true`
        - **default**: `null`
      3. Item:
        - **name**: `src`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      4. Item:
        - **name**: `anchor`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      5. Item:
        - **name**: `sha256`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      6. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      7. Item:
        - **name**: `doc_id`
        - **type**: `uuid`
        - **nullable**: `true`
        - **default**: `null`
      8. Item:
        - **name**: `version_id`
        - **type**: `bigint`
        - **nullable**: `true`
        - **default**: `null`
      9. Item:
        - **name**: `fragment_index`
        - **type**: `integer`
        - **nullable**: `true`
        - **default**: `null`
      10. Item:
        - **name**: `fragment_type`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      11. Item:
        - **name**: `content`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      12. Item:
        - **name**: `updated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `true`
        - **default**: `now()`
      13. Item:
        - **name**: `meta`
        - **type**: `jsonb`
        - **nullable**: `true`
        - **default**: `'{}'::jsonb`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `doc_fragment_project_id_src_anchor_key`
        - **columns**:
          1. `project_id`
          2. `src`
          3. `anchor`
      2. Item:
        - **name**: `idx_doc_fragment_content_unique`
        - **columns**:
          1. `doc_id`
          2. `version_id`
          3. `fragment_index`
      3. Item:
        - **name**: `idx_doc_fragment_doc_id`
        - **columns**:
          1. `doc_id`
      4. Item:
        - **name**: `idx_doc_fragment_meta`
        - **columns**:
          1. `meta`
      5. Item:
        - **name**: `idx_doc_fragment_project`
        - **columns**:
          1. `project_id`
      6. Item:
        - **name**: `idx_doc_fragment_sha256`
        - **columns**:
          1. `sha256`
      7. Item:
        - **name**: `idx_doc_fragment_src`
        - **columns**:
          1. `src`
      8. Item:
        - **name**: `idx_doc_fragment_type`
        - **columns**:
          1. `fragment_type`
      9. Item:
        - **name**: `idx_doc_fragment_version_id`
        - **columns**:
          1. `version_id`
    - **foreign_keys**:
      1. Item:
        - **constraint**: `doc_fragment_doc_id_fkey`
        - **column**: `doc_id`
        - **references**: `control.doc_registry`
        - **referenced_column**: `doc_id`
      2. Item:
        - **constraint**: `doc_fragment_version_id_fkey`
        - **column**: `version_id`
        - **references**: `control.doc_version`
        - **referenced_column**: `id`
  7. Item:
    - **name**: `doc_registry`
    - **columns**:
      1. Item:
        - **name**: `doc_id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `logical_name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `role`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `repo_path`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `share_path`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      6. Item:
        - **name**: `is_ssot`
        - **type**: `boolean`
        - **nullable**: `false`
        - **default**: `null`
      7. Item:
        - **name**: `enabled`
        - **type**: `boolean`
        - **nullable**: `false`
        - **default**: `true`
      8. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      9. Item:
        - **name**: `updated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `doc_id`
    - **indexes**:
      1. Item:
        - **name**: `doc_registry_logical_name_key`
        - **columns**:
          1. `logical_name`
    - **foreign_keys**:
  8. Item:
    - **name**: `doc_sync_state`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `nextval('control.doc_sync_state_id_seq'::regclass)`
      2. Item:
        - **name**: `doc_id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `target`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `last_synced_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `true`
        - **default**: `null`
      5. Item:
        - **name**: `last_hash`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      6. Item:
        - **name**: `status`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      7. Item:
        - **name**: `message`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      8. Item:
        - **name**: `updated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
    - **foreign_keys**:
      1. Item:
        - **constraint**: `doc_sync_state_doc_id_fkey`
        - **column**: `doc_id`
        - **references**: `control.doc_registry`
        - **referenced_column**: `doc_id`
  9. Item:
    - **name**: `doc_version`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `nextval('control.doc_version_id_seq'::regclass)`
      2. Item:
        - **name**: `doc_id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `git_commit`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      4. Item:
        - **name**: `content_hash`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `size_bytes`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `recorded_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
    - **foreign_keys**:
      1. Item:
        - **constraint**: `doc_version_doc_id_fkey`
        - **column**: `doc_id`
        - **references**: `control.doc_registry`
        - **referenced_column**: `doc_id`
  10. Item:
    - **name**: `guard_definition`
    - **columns**:
      1. Item:
        - **name**: `guard_id`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      2. Item:
        - **name**: `name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `description`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      4. Item:
        - **name**: `rule_ids`
        - **type**: `ARRAY`
        - **nullable**: `false`
        - **default**: `'{}'::text[]`
      5. Item:
        - **name**: `strict_default`
        - **type**: `boolean`
        - **nullable**: `false`
        - **default**: `false`
      6. Item:
        - **name**: `script_path`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      7. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `guard_id`
    - **indexes**:
    - **foreign_keys**:
  11. Item:
    - **name**: `hint_registry`
    - **columns**:
      1. Item:
        - **name**: `hint_id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `logical_name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `scope`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `applies_to`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `kind`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `injection_mode`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      7. Item:
        - **name**: `payload`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `null`
      8. Item:
        - **name**: `enabled`
        - **type**: `boolean`
        - **nullable**: `false`
        - **default**: `true`
      9. Item:
        - **name**: `priority`
        - **type**: `integer`
        - **nullable**: `false`
        - **default**: `0`
      10. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      11. Item:
        - **name**: `updated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `hint_id`
    - **indexes**:
      1. Item:
        - **name**: `hint_registry_logical_name_key`
        - **columns**:
          1. `logical_name`
      2. Item:
        - **name**: `idx_hint_registry_applies_to`
        - **columns**:
          1. `applies_to`
      3. Item:
        - **name**: `idx_hint_registry_kind`
        - **columns**:
          1. `kind`
          2. `priority`
      4. Item:
        - **name**: `idx_hint_registry_scope`
        - **columns**:
          1. `scope`
    - **foreign_keys**:
  12. Item:
    - **name**: `kb_document`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `path`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `title`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      4. Item:
        - **name**: `doc_type`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      5. Item:
        - **name**: `project`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `'Gemantria.v2'::text`
      6. Item:
        - **name**: `content_hash`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      7. Item:
        - **name**: `size_bytes`
        - **type**: `integer`
        - **nullable**: `false`
        - **default**: `null`
      8. Item:
        - **name**: `mtime`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `null`
      9. Item:
        - **name**: `referenced_by`
        - **type**: `ARRAY`
        - **nullable**: `true`
        - **default**: `'{}'::text[]`
      10. Item:
        - **name**: `is_canonical`
        - **type**: `boolean`
        - **nullable**: `false`
        - **default**: `false`
      11. Item:
        - **name**: `status`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `'unreviewed'::text`
      12. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      13. Item:
        - **name**: `updated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      14. Item:
        - **name**: `embedding`
        - **type**: `USER-DEFINED`
        - **nullable**: `true`
        - **default**: `null`
      15. Item:
        - **name**: `lifecycle_stage`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `'active'::text`
      16. Item:
        - **name**: `phase_number`
        - **type**: `integer`
        - **nullable**: `true`
        - **default**: `null`
      17. Item:
        - **name**: `deprecated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `true`
        - **default**: `null`
      18. Item:
        - **name**: `deprecated_reason`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      19. Item:
        - **name**: `topic_key`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `idx_kb_document_content_hash`
        - **columns**:
          1. `content_hash`
      2. Item:
        - **name**: `idx_kb_document_doc_type`
        - **columns**:
          1. `doc_type`
      3. Item:
        - **name**: `idx_kb_document_embedding`
        - **columns**:
          1. `embedding`
      4. Item:
        - **name**: `idx_kb_document_path`
        - **columns**:
          1. `path`
      5. Item:
        - **name**: `idx_kb_document_project_hash`
        - **columns**:
          1. `project`
          2. `content_hash`
      6. Item:
        - **name**: `idx_kb_document_status`
        - **columns**:
          1. `status`
      7. Item:
        - **name**: `kb_document_path_key`
        - **columns**:
          1. `path`
    - **foreign_keys**:
  13. Item:
    - **name**: `rule_definition`
    - **columns**:
      1. Item:
        - **name**: `rule_id`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      2. Item:
        - **name**: `name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `status`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `description`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      5. Item:
        - **name**: `severity`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `docs_path`
        - **type**: `text`
        - **nullable**: `true`
        - **default**: `null`
      7. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      8. Item:
        - **name**: `updated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `rule_id`
    - **indexes**:
    - **foreign_keys**:
  14. Item:
    - **name**: `rule_source`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `nextval('control.rule_source_id_seq'::regclass)`
      2. Item:
        - **name**: `rule_id`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `source_type`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `path`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `content_hash`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
    - **foreign_keys**:
      1. Item:
        - **constraint**: `rule_source_rule_id_fkey`
        - **column**: `rule_id`
        - **references**: `control.rule_definition`
        - **referenced_column**: `rule_id`
  15. Item:
    - **name**: `system_state_ledger`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `source_of_truth`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `hash`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `generated_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
      6. Item:
        - **name**: `verified_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `true`
        - **default**: `null`
      7. Item:
        - **name**: `status`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `'unknown'::text`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `idx_system_state_ledger_name`
        - **columns**:
          1. `name`
      2. Item:
        - **name**: `idx_system_state_ledger_source`
        - **columns**:
          1. `source_of_truth`
      3. Item:
        - **name**: `idx_system_state_ledger_status`
        - **columns**:
          1. `status`
    - **foreign_keys**:
  16. Item:
    - **name**: `tool_catalog`
    - **columns**:
      1. Item:
        - **name**: `id`
        - **type**: `uuid`
        - **nullable**: `false`
        - **default**: `gen_random_uuid()`
      2. Item:
        - **name**: `project_id`
        - **type**: `bigint`
        - **nullable**: `false`
        - **default**: `null`
      3. Item:
        - **name**: `name`
        - **type**: `text`
        - **nullable**: `false`
        - **default**: `null`
      4. Item:
        - **name**: `ring`
        - **type**: `integer`
        - **nullable**: `false`
        - **default**: `null`
      5. Item:
        - **name**: `io_schema`
        - **type**: `jsonb`
        - **nullable**: `false`
        - **default**: `null`
      6. Item:
        - **name**: `enabled`
        - **type**: `boolean`
        - **nullable**: `false`
        - **default**: `true`
      7. Item:
        - **name**: `created_at`
        - **type**: `timestamp with time zone`
        - **nullable**: `false`
        - **default**: `now()`
    - **primary_key**:
      1. `id`
    - **indexes**:
      1. Item:
        - **name**: `idx_tool_catalog_enabled`
        - **columns**:
          1. `enabled`
      2. Item:
        - **name**: `idx_tool_catalog_project`
        - **columns**:
          1. `project_id`
      3. Item:
        - **name**: `idx_tool_catalog_ring`
        - **columns**:
          1. `ring`
      4. Item:
        - **name**: `tool_catalog_project_id_name_key`
        - **columns**:
          1. `project_id`
          2. `name`
    - **foreign_keys**:
