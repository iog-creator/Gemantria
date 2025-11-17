# Doc Content + pgvector Ingestion Plan — Governance/Docs RAG

## 0. Context

We now have:

- **Rules DB SSOT**:

  - `control.rule_definition`, `control.rule_source`

  - `scripts/governance/ingest_rules_to_db.py`

  - `scripts/guards/guard_rules_db_ssot.py`

- **Doc Registry SSOT**:

  - `control.doc_registry`, `control.doc_version`, `control.doc_sync_state`

  - `scripts/governance/ingest_docs_to_db.py`

  - `scripts/guards/guard_docs_db_ssot.py`

  - `scripts/sync_share.py` using the registry when DB is on

- **DB-on verification (OPS-015)**:

  - Migrations applied

  - Ingestions run (rules + docs)

  - Guards in READY mode

  - share.sync working (registry-ready, manifest fallback)

Next step: make **full documentation content** and **embeddings** a first-class part

of the control-plane so governance/runbook docs are directly queryable via RAG

from Postgres + pgvector.

---

## 1. Goals

1. **Store full doc contents (or chunks) in Postgres**

   - Derive from repo files tracked in `control.doc_registry`.

   - Maintain provenance: which version (hash/commit) each chunk came from.

2. **Add pgvector embeddings for those chunks**

   - Use the configured embedding model (Phase-7 LM/embedding config).

   - Store vectors in Postgres (pgvector) for RAG queries.

3. **Make governance/docs RAG-ready**

   - Ability to answer:

     - "What do the runbooks say about X?"

     - "Show me relevant governance rules + docs for this question."

4. **Preserve DSN + guard patterns**

   - Use centralized loaders (`get_control_engine`, etc.).

   - Keep DB-off tolerance in scripts, but allow STRICT runs (like OPS-015).

---

## 2. Existing Building Blocks

### 2.1 Registry spine

- `control.doc_registry` → which docs exist, logical names, repo paths.

- `control.doc_version` → hashes + size + (optional) git commit.

- `control.doc_sync_state` → used by sync_share (share is derived).

### 2.2 Fragment model (candidate)

We already have `control.doc_fragment` (or a similar table) used for

proof-of-rewrite (PoR) / fragments in other parts of the system. This can be:

- **Reused** for governance/docs content, OR

- **Wrapped** with an additional table keyed by `doc_id` from `control.doc_registry`.

We need to choose one canonical pattern and avoid duplicating fragment logic.

### 2.3 LM / embedding config (Phase-7)

- Phase-7 defined local LM + embedding slots.

- We will reuse the **embedding slot** and env vars so the content-embedding

  pipeline uses the same model selection contract as the rest of the system.

---

## 3. Proposed Schema Extensions (Phase-8C)

### 3.1 `control.doc_fragment` (normalize & extend)

If an existing table already exists, we **extend** it; otherwise we create it.

**Columns (target shape):**

- `id` (BIGSERIAL, PK)

- `doc_id` (UUID, FK → control.doc_registry.doc_id)

- `version_id` (BIGINT, FK → control.doc_version.id, optional)

- `fragment_index` (INT) — order within the doc

- `fragment_type` (TEXT) — e.g. "paragraph", "heading", "code", "meta"

- `content` (TEXT) — actual text of the fragment

- `created_at` (TIMESTAMPTZ)

- `updated_at` (TIMESTAMPTZ)

**Notes:**

- `doc_id` ties fragment back to registry (logical_name, paths).

- `version_id` lets us track which version hash produced these fragments.

- `fragment_index` preserves ordering for reconstruction if needed.

### 3.2 `control.doc_embedding` (pgvector)

Add a dedicated embeddings table keyed to fragments.

```sql

CREATE TABLE control.doc_embedding (

    id              BIGSERIAL PRIMARY KEY,

    fragment_id     BIGINT NOT NULL REFERENCES control.doc_fragment(id) ON DELETE CASCADE,

    model_name      TEXT NOT NULL,

    embedding       vector(1024) NOT NULL,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

```

**Considerations:**

* `vector(1024)` matches the embedding dimension we use elsewhere (Phase-7/LM plan).

* We may add `norm`/`metadata` columns later if needed.

---

## 4. Ingestion Pipelines

### 4.1 Content ingestion (registry → fragments)

**Script (planned):** `scripts/governance/ingest_doc_content.py`

**Responsibilities:**

1. Query `control.doc_registry` + `control.doc_version` to find:

   * Enabled docs (`is_ssot = TRUE`, `enabled = TRUE`).

   * Their latest version hashes (most recent `doc_version` per `doc_id`).

2. For each doc/version:

   * Read file from repo path (relative to `REPO_ROOT`).

   * Normalize:

     * Strip BOM, normalize newlines.

     * Chunk into fragments:

       * Default: line/paragraph-based splitting.

       * Preserve headings (e.g. `#`, `##`) and code fences separately.

3. Upsert into `control.doc_fragment`:

   * Delete or mark obsolete fragments for a given `(doc_id, version_id)` before inserting new ones.

   * Insert new fragments with `fragment_index` and `fragment_type`.

4. DB-off behavior:

   * If DB is unavailable: exit with clear error (for STRICT runs).

   * A separate `--dry-run` mode may log chunking only.

### 4.2 Embedding ingestion (fragments → pgvector)

**Script (planned):** `scripts/governance/ingest_doc_embeddings.py`

**Responsibilities:**

1. Query `control.doc_fragment` for:

   * Fragments that do **not yet** have an embedding row for the target model.

   * Use a `LEFT JOIN`/NOT EXISTS pattern on `control.doc_embedding`.

