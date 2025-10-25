-- Migration 001: Two Database Safety and Core Tables
-- Ensures safe coexistence with bible_db (read-only) and gematria (read-write)

-- Create schema for LangGraph checkpointer (optional)
CREATE SCHEMA IF NOT EXISTS langgraph;

-- Core concepts table with bible_db integration safety
CREATE TABLE IF NOT EXISTS concepts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    hebrew_text VARCHAR(255) NOT NULL, -- Consonants only
    hebrew_with_nikud VARCHAR(255), -- With vowels (optional)
    gematria_value INTEGER NOT NULL CHECK (gematria_value > 0),
    gematria_calculation TEXT NOT NULL,
    english_meaning TEXT,

    -- Book attribution
    book_id INTEGER, -- Will be populated after books table
    book_source VARCHAR(100),
    testament VARCHAR(5) CHECK (testament IN ('OT', 'NT')),

    -- Verses and context
    primary_verse TEXT NOT NULL,
    verse_references TEXT[],
    context_passage TEXT,

    -- Theological metadata
    theological_category VARCHAR(100),
    semantic_tags TEXT[],
    doctrinal_tags TEXT[],

    -- AI enrichment (populated later)
    insights TEXT,
    theological_significance TEXT,

    -- Bible integration
    strong_number VARCHAR(10), -- H0120 format
    bible_db_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    hebrew_name VARCHAR(100),
    testament VARCHAR(5) NOT NULL CHECK (testament IN ('OT', 'NT')),
    category VARCHAR(50) NOT NULL,
    book_number INTEGER NOT NULL,
    concept_count INTEGER DEFAULT 0,
    integration_status VARCHAR(20) DEFAULT 'pending',
    integration_date TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    UNIQUE(testament, book_number)
);

-- Add foreign key after books table exists
ALTER TABLE concepts ADD CONSTRAINT fk_concepts_book_id
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL;

-- Verse-noun occurrences bridge table
CREATE TABLE IF NOT EXISTS verse_noun_occurrences (
    id SERIAL PRIMARY KEY,
    concept_id INTEGER REFERENCES concepts(id),
    bible_verse_id INTEGER, -- References bible.verses.id
    bible_book_name VARCHAR(50),
    bible_chapter INTEGER,
    bible_verse_num INTEGER,
    strong_number VARCHAR(10),
    context_words TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(concept_id, bible_verse_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_concepts_gematria_value ON concepts(gematria_value);
CREATE INDEX IF NOT EXISTS idx_concepts_book_id ON concepts(book_id);
CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(name);
CREATE INDEX IF NOT EXISTS idx_concepts_strong_number ON concepts(strong_number);
CREATE INDEX IF NOT EXISTS idx_verse_occurrences_concept ON verse_noun_occurrences(concept_id);
CREATE INDEX IF NOT EXISTS idx_verse_occurrences_verse ON verse_noun_occurrences(bible_verse_id);
CREATE INDEX IF NOT EXISTS idx_books_testament ON books(testament);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);

-- Views for common queries
CREATE OR REPLACE VIEW v_concepts_with_verses AS
SELECT
    c.*,
    COUNT(vno.id) as occurrence_count,
    COALESCE(ARRAY_AGG(DISTINCT vno.bible_book_name) FILTER (WHERE vno.bible_book_name IS NOT NULL), ARRAY[]::VARCHAR[]) as books_referenced
FROM concepts c
LEFT JOIN verse_noun_occurrences vno ON c.id = vno.concept_id
GROUP BY c.id;

-- Trigger to update concept count in books
CREATE OR REPLACE FUNCTION update_book_concept_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE books
    SET concept_count = (
        SELECT COUNT(*)
        FROM concepts
        WHERE book_id = COALESCE(NEW.book_id, OLD.book_id)
    )
    WHERE id = COALESCE(NEW.book_id, OLD.book_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_concept_book_count
    AFTER INSERT OR UPDATE OR DELETE ON concepts
    FOR EACH ROW EXECUTE FUNCTION update_book_concept_count();

-- Comments for documentation
COMMENT ON TABLE concepts IS 'Core Hebrew nouns with gematria values and theological enrichment';
COMMENT ON TABLE books IS 'Biblical book metadata and integration status';
COMMENT ON TABLE verse_noun_occurrences IS 'Bridge table linking concepts to bible verses';
COMMENT ON COLUMN concepts.bible_db_verified IS 'Whether this concept has been verified against bible_db data';
COMMENT ON VIEW v_concepts_with_verses IS 'Concepts with verse occurrence summaries';
