-- PR-004: Postgres checkpointer state table
CREATE TABLE IF NOT EXISTS checkpointer_state (
  workflow   TEXT      NOT NULL,
  thread_id  TEXT      NOT NULL,
  checkpoint_id TEXT   NOT NULL,
  parent_checkpoint_id TEXT NULL,
  checkpoint JSONB     NOT NULL,
  metadata   JSONB     NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (workflow, thread_id, checkpoint_id)
);

CREATE INDEX IF NOT EXISTS idx_checkpointer_state_workflow_thread_created
  ON checkpointer_state (workflow, thread_id, created_at DESC);

-- PR-004: Postgres checkpointer writes table for put_writes support
CREATE TABLE IF NOT EXISTS checkpointer_writes (
  workflow      TEXT      NOT NULL,
  thread_id     TEXT      NOT NULL,
  checkpoint_id TEXT      NOT NULL,
  task_id       TEXT      NOT NULL,
  idx           INT       NOT NULL,
  channel       TEXT      NOT NULL,
  value         JSONB     NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (workflow, thread_id, checkpoint_id, task_id, idx)
);
