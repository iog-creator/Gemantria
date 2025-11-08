-- Migration: Create ai_policy_view for Always-Apply policy triad
-- Ensures automation guards can fetch the authoritative Always-Apply set from Postgres.

CREATE OR REPLACE VIEW ai_policy_view AS
SELECT '050,051,052'::text AS triad;

