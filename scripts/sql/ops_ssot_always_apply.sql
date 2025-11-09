-- Minimal SSOT view for Always-Apply triad (adjust array if policy changes)
-- This view serves as the single source of truth for which rules are Always-Apply.
-- The sync_alwaysapply_from_db.py script reads from this view to update documentation.

create or replace view ops_ssot_always_apply as
select unnest(array[50,51,52])::int as rule_id, true as active;

