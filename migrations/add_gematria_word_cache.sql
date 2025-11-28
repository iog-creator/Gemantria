-- Phase 14, PR 14.2: Gematria Word Cache
--
-- Create gematria.word_cache table in writable gemantria database
-- for performance caching of calculated gematria values.
--
-- Governance Mandate 1: Cache MUST reside in gemantria DB (writable),
-- NOT in bible_db (read-only).
--
-- Corrections applied per PM review:
-- - Fixed strongs_id typo (was "strong sid")
-- - Added CREATE SCHEMA IF NOT EXISTS
-- - Limited initial systems to: mispar_hechrachi, mispar_gadol, isopsephy

CREATE SCHEMA IF NOT EXISTS gematria;

CREATE TABLE IF NOT EXISTS gematria.word_cache (
    cache_id         BIGSERIAL PRIMARY KEY,
    language         TEXT NOT NULL CHECK (language IN ('HE', 'GR')),
    strongs_id       TEXT NOT NULL,
    surface_form     TEXT NOT NULL,
    system           TEXT NOT NULL CHECK (
        system IN ('mispar_hechrachi', 'mispar_gadol', 'isopsephy')
    ),
    gematria_value   INTEGER NOT NULL CHECK (gematria_value >= 0),
    calc_version     TEXT NOT NULL DEFAULT 'v1.0',
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (language, strongs_id, surface_form, system)
);

CREATE INDEX IF NOT EXISTS idx_gematria_cache_lookup
ON gematria.word_cache(language, strongs_id, system);

COMMENT ON TABLE gematria.word_cache IS 'Phase 14 PR 14.2: Gematria value cache for performance';
COMMENT ON COLUMN gematria.word_cache.calc_version IS 'Algorithm version for auditability';
