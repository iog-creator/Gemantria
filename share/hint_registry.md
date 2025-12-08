# hint_registry

**Generated**: 2025-12-08T17:09:47.862277+00:00
**Source**: `hint_registry.json`

---

- **schema**: `control.hint_registry.v1`
- **generated_at**: `2025-12-08T17:09:35.617273+00:00`
- **table**: `control.hint_registry`
- **rows**:
  1. Item:
    - **hint_id**: `06d80888-852b-4360-a14e-32c5bfcb7901`
    - **logical_name**: `reality.green.backup_system.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `backup_system`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `make backup.surfaces`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  2. Item:
    - **hint_id**: `178555a3-fade-4659-bdec-a2331dfe02f8`
    - **logical_name**: `data.bible_lemma_english`
    - **scope**: `data`
    - **applies_to**:
      - **flow**: `ingest_bible_nouns`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**: `Bible DB 'lemma' column contains English definitions. Use surface form for Hebrew text & Gematria.`
      - **commands**:
      - **metadata**:
        - **source**: `Phase 8 Recovery`
      - **constraints**:
        - **use_surface**: `true`
    - **enabled**: `true`
    - **priority**: `20`
    - **created_at**: `2025-12-02T11:03:55.219239-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  3. Item:
    - **hint_id**: `187b7465-5d06-4b20-83a2-344146341f78`
    - **logical_name**: `reality.green.agents_dms_contract.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `agents_dms_contract`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `make housekeeping  # sync AGENTS.md with DMS`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  4. Item:
    - **hint_id**: `1b1ab1a8-8385-458b-a921-46e497bd71b3`
    - **logical_name**: `reality.green.share_sync_and_exports.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `share_sync_and_exports`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `make share.sync`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  5. Item:
    - **hint_id**: `1fd8c188-f8d0-4b0e-830d-1bd58a80ad9e`
    - **logical_name**: `share.dms_only`
    - **scope**: `handoff`
    - **applies_to**:
      - **flow**: `handoff.generate`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**: `share/ sync is DMS-only. No manifest fallback.`
      - **commands**:
        1. `make share.sync`
      - **metadata**:
        - **source**: `Rule-030`
        - **agent_file**: `AGENTS.md`
      - **constraints**:
        - **dms_only**: `true`
        - **rule_ref**: `030`
    - **enabled**: `true`
    - **priority**: `1`
    - **created_at**: `2025-11-29T07:24:46.201152-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  6. Item:
    - **hint_id**: `1ff224d9-35a4-4b4e-a1b7-80e0e9afef42`
    - **logical_name**: `HINT-CODE-001`
    - **scope**: `python`
    - **applies_to**:
      - **flow**: `datetime_usage`
      - **category**: `stdlib`
    - **kind**: `REQUIRED`
    - **injection_mode**: `TOOL_CALL`
    - **payload**:
      - **error**: `AttributeError: type object datetime has no attribute timezone`
      - **title**: `datetime.timezone vs timezone import`
      - **wrong**: `datetime.now(datetime.timezone.utc)`
      - **problem**: `datetime.datetime.timezone does not exist`
      - **severity**: `HIGH`
      - **correct_v1**: `from datetime import timezone, datetime\ndatetime.now(timezone.utc)`
      - **correct_v2**: `from datetime import UTC\ndatetime.now(UTC)`
      - **python_version**: `3.11+ prefers UTC, <3.11 use timezone.utc`
    - **enabled**: `true`
    - **priority**: `7`
    - **created_at**: `2025-12-02T10:03:34.384140-08:00`
    - **updated_at**: `2025-12-02T10:03:34.384140-08:00`
  7. Item:
    - **hint_id**: `22ea34c9-a463-48be-87b2-fe66ed737466`
    - **logical_name**: `HINT-DEBUG-001`
    - **scope**: `debugging`
    - **applies_to**:
      - **flow**: `empty_analytics`
      - **category**: `troubleshooting`
    - **kind**: `DEBUG`
    - **injection_mode**: `POST_PROMPT`
    - **payload**:
      - **title**: `Analytics producing empty outputs`
      - **tools**:
        1. `jq for JSON inspection`
        2. `psql for DB queries`
        3. `grep for threshold values`
      - **severity**: `LOW`
      - **checklist**:
        1. `1. Check input file exists and has data`
        2. `2. Verify DB connection if data from DB`
        3. `3. Check thresholds/filters (min nodes, window size)`
        4. `4. Inspect sample input data structure`
        5. `5. Run script with --verbose or add logging`
      - **common_causes**:
        1. `Insufficient input data`
        2. `Missing metadata fields`
        3. `Strict threshold filters`
        4. `Schema mismatch`
    - **enabled**: `true`
    - **priority**: `30`
    - **created_at**: `2025-12-02T10:03:48.163957-08:00`
    - **updated_at**: `2025-12-02T10:03:48.163957-08:00`
  8. Item:
    - **hint_id**: `2f7f8461-dcec-41cb-9383-bafad1c4b5e8`
    - **logical_name**: `HINT-SCHEMA-001`
    - **scope**: `database`
    - **applies_to**:
      - **flow**: `schema_discovery`
      - **category**: `metadata`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**: `Use LEFT JOIN v_concepts_with_verses not concepts for verse data`
      - **title**: `concepts table lacks verse metadata`
      - **problem**: `Code analysis suggests concepts has book/chapter/verse but it does not`
      - **severity**: `CRITICAL`
      - **code_pattern**: `JOIN concepts c ON ... - add JOIN v_concepts_with_verses v`
      - **actual_source**: `v_concepts_with_verses VIEW has the metadata`
      - **fields_available**:
        1. `gematria_value`
        2. `book_source`
        3. `verses (JSONB)`
    - **enabled**: `true`
    - **priority**: `5`
    - **created_at**: `2025-12-02T10:03:16.179369-08:00`
    - **updated_at**: `2025-12-02T10:03:16.179369-08:00`
  9. Item:
    - **hint_id**: `310fb93d-0568-488b-ae7c-f2472365418b`
    - **logical_name**: `governance.fail_closed`
    - **scope**: `handoff`
    - **applies_to**:
      - **flow**: `handoff.generate`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**: `Governance scripts must fail-closed on errors. No silent fallbacks.`
      - **commands**:
      - **metadata**:
        - **source**: `Rule-039`
        - **agent_file**: `AGENTS.md`
      - **constraints**:
        - **rule_ref**: `039`
        - **fail_closed**: `true`
    - **enabled**: `true`
    - **priority**: `5`
    - **created_at**: `2025-11-29T07:41:52.592675-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  10. Item:
    - **hint_id**: `31b55757-fb41-4049-a28c-ba264ead1a7e`
    - **logical_name**: `HINT-PHASE-002`
    - **scope**: `analytics`
    - **applies_to**:
      - **flow**: `correlation_analytics`
      - **phase**: `Phase-10`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**: `Run backfill_noun_embeddings.py OR create correlation view`
      - **title**: `Phase 10 needs embeddings and view/scipy`
      - **problem**: `Correlation analytics requires concept embeddings + DB view OR scipy`
      - **symptom**: `total_correlations = 0`
      - **severity**: `CRITICAL`
      - **threshold**: `>=2 concepts with non-NULL embeddings`
      - **data_source**: `concept_network table`
      - **required_setup**:
        1. `concept_network.embedding populated`
        2. `concept_correlations view OR scipy installed`
    - **enabled**: `true`
    - **priority**: `4`
    - **created_at**: `2025-12-02T10:03:48.136139-08:00`
    - **updated_at**: `2025-12-02T10:03:48.136139-08:00`
  11. Item:
    - **hint_id**: `4051130b-41b4-40af-bb27-3b63003d9988`
    - **logical_name**: `HINT-CALC-001`
    - **scope**: `analytics`
    - **applies_to**:
      - **flow**: `temporal_analytics`
      - **category**: `calculation`
    - **kind**: `SUGGESTED`
    - **injection_mode**: `TOOL_CALL`
    - **payload**:
      - **sql**: `chapter \* 1000 + verse_num AS position`
      - **title**: `Standard position calculation formula`
      - **usage**: `Phase 8 temporal analytics, export_stats.py`
      - **python**: `position = (chapter \* 1000) + verse if (chapter and verse) else None`
      - **formula**: `position = (chapter \* 1000) + verse`
      - **code_ref**: `scripts/export_stats.py:846`
      - **severity**: `LOW`
      - **rationale**: `Allows up to 999 verses per chapter, maintains sort order`
    - **enabled**: `true`
    - **priority**: `25`
    - **created_at**: `2025-12-02T10:03:26.424702-08:00`
    - **updated_at**: `2025-12-02T10:03:26.424702-08:00`
  12. Item:
    - **hint_id**: `4085630c-f020-437a-9d59-19589c29f71d`
    - **logical_name**: `HINT-DB-001`
    - **scope**: `database`
    - **applies_to**:
      - **flow**: `db_access`
      - **trigger**: `agent_proceeds_without_DSN`
      - **category**: `governance`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**:

```
1. STOP immediately if DSN missing
2. Add to .env: GEMATRIA_DSN=postgresql://mccoy@/gematria?host=/var/run/postgresql
3. Verify: psql $GEMATRIA_DSN -c SELECT current_database();
```

      - **title**: `Missing DSN is fatal error`
      - **doc_ref**: `docs/hints/HINT-DB-001-dsn-mandatory.md, docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md`
      - **problem**: `Agent accepted missing GEMATRIA_DSN/BIBLE_DB_DSN as warning instead of blocking`
      - **severity**: `CRITICAL`
      - **agent_behavior**: `MUST HALT, never proceed with code-only analysis`
      - **governance_violated**:
        1. `Rule-050/051/052`
        2. `Rule-066`
        3. `Rule-069`
        4. `Rule-070`
        5. `Phase-14`
        6. `Phase-15`
    - **enabled**: `true`
    - **priority**: `5`
    - **created_at**: `2025-12-02T10:00:30.234199-08:00`
    - **updated_at**: `2025-12-02T10:00:30.234199-08:00`
  13. Item:
    - **hint_id**: `42609cbf-9344-4e04-a85f-5fb4514ec904`
    - **logical_name**: `reality.green.dms_hint_registry.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `dms_hint_registry`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `make housekeeping  # ensure DMS hints are populated`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  14. Item:
    - **hint_id**: `4e53da3e-07a8-4084-bd45-c6f1124e745a`
    - **logical_name**: `status.local_gates_first`
    - **scope**: `status_api`
    - **applies_to**:
      - **flow**: `status_snapshot`
    - **kind**: `REQUIRED`
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
    - **enabled**: `true`
    - **priority**: `0`
    - **created_at**: `2025-11-29T07:24:46.201152-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  15. Item:
    - **hint_id**: `4f463f01-399e-4c2b-82b0-0f1974a20f8d`
    - **logical_name**: `reality.green.repo_alignment_(layer_4).remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `repo_alignment_(layer_4)`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/guards/guard_repo_layer4_alignment.py --mode HINT`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  16. Item:
    - **hint_id**: `51004f23-e213-41c5-a389-7f627b48c336`
    - **logical_name**: `reality.green.root_surface.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `root_surface`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/guards/guard_root_surface_policy.py --mode HINT`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  17. Item:
    - **hint_id**: `5bc8c31d-c42f-411a-bfaa-56a893aedf15`
    - **logical_name**: `HINT-GRAPH-001`
    - **scope**: `graph_export`
    - **applies_to**:
      - **flow**: `export_graph`
      - **component**: `node_source`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**: `Check exports/ai_nouns.json - if stale/test data, rename to .bak to force DB fallback`
      - **title**: `ai_nouns.json silently overrides DB nodes`
      - **problem**: `export_graph.py prioritizes ai_nouns.json over database, causing 1-node graphs if file is stale`
      - **symptom**: `graph_latest.json has 1 node despite DB having 1000s`
      - **code_ref**: `scripts/export_graph.py:262-273`
      - **severity**: `HIGH`
      - **prevention**: `ai_nouns.json should be generated, not manually edited`
    - **enabled**: `true`
    - **priority**: `10`
    - **created_at**: `2025-12-02T10:03:08.590675-08:00`
    - **updated_at**: `2025-12-02T10:03:08.590675-08:00`
  18. Item:
    - **hint_id**: `5edb1012-6141-4778-ab6c-e1ed17c73b81`
    - **logical_name**: `HINT-MIGRATION-001`
    - **scope**: `database`
    - **applies_to**:
      - **flow**: `correlation_analytics`
      - **category**: `schema`
    - **kind**: `SUGGESTED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**: `Run migration: psql $GEMATRIA_DSN -f migrations/???_concept_correlations.sql`
      - **title**: `concept_correlations view not created`
      - **problem**: `Phase 10 expects concept_correlations view but it does not exist`
      - **symptom**: `relation concept_correlations does not exist`
      - **code_ref**: `scripts/export_stats.py::export_correlations`
      - **fallback**: `Python scipy fallback will be used automatically`
      - **severity**: `MEDIUM`
    - **enabled**: `true`
    - **priority**: `18`
    - **created_at**: `2025-12-02T10:03:44.116411-08:00`
    - **updated_at**: `2025-12-02T10:03:44.116411-08:00`
  19. Item:
    - **hint_id**: `6718674b-53db-40b6-ac03-1c04f9a24a02`
    - **logical_name**: `reality.green.handoff_kernel.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `handoff_kernel`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/pm/generate_handoff_kernel.py`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  20. Item:
    - **hint_id**: `6860e0fa-b018-453e-b584-18f51f2bde43`
    - **logical_name**: `reality.green.db_health.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `db_health`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `make book.smoke`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  21. Item:
    - **hint_id**: `716489ab-c26b-4767-8968-5c0171f0656a`
    - **logical_name**: `reality.green.oa_state.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `oa_state`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python pmagent/oa/state.py  # refresh OA snapshot`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  22. Item:
    - **hint_id**: `725f5044-1091-42dc-a572-32a99c677d3d`
    - **logical_name**: `reality.green.bootstrap_consistency.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `bootstrap_consistency`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/pm/generate_pm_bootstrap_state.py`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  23. Item:
    - **hint_id**: `7d376b6d-b4d0-42b8-b286-e7cbd01b942b`
    - **logical_name**: `oa.boot.kernel_first`
    - **scope**: `orchestrator_assistant`
    - **applies_to**:
      - **flow**: `handoff.oa_boot`
      - **rule**: `026`
      - **agent**: `oa`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**:

