-- Ensure restricted RW role can create objects and write rows (least-privilege) — idempotent

DO $$
DECLARE r text := coalesce(current_setting('gemantria.rw_user', true), 'gemantria_rw');
BEGIN
  EXECUTE format('GRANT USAGE, CREATE ON SCHEMA gematria, telemetry, ops TO %I;', r);
  EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA gematria TO %I;', r);
  EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA telemetry TO %I;', r);
  EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA gematria  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO %I;', r);
  EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA telemetry GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO %I;', r);
END $$;

