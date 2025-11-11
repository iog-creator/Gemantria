-- P0 control-plane primitives for Guarded Tool Calls

CREATE TABLE IF NOT EXISTS tool_catalog (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  version TEXT NOT NULL,
  io_schema_json JSONB NOT NULL,
  exec_kind TEXT NOT NULL,     -- "python_fn"|"cli"|"http_local"
  entrypoint TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS capability_rule (
  id SERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL,
  predicate_json JSONB NOT NULL,
  allow_tool_ids INT[] NOT NULL
);

CREATE TABLE IF NOT EXISTS doc_fragment (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL,
  uri TEXT NOT NULL,
  anchor TEXT NOT NULL,
  sha256 CHAR(64) NOT NULL,
  required_for JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS capability_session (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL,
  task_id UUID NOT NULL UNIQUE,
  allowed_tool_ids INT[] NOT NULL,
  checklist_json JSONB NOT NULL,
  por_status JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_run (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL,
  task_id UUID NOT NULL,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  success BOOLEAN,
  quarantined BOOLEAN DEFAULT false,
  result_json JSONB,
  evidence_uri TEXT,
  violations_json JSONB DEFAULT '[]'::jsonb
);

-- Optional Tool Bus queue (OFF by default; used when enabled)
CREATE TABLE IF NOT EXISTS agent_queue (
  id BIGSERIAL PRIMARY KEY,
  task_id UUID NOT NULL,
  call_json JSONB NOT NULL,
  enqueued_at TIMESTAMPTZ DEFAULT now(),
  state TEXT NOT NULL DEFAULT 'queued', -- queued|running|done|error
  error_msg TEXT
);

-- Scorecard MVs (7d/30d)
DROP MATERIALIZED VIEW IF EXISTS mv_compliance_7d;
CREATE MATERIALIZED VIEW mv_compliance_7d AS
SELECT
  project_id,
  count(*) AS runs,
  avg((result_json->>'schema_ok')::bool::int)        AS schema_ok_rate,
  avg((result_json->>'por_ok')::bool::int)           AS por_ok_rate,
  avg((result_json->>'provenance_ok')::bool::int)    AS provenance_ok_rate,
  avg((success)::int)                                 AS success_rate,
  sum(jsonb_array_length(violations_json))            AS violations,
  avg(CASE WHEN (result_json ? 'retry_count')
           THEN LEAST((result_json->>'retry_count')::int,1)
           ELSE 0 END)                                AS retry_rate
FROM agent_run
WHERE started_at >= now() - interval '7 days'
GROUP BY project_id;

DROP MATERIALIZED VIEW IF EXISTS mv_compliance_30d;
CREATE MATERIALIZED VIEW mv_compliance_30d AS
SELECT
  project_id,
  count(*) AS runs,
  avg((result_json->>'schema_ok')::bool::int)        AS schema_ok_rate,
  avg((result_json->>'por_ok')::bool::int)           AS por_ok_rate,
  avg((result_json->>'provenance_ok')::bool::int)    AS provenance_ok_rate,
  avg((success)::int)                                 AS success_rate,
  sum(jsonb_array_length(violations_json))            AS violations,
  avg(CASE WHEN (result_json ? 'retry_count')
           THEN LEAST((result_json->>'retry_count')::int,1)
           ELSE 0 END)                                AS retry_rate
FROM agent_run
WHERE started_at >= now() - interval '30 days'
GROUP BY project_id;