```
On new OA session, read `PM_KERNEL.json` and `PM_BOOTSTRAP_STATE.json` before reasoning. Never infer phase or health from prior chats. If the kernel indicates degraded health, OA must warn PM and refuse normal analytical work until remediation scope is defined.
```

      - **commands**:
        1. `cat share/handoff/PM_KERNEL.json`
        2. `cat share/PM_BOOTSTRAP_STATE.json`
      - **metadata**:
        - **severity**: `ERROR`
        - **docs_refs**:
          1. `docs/SSOT/PM_HANDOFF_PROTOCOL.md`
          2. `docs/SSOT/SHARE_FOLDER_ANALYSIS.md`
        - **description**: `Force Orchestrator Assistant to treat kernel as authority and escalate degraded health`
      - **constraints**:
        - **kernel_required**: `true`
        - **no_phase_inference**: `true`
        - **escalate_degraded_health**: `true`
    - **enabled**: `true`
    - **priority**: `0`
    - **created_at**: `2025-12-06T09:09:19.892311-08:00`
    - **updated_at**: `2025-12-06T09:09:19.892311-08:00`
  24. Item:
    - **hint_id**: `7fe0a06e-2b53-4ca1-9e03-213f6e5722ab`
    - **logical_name**: `HINT-SCHEMA-002`
    - **scope**: `database`
    - **applies_to**:
      - **flow**: `jsonb_extraction`
      - **category**: `postgres`
    - **kind**: `SUGGESTED`
    - **injection_mode**: `TOOL_CALL`
    - **payload**:
      - **title**: `JSONB array requires special extraction`
      - **problem**: `verses field is JSONB array, cannot use direct column access`
      - **severity**: `MEDIUM`
      - **sql_code**: `(verses::jsonb->0->>""chapter"")::int`
      - **python_code**:

