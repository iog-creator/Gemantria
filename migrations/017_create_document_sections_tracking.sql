-- Migration: 017_create_document_sections_tracking.sql
-- Purpose: Create document sections tracking for AI-assisted document management
-- Related Rules: Rule-061 (AI Learning Tracking), Rule-058 (Auto-Housekeeping)

CREATE TABLE IF NOT EXISTS document_sections (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255) NOT NULL, -- e.g., 'GEMATRIA_MASTER_REFERENCE.md'
    section_name VARCHAR(500) NOT NULL, -- e.g., 'Database Schema & Architecture'
    section_path TEXT, -- Full path like 'docs/SSOT/GEMATRIA_MASTER_REFERENCE.md'
    section_level INTEGER NOT NULL, -- 1 for #, 2 for ##, 3 for ###, etc.
    parent_section VARCHAR(500), -- Parent section name for hierarchy
    content_hash VARCHAR(64), -- SHA-256 of section content
    word_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_name, section_name)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_document_sections_name ON document_sections (document_name);
CREATE INDEX IF NOT EXISTS idx_document_sections_path ON document_sections (section_path);
CREATE INDEX IF NOT EXISTS idx_document_sections_parent ON document_sections (parent_section);

-- Function to update document section
CREATE OR REPLACE FUNCTION update_document_section(
    p_document_name VARCHAR(255),
    p_section_name VARCHAR(500),
    p_section_path TEXT,
    p_section_level INTEGER,
    p_parent_section VARCHAR(500),
    p_content_hash VARCHAR(64),
    p_word_count INTEGER DEFAULT 0
) RETURNS VOID AS $$
BEGIN
    INSERT INTO document_sections (
        document_name, section_name, section_path, section_level,
        parent_section, content_hash, word_count, last_updated
    ) VALUES (
        p_document_name, p_section_name, p_section_path, p_section_level,
        p_parent_section, p_content_hash, p_word_count, NOW()
    )
    ON CONFLICT (document_name, section_name) DO UPDATE SET
        section_path = EXCLUDED.section_path,
        section_level = EXCLUDED.section_level,
        parent_section = EXCLUDED.parent_section,
        content_hash = EXCLUDED.content_hash,
        word_count = EXCLUDED.word_count,
        last_updated = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to get document section hierarchy
CREATE OR REPLACE FUNCTION get_document_hierarchy(doc_name VARCHAR(255))
RETURNS TABLE (
    section_name VARCHAR(500),
    section_level INTEGER,
    parent_section VARCHAR(500),
    word_count INTEGER,
    last_updated TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ds.section_name,
        ds.section_level,
        ds.parent_section,
        ds.word_count,
        ds.last_updated
    FROM document_sections ds
    WHERE ds.document_name = doc_name
    ORDER BY ds.section_level, ds.section_name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE document_sections IS 'Tracks document sections for AI-assisted document management and maintenance';
COMMENT ON FUNCTION update_document_section IS 'Updates or inserts document section tracking information';
COMMENT ON FUNCTION get_document_hierarchy IS 'Returns hierarchical view of document sections';
