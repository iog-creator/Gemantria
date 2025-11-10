-- Demo seed: one run with start/end + one AI interaction
INSERT INTO telemetry.metrics_log (run_id, workflow, thread_id, node, event, status, started_at, items_in, items_out)
VALUES
  ('00000000-0000-0000-0000-000000000001'::uuid, 'demo', 'thread-001', 'extract', 'node_start', 'ok', now(), 0, NULL),
  ('00000000-0000-0000-0000-000000000001'::uuid, 'demo', 'thread-001', 'extract', 'node_end', 'ok', now() + interval '1 minute', NULL, 3)
ON CONFLICT DO NOTHING;

INSERT INTO telemetry.ai_interactions (session_id, interaction_type, user_query, ai_response, tools_used, success)
VALUES ('demo-session-001', 'user_query', '{"prompt":"hello"}', '{"text":"hi"}', ARRAY['demo'], true)
ON CONFLICT DO NOTHING;