```
verses_json = row[8]  # JSONB from query\nif verses_json:\n    first = verses_json[0]\n    chapter = first.get(""chapter"")\n    verse = first.get(""verse"")
```

      - **common_error**: `column verses.chapter does not exist`
    - **enabled**: `true`
    - **priority**: `15`
    - **created_at**: `2025-12-02T10:03:16.208376-08:00`
    - **updated_at**: `2025-12-02T10:03:16.208376-08:00`
  25. Item:
    - **hint_id**: `8096a79c-3350-484b-93e3-26f5c6798ddb`
    - **logical_name**: `reality.green.ledger_verification.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `ledger_verification`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `make state.sync`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  26. Item:
    - **hint_id**: `818c8fcb-a16b-4e5c-a589-c36f8abaabc0`
    - **logical_name**: `HINT-PHASE-001`
    - **scope**: `analytics`
    - **applies_to**:
      - **flow**: `temporal_analytics`
      - **phase**: `Phase-8`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**: `Enrich graph export with verse metadata before Phase 8`
      - **title**: `Phase 8 needs position/gematria metadata`
      - **problem**: `Temporal analytics requires nodes with position, chapter, verse, gematria`
      - **symptom**: `total_series = 0 despite many nodes`
      - **severity**: `CRITICAL`
      - **threshold**: `>=10 nodes with complete metadata for rolling window`
      - **data_source**: `v_concepts_with_verses view`
      - **required_fields**:
        1. `position OR (chapter + verse)`
        2. `gematria`
    - **enabled**: `true`
    - **priority**: `3`
    - **created_at**: `2025-12-02T10:03:44.147432-08:00`
    - **updated_at**: `2025-12-02T10:03:44.147432-08:00`
  27. Item:
    - **hint_id**: `86f9df85-32f1-4138-a016-f246fe6662c1`
    - **logical_name**: `reality.green.ketiv_primary_policy.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `ketiv_primary_policy`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/guards/guard_ketiv_primary.py`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  28. Item:
    - **hint_id**: `899b6bf1-02ce-430b-9229-f2cd37690d6f`
    - **logical_name**: `docs.dms_only`
    - **scope**: `handoff`
    - **applies_to**:
      - **flow**: `handoff.generate`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**: `DMS-only, no fallback. share/ is derived from control.doc_registry only.`
      - **commands**:
      - **metadata**:
        - **source**: `Rule-050`
        - **agent_file**: `AGENTS.md`
      - **constraints**:
        - **rule_ref**: `050`
        - **no_fallback**: `true`
    - **enabled**: `true`
    - **priority**: `0`
    - **created_at**: `2025-11-29T07:24:46.201152-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  29. Item:
    - **hint_id**: `a9f29790-e359-48f6-b9b8-abef3d83f1c8`
    - **logical_name**: `reality.green.dms_metadata.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `dms_metadata`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/governance/dms_doc_cleanup.py --dry-run`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  30. Item:
    - **hint_id**: `b9f55f14-c664-49be-b16b-900d8bbc9ea6`
    - **logical_name**: `ops.regenerate_truncation`
    - **scope**: `ops`
    - **applies_to**:
      - **flow**: `regenerate_network`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**: `Regeneration TRUNCATES concept_network. Ensure canonical data is backed up before running.`
      - **commands**:
        1. `pmagent graph regenerate --force`
      - **metadata**:
        - **source**: `Phase 8 Recovery`
      - **constraints**:
        - **backup_required**: `true`
    - **enabled**: `true`
    - **priority**: `20`
    - **created_at**: `2025-12-02T11:03:55.219239-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  31. Item:
    - **hint_id**: `c7873c24-15a6-4e8e-9467-c9e1ac39fd7b`
    - **logical_name**: `reality.green.share_sync_policy.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `share_sync_policy`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/guards/guard_share_sync_policy.py --mode HINT`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  32. Item:
    - **hint_id**: `cc06be38-0322-48c3-bb93-8ea127df39d7`
    - **logical_name**: `reality.green.dms_alignment.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `dms_alignment`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/guards/guard_dms_share_alignment.py --mode HINT`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  33. Item:
    - **hint_id**: `d16d7755-7262-4309-a5ad-de46c931bcd0`
    - **logical_name**: `reality.green.webui_shell_sanity.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `webui_shell_sanity`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `Check webui/orchestrator-shell/ for missing files`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  34. Item:
    - **hint_id**: `d46f4e39-180a-43d8-86ea-5f2093505f4f`
    - **logical_name**: `reality.green.agents.md_sync.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `agents.md_sync`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `touch scripts/AGENTS.md  # if code changes are intentional`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  35. Item:
    - **hint_id**: `d60115a0-3b24-4d37-803e-60a3ac070c1f`
    - **logical_name**: `reality.green.control_plane_health.remediation`
    - **scope**: `reality.green`
    - **applies_to**:
      - **flow**: `control_plane_health`
      - **category**: `remediation`
    - **kind**: `REQUIRED`
    - **injection_mode**: `META_ONLY`
    - **payload**:
      - **command**: `python scripts/guards/guard_control_plane_health.py`
    - **enabled**: `true`
    - **priority**: `100`
    - **created_at**: `2025-12-07T14:23:51.217267-08:00`
    - **updated_at**: `2025-12-07T14:23:51.217267-08:00`
  36. Item:
    - **hint_id**: `dbd5c5b3-a242-4a5d-8dc6-9f60dac38acf`
    - **logical_name**: `HINT-DEP-001`
    - **scope**: `environment`
    - **applies_to**:
      - **flow**: `correlation_analytics`
      - **category**: `dependencies`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**: `pip install scipy (within activated venv)`
      - **title**: `scipy required for correlation fallback`
      - **problem**: `Phase 10 Python fallback needs scipy.stats.pearsonr`
      - **symptom**: `ERROR: scipy not available for correlation computation fallback`
      - **used_by**:
        1. `scripts/export_stats.py::_compute_correlations_python`
      - **severity**: `MEDIUM`
      - **when_needed**: `If concept_correlations DB view unavailable`
    - **enabled**: `true`
    - **priority**: `12`
    - **created_at**: `2025-12-02T10:03:34.417893-08:00`
    - **updated_at**: `2025-12-02T10:03:34.417893-08:00`
  37. Item:
    - **hint_id**: `de73c666-b0e3-4ee4-984b-52cd1c9383e4`
    - **logical_name**: `HINT-GRAPH-002`
    - **scope**: `graph_export`
    - **applies_to**:
      - **flow**: `export_graph`
      - **component**: `fast_lane`
    - **kind**: `SUGGESTED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**: `Remove or rename exports/graph_latest.json before running export`
      - **title**: `Fast-lane check blocks graph re-export`
      - **problem**: `export_graph.py detects existing graph_latest.json and skips DB rebuild`
      - **symptom**: `Script runs but graph not updated despite DB changes`
      - **code_ref**: `grep fast.lane scripts/export_graph.py`
      - **severity**: `MEDIUM`
      - **code_behavior**: `Optimization to avoid redundant exports`
    - **enabled**: `true`
    - **priority**: `20`
    - **created_at**: `2025-12-02T10:03:08.623253-08:00`
    - **updated_at**: `2025-12-02T10:03:08.623253-08:00`
  38. Item:
    - **hint_id**: `e0045b5e-2ce3-4482-8aa7-b844235adb1a`
    - **logical_name**: `reality.green.required_checks`
    - **scope**: `status_api`
    - **applies_to**:
      - **flow**: `reality_check`
    - **kind**: `REQUIRED`
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
    - **enabled**: `true`
    - **priority**: `10`
    - **created_at**: `2025-11-29T07:41:52.592675-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  39. Item:
    - **hint_id**: `e0919a4a-80aa-43a9-8b36-11454c68d318`
    - **logical_name**: `HINT-SCHEMA-003`
    - **scope**: `database`
    - **applies_to**:
      - **flow**: `joins`
      - **category**: `postgres`
    - **kind**: `REQUIRED`
    - **injection_mode**: `TOOL_CALL`
    - **payload**:
      - **title**: `UUID joins require ::text casting`
      - **problem**: `concept_id is UUID, joining to text fields fails without cast`
      - **symptom**: `ERROR: operator does not exist: uuid = text`
      - **severity**: `HIGH`
      - **applies_to**:
        1. `concept_network`
        2. `concepts`
        3. `v_concepts_with_verses`
      - **fix_pattern**: `c.id::text = n.concept_id::text`
      - **wrong_pattern**: `c.id = n.concept_id`
    - **enabled**: `true`
    - **priority**: `8`
    - **created_at**: `2025-12-02T10:03:26.396198-08:00`
    - **updated_at**: `2025-12-02T10:03:26.396198-08:00`
  40. Item:
    - **hint_id**: `e9f6d947-496b-4efd-b1b3-83023c42c27e`
    - **logical_name**: `HINT-ENV-001`
    - **scope**: `environment`
    - **applies_to**:
      - **flow**: `setup`
      - **trigger**: `GEMATRIA_DSN_empty_OR_ModuleNotFoundError`
      - **category**: `environment`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **fix**:

