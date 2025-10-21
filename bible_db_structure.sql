-- Bible Database Structure (Read-Only Reference)
-- This is a stub schema showing the structure of bible_db
-- The actual bible_db is read-only and should not be modified

-- Schema for biblical content
CREATE SCHEMA IF NOT EXISTS bible;

-- Books table (read-only)
CREATE TABLE IF NOT EXISTS bible.books (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    hebrew_name VARCHAR(100),
    greek_name VARCHAR(100),
    testament VARCHAR(5) NOT NULL CHECK (testament IN ('OT', 'NT')),
    category VARCHAR(50),
    book_number INTEGER NOT NULL,
    chapter_count INTEGER,
    verse_count INTEGER,

    UNIQUE(testament, book_number)
);

-- Verses table (read-only) - main content table
CREATE TABLE IF NOT EXISTS bible.verses (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES bible.books(id),
    book_name VARCHAR(50),
    chapter_num INTEGER NOT NULL,
    verse_num INTEGER NOT NULL,
    text TEXT NOT NULL,
    translation_source VARCHAR(20) DEFAULT 'KJV',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(book_id, chapter_num, verse_num, translation_source)
);

-- Hebrew words from OT (read-only)
CREATE TABLE IF NOT EXISTS bible.hebrew_ot_words (
    id SERIAL PRIMARY KEY,
    verse_id INTEGER REFERENCES bible.verses(id),
    word_position INTEGER NOT NULL,
    hebrew_text VARCHAR(100) NOT NULL,
    transliteration VARCHAR(100),
    strong_number VARCHAR(10),
    morphology_code VARCHAR(20),
    english_gloss VARCHAR(200),

    UNIQUE(verse_id, word_position)
);

-- Hebrew entries/lexicon (read-only)
CREATE TABLE IF NOT EXISTS bible.hebrew_entries (
    strong_number VARCHAR(10) PRIMARY KEY,
    hebrew_word VARCHAR(100) NOT NULL,
    transliteration VARCHAR(100),
    pronunciation VARCHAR(100),
    part_of_speech VARCHAR(50),
    definition TEXT,
    usage_notes TEXT
);

-- Greek words from NT (read-only)
CREATE TABLE IF NOT EXISTS bible.greek_nt_words (
    id SERIAL PRIMARY KEY,
    verse_id INTEGER REFERENCES bible.verses(id),
    word_position INTEGER NOT NULL,
    greek_text VARCHAR(100) NOT NULL,
    transliteration VARCHAR(100),
    strong_number VARCHAR(10),
    morphology_code VARCHAR(20),
    english_gloss VARCHAR(200),

    UNIQUE(verse_id, word_position)
);

-- Verse embeddings for semantic search (read-only)
CREATE TABLE IF NOT EXISTS bible.verse_embeddings (
    verse_id INTEGER PRIMARY KEY REFERENCES bible.verses(id),
    embedding VECTOR(768), -- Matches sentence-transformer dimension
    model_name VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance (read-only operations)
CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON bible.verses(book_id, chapter_num);
CREATE INDEX IF NOT EXISTS idx_verses_reference ON bible.verses(book_name, chapter_num, verse_num);
CREATE INDEX IF NOT EXISTS idx_hebrew_words_verse ON bible.hebrew_ot_words(verse_id);
CREATE INDEX IF NOT EXISTS idx_hebrew_words_strong ON bible.hebrew_ot_words(strong_number);
CREATE INDEX IF NOT EXISTS idx_hebrew_entries_strong ON bible.hebrew_entries(strong_number);
CREATE INDEX IF NOT EXISTS idx_greek_words_verse ON bible.greek_nt_words(verse_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON bible.verse_embeddings(model_name);

-- Views for common queries (read-only)
CREATE OR REPLACE VIEW bible.v_verses_with_text AS
SELECT
    v.id,
    b.name as book_name,
    b.hebrew_name,
    v.chapter_num,
    v.verse_num,
    v.text,
    v.translation_source
FROM bible.verses v
JOIN bible.books b ON v.book_id = b.id
ORDER BY b.book_number, v.chapter_num, v.verse_num;

CREATE OR REPLACE VIEW bible.v_ot_words_with_verses AS
SELECT
    w.*,
    v.book_name,
    v.chapter_num,
    v.verse_num,
    v.text as verse_text,
    e.definition,
    e.part_of_speech
FROM bible.hebrew_ot_words w
JOIN bible.verses v ON w.verse_id = v.id
LEFT JOIN bible.hebrew_entries e ON w.strong_number = e.strong_number
ORDER BY v.book_name, v.chapter_num, v.verse_num, w.word_position;

-- Comments for documentation
COMMENT ON SCHEMA bible IS 'Read-only biblical content and linguistic data';
COMMENT ON TABLE bible.verses IS 'Complete biblical text by verse (~116,566 verses)';
COMMENT ON TABLE bible.hebrew_ot_words IS 'Hebrew words from OT with linguistic analysis (~283,717 words)';
COMMENT ON TABLE bible.verse_embeddings IS '768-dimensional embeddings for semantic search';
COMMENT ON VIEW bible.v_verses_with_text IS 'Verses with book names for easy reference';
COMMENT ON VIEW bible.v_ot_words_with_verses IS 'Hebrew words with verse context and definitions';

-- Security: Ensure this database remains read-only
-- REVOKE CREATE, INSERT, UPDATE, DELETE ON SCHEMA bible FROM PUBLIC;
-- GRANT SELECT ON ALL TABLES IN SCHEMA bible TO PUBLIC;
