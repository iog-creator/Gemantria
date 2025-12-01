# hint_registry

**Generated**: 2025-12-01T16:09:43.847929+00:00
**Source**: `hint_registry.json`

---

- **schema**: `control.hint_registry.v1`
- **generated_at**: `2025-12-01T16:09:32.398097+00:00`
- **table**: `control.hint_registry`
- **rows**:
  1. Item:
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
    - **updated_at**: `2025-11-29T07:41:52.592675-08:00`
  2. Item:
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
    - **updated_at**: `2025-11-29T07:41:52.592675-08:00`
  3. Item:
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
    - **updated_at**: `2025-11-29T07:41:52.592675-08:00`
  4. Item:
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
    - **updated_at**: `2025-11-29T07:41:52.592675-08:00`
  5. Item:
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
    - **updated_at**: `2025-11-29T07:41:52.592675-08:00`
- **row_count**: `5`
- **db_off**: `false`