2. For each batch:

   * Call the configured embedding model via the centralized LM/embedding interface.

   * Store embeddings in `control.doc_embedding`.

3. Configuration:

   * Env var for embedding model (e.g. `DOC_EMBED_MODEL` or reuse `EMBEDDING_MODEL`).

   * Batch size, rate limits, etc.

4. DB/LMM-off behavior:

   * In HINT mode, can be tolerant (skip if LM is off).

   * In STRICT mode, governance docs should have embeddings, so we can fail if

     a minimal set of core docs isn't embedded.

---

## 5. Guards & CI

### 5.1 Fragment coverage guard

**File (planned):** `scripts/guards/guard_doc_fragments.py`

Checks:

* For all docs with `is_ssot = TRUE` and `enabled = TRUE`:

  * There is at least one `control.doc_fragment` row.

* Reports:

  * Number of docs missing fragments.

  * Total fragment count.

### 5.2 Embedding coverage guard

**File (planned):** `scripts/guards/guard_doc_embeddings.py`

Checks:

* For all core docs (AGENTS, MASTER_PLAN, RULES_INDEX, core SSOT docs):

  * Each fragment has at least one embedding row for the target model.

* Reports:

  * Missing embedding counts.

These can be HINT on PRs and STRICT on tags / "reality check" runs.

---

## 6. Query Surfaces (Phase-8D) ✅ IMPLEMENTED

Once content + embeddings exist:

* ✅ Helper functions / views:

  * `control.v_doc_fragments` — join registry + fragments.

  * `control.v_doc_embeddings` — join fragments + embeddings.

* ✅ CLI command:

  * `pmagent docs.search` — CLI command for governance/docs queries (Phase-8C.4).

* ✅ API + UI (Phase-8D):

  * `GET /api/docs/search` — REST API endpoint for semantic search over governance/docs.

  * `GET /governance-search` — HTML page with search interface (Atlas-integrated).

  * Atlas integration: "Governance Search" link added to `docs/atlas/index.html`.

  * See `docs/SSOT/ATLAS_GOVERNANCE_SEARCH_PANEL.md` for full specification.

---

## 7. Phasing

### Phase-8C.1 — Schema migrations

* Add/extend `control.doc_fragment`.

* Add `control.doc_embedding` with pgvector.

### Phase-8C.2 — Content ingestion ✅ IMPLEMENTED

* ✅ Implemented `ingest_doc_content.py`.

* ✅ Added Makefile targets:

  * `governance.ingest.doc_content`

  * `governance.ingest.doc_content.dryrun`

* ✅ Guard: `guard_doc_fragments.py` validates Tier-0 AGENTS docs have fragments.

### Phase-8C.3 — Embedding ingestion ✅ IMPLEMENTED (DB+LM READY)

* ✅ Implemented `ingest_doc_embeddings.py`.

* ✅ Added Makefile targets:

  * `governance.ingest.doc_embeddings`

  * `governance.ingest.doc_embeddings.dryrun`

* ✅ Guard: `guard_doc_embeddings.py` validates Tier-0 AGENTS docs have embeddings.

* ✅ All 75 AGENTS docs (2,963 fragments) embedded and RAG-ready (OPS-021 complete).

### Phase-8C.4 — STRICT posture + pmagent search ✅ IMPLEMENTED

* ✅ Guards wired into `ops.tagproof` STRICT lane:

  * `guard_doc_fragments.py` (STRICT_MODE=STRICT)

  * `guard_doc_embeddings.py` (STRICT_MODE=STRICT)

* ✅ CI integration:

  * HINT on PRs (via `ci.guards.doc_vectors`).

  * STRICT on tags (via `ops.tagproof`).

* ✅ `pmagent docs.search` CLI command:

  * Semantic search over control-plane embeddings.

  * Queries `control.doc_embedding` + `control.doc_fragment` + `control.doc_registry`.

  * Returns top-k fragments with provenance (logical_name, score, snippet).

  * Usage: `pmagent docs.search "query text" --k 10 [--tier0-only/--all] [--json-only]`.

* ✅ Tier-0 enforcement:

  * In STRICT mode, Tier-0 docs (AGENTS_ROOT + AGENTS::*) must have:

    * Registry + versions (guard_docs_db_ssot)

    * Fragments (guard_doc_fragments)

    * Embeddings (guard_doc_embeddings)

  * All three guards must pass for Phase-8C to be considered complete.

---

## 8. Principle

> Registry (metadata) → Content (fragments) → Embeddings (pgvector) → RAG

* **Registry** says *what* docs exist and where.

* **Fragments** store *what they say* (normalized content).

* **Embeddings** make them *searchable* and *answerable*.

---

## AGENTS Framework as Core Content

The AGENTS.md framework is **Tier-0** for content and embeddings:

- Root `AGENTS.md` and all module-level AGENTS docs define:

  - Agent purposes

  - Invariants and safety rules

  - Directory/module responsibilities

Content ingestion requirements:

- All `AGENTS*.md` docs tracked in `control.doc_registry` MUST be fragmented into

  `control.doc_fragment` entries.

- In STRICT posture:

  - It is an error for an AGENTS doc to have zero fragments.

Embedding requirements:

- For the configured governance/docs embedding model:

  - All fragments belonging to AGENTS docs MUST have embeddings in

    `control.doc_embedding`.

- Guards (`guard_doc_fragments.py`, `guard_doc_embeddings.py`) will treat missing

  AGENTS coverage as Tier-0 failures in STRICT DB-on runs.