```
1. Activate venv: source .venv/bin/activate
2. Set PYTHONPATH: export PYTHONPATH=$(pwd):$PYTHONPATH
3. Verify: which python (should show .venv/bin/python)
```

      - **title**: `Python venv not activated`
      - **doc_ref**: `docs/hints/HINT-ENV-001-venv-not-activated.md`
      - **problem**: `Scripts cannot access project modules or environment variables`
      - **severity**: `CRITICAL`
    - **enabled**: `true`
    - **priority**: `10`
    - **created_at**: `2025-12-02T10:00:27.278878-08:00`
    - **updated_at**: `2025-12-02T10:00:27.278878-08:00`
  41. Item:
    - **hint_id**: `edf85953-cd58-4165-8e3b-a324bd9adf48`
    - **logical_name**: `db.dsn_env_var_ignored`
    - **scope**: `infra`
    - **applies_to**:
      - **flow**: `db_connection`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**: `get_connection_dsn() ignores 'env_var' arg. Use scripts.config.env for specific DBs (e.g. Bible DB).`
      - **commands**:
      - **metadata**:
        - **source**: `Phase 8 Recovery`
      - **constraints**:
        - **use_loader**: `true`
    - **enabled**: `true`
    - **priority**: `20`
    - **created_at**: `2025-12-02T11:03:55.219239-08:00`
    - **updated_at**: `2025-12-02T11:03:55.219239-08:00`
  42. Item:
    - **hint_id**: `f04024e4-0f8c-4769-9875-e9f1f56cc5b9`
    - **logical_name**: `ops.preflight.kernel_health`
    - **scope**: `ops`
    - **applies_to**:
      - **flow**: `ops.preflight`
      - **rule**: `026`
      - **agent**: `cursor`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**:

