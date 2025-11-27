-- Phase 12: Advanced Pattern Mining Schema
-- Creates tables for storing discovered patterns and their occurrences.

BEGIN;

-- 1. Patterns Table
-- Stores the definition of a pattern (motif, sequence, etc.)
CREATE TABLE IF NOT EXISTS public.patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- e.g., 'motif', 'sequence', 'clique'
    definition JSONB NOT NULL, -- Structural definition
    metadata JSONB DEFAULT '{}'::jsonb, -- Algorithm used, params, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT patterns_name_key UNIQUE (name)
);

-- 2. Pattern Occurrences Table
-- Stores specific instances of a pattern found in the graph
CREATE TABLE IF NOT EXISTS public.pattern_occurrences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID NOT NULL REFERENCES public.patterns(id) ON DELETE CASCADE,
    nodes JSONB NOT NULL, -- List of node IDs in this occurrence
    edges JSONB DEFAULT '[]'::jsonb, -- List of edge IDs in this occurrence
    score FLOAT DEFAULT 0.0, -- Relevance/strength score
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Index for fast lookups by pattern
    CONSTRAINT fk_pattern FOREIGN KEY (pattern_id) REFERENCES public.patterns(id)
);

CREATE INDEX IF NOT EXISTS idx_pattern_occurrences_pattern_id ON public.pattern_occurrences(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_occurrences_score ON public.pattern_occurrences(score DESC);

-- 3. Grant permissions (if needed, assuming public schema is accessible)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.patterns TO public;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pattern_occurrences TO public;

COMMIT;
