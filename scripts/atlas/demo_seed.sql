-- Dev-only seed for Atlas visual proof (read-only views)
-- Safe to run multiple times.

CREATE TABLE IF NOT EXISTS public.metrics_log (
  run_id TEXT,
  node TEXT,
  status TEXT,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  items_in INT,
  items_out INT,
  error TEXT
);

CREATE TABLE IF NOT EXISTS public.checkpointer_state (
  pipeline_id TEXT,
  step TEXT,
  ts TIMESTAMPTZ
);

-- Trim prior demo rows (idempotent demo namespace)
DELETE FROM public.metrics_log WHERE run_id LIKE 'demo-%';
DELETE FROM public.checkpointer_state WHERE pipeline_id LIKE 'demo-%';

-- Minimal telemetry (2 nodes, 1 recent run, 1 historical run)
INSERT INTO public.metrics_log(run_id,node,status,started_at,ended_at,items_in,items_out,error) VALUES
('demo-run-now','extract','ok', now() - interval '2 minutes', now() - interval '1 minutes', 120, 118, NULL),
('demo-run-now','transform','ok', now() - interval '60 seconds', now() - interval '5 seconds', 118, 118, NULL),
('demo-run-hist','extract','ok', now() - interval '2 days', now() - interval '2 days' + interval '2 minutes', 90, 90, NULL),
('demo-run-hist','transform','ok', now() - interval '2 days' + interval '2 minutes', now() - interval '2 days' + interval '3 minutes', 90, 89, NULL);

INSERT INTO public.checkpointer_state(pipeline_id,step,ts) VALUES
('demo-pipeline','transform', now()),
('demo-pipeline','extract',   now() - interval '2 minutes');