```
Before any destructive operation (deleting or regenerating share surfaces, schema changes, bulk writes), load `PM_KERNEL.json`, verify branch/phase match, ensure backup is recent, and check DMS alignment, share sync, and bootstrap consistency. If any guard fails, restrict scope to remediation only.
```

      - **commands**:
        1. `cat share/handoff/PM_KERNEL.json`
        2. `git rev-parse --abbrev-ref HEAD`
        3. `make reality.green`
      - **metadata**:
        - **severity**: `ERROR`
        - **docs_refs**:
          1. `docs/SSOT/EXECUTION_CONTRACT.md`
          2. `docs/SSOT/PM_HANDOFF_PROTOCOL.md`
          3. `docs/SSOT/SHARE_FOLDER_ANALYSIS.md`
          4. `docs/SSOT/PHASE26_HANDOFF_KERNEL.md`
        - **description**: `Force Cursor/OPS to run kernel-aware preflight before destructive operations`
      - **constraints**:
        - **kernel_branch_match**: `true`
        - **guards_green_required**: `true`
        - **remediation_only_if_degraded**: `true`
    - **enabled**: `true`
    - **priority**: `0`
    - **created_at**: `2025-12-06T09:09:19.892311-08:00`
    - **updated_at**: `2025-12-06T09:09:19.892311-08:00`
  43. Item:
    - **hint_id**: `fd7d1f9c-98e4-4036-8d67-fb85b1e92a02`
    - **logical_name**: `pm.boot.kernel_first`
    - **scope**: `pm`
    - **applies_to**:
      - **flow**: `handoff.pm_boot`
      - **rule**: `026`
      - **agent**: `pm`
    - **kind**: `REQUIRED`
    - **injection_mode**: `PRE_PROMPT`
    - **payload**:
      - **text**:

```
New PM chat must \*first\* read `share/handoff/PM_KERNEL.json`, then `share/PM_BOOTSTRAP_STATE.json`, and only then phase docs. If kernel and bootstrap disagree, or `health.reality_green=false`, PM must enter degraded mode and halt phase work.
```

      - **commands**:
        1. `cat share/handoff/PM_KERNEL.json`
        2. `cat share/PM_BOOTSTRAP_STATE.json`
      - **metadata**:
        - **severity**: `ERROR`
        - **docs_refs**:
          1. `docs/SSOT/PM_HANDOFF_PROTOCOL.md`
          2. `docs/SSOT/SHARE_FOLDER_ANALYSIS.md`
          3. `docs/SSOT/PHASE26_HANDOFF_KERNEL.md`
        - **description**: `Force PM boot sequence to obey Phase-25/26 rules`
      - **constraints**:
        - **reality_green_required**: `true`
        - **degraded_mode_on_mismatch**: `true`
        - **kernel_bootstrap_agreement**: `true`
    - **enabled**: `true`
    - **priority**: `0`
    - **created_at**: `2025-12-06T09:09:19.892311-08:00`
    - **updated_at**: `2025-12-06T09:09:19.892311-08:00`
- **row_count**: `43`
- **db_off**: `false`
