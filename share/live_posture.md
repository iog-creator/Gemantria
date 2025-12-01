# live_posture

**Generated**: 2025-12-01T16:09:43.881667+00:00
**Source**: `live_posture.json`

---

- **schema**: `live_posture.v1`
- **generated_at**: `2025-12-01T16:09:33.875450+00:00`
- **db**:
  - **mode**: `ready`
  - **ok**: `true`
  - **dsn_rw**: `postgresql://<REDACTED>/gematria`
  - **dsn_ro**: `postgresql://<REDACTED>/gematria`
  - **dsn_bible**: `postgresql://<REDACTED>/bible_db`
- **lm**:
  - **slots**:
    1. Item:
      - **name**: `local_agent`
      - **provider**: `lmstudio`
      - **model**: `ibm/granite-4-h-tiny`
      - **service**: `OK`
    2. Item:
      - **name**: `embedding`
      - **provider**: `lmstudio`
      - **model**: `text-embedding-bge-m3`
      - **service**: `OK`
    3. Item:
      - **name**: `reranker`
      - **provider**: `lmstudio`
      - **model**: `ibm/granite-4-h-tiny (embedding_only)`
      - **service**: `OK`
    4. Item:
      - **name**: `theology`
      - **provider**: `lmstudio`
      - **model**: `christian-bible-expert-v2.0-12b`
      - **service**: `OK`
  - **model_availability**:
    - **local_agent**:
      - **provider**: `lmstudio`
      - **model**: `ibm/granite-4-h-tiny`
      - **available**: `true`
    - **embedding**:
      - **provider**: `lmstudio`
      - **model**: `text-embedding-bge-m3`
      - **available**: `true`
    - **reranker**:
      - **provider**: `lmstudio`
      - **model**: `ibm/granite-4-h-tiny (embedding_only)`
      - **available**: `true`
    - **theology**:
      - **provider**: `lmstudio`
      - **model**: `christian-bible-expert-v2.0-12b`
      - **available**: `true`
  - **qwen_available**: `false`
  - **granite_available**: `true`
- **checkpointer**: `memory`
- **enforce_strict**: ``
- **db_off**: `false`
