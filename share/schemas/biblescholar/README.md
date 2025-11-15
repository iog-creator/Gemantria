# Database Schema and Setup

This directory contains the complete database structure for the BibleScholar Project.

## 📋 Overview

The BibleScholar Project uses PostgreSQL with the pgvector extension for storing:
- **Hebrew lexicon data**: 12,743 entries with Strong's numbers and morphology
- **Greek lexicon data**: 160,185 entries with lexical analysis
- **Biblical text**: Complete verses with cross-references
- **Vector embeddings**: For semantic search capabilities

## 📁 Files

### Structure Files (Schema Only)
- `bible_db_structure.sql` - Main database schema with tables, indexes, and constraints
- `bible_db_verses_structure.sql` - Verses table structure and related components
- `bible_db_versification_structure.sql` - Versification mapping tables

### Size Information
```
bible_db_structure.sql              ~24 KB  (Schema only)
bible_db_verses_structure.sql       ~3 KB   (Verses schema)
bible_db_versification_structure.sql ~2 KB   (Mappings schema)
```

**Note**: Data files (2.7GB+) are excluded from version control for repository size management.

## 🔧 Database Setup

### Prerequisites
```bash
# Install PostgreSQL 13+ with pgvector
sudo apt-get install postgresql-13 postgresql-13-dev
git clone https://github.com/pgvector/pgvector.git
cd pgvector && make && sudo make install
```

### Initial Setup
```sql
-- Create database
CREATE DATABASE bible_db;

-- Connect to database
\c bible_db;

-- Enable pgvector extension
CREATE EXTENSION vector;

-- Run structure scripts
\i bible_db_structure.sql
\i bible_db_verses_structure.sql  
\i bible_db_versification_structure.sql
```

### Connection Configuration
```bash
# Environment variables (.env file)
DATABASE_URL=postgresql://postgres:password@localhost:5432/bible_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bible_db
DB_USER=postgres
DB_PASSWORD=password
```

## 📊 Database Schema

### Core Tables

#### `hebrew_words`
- **Purpose**: Hebrew lexicon with Strong's numbers
- **Fields**: strong_number, word, transliteration, pronunciation, definition, morphology
- **Size**: 12,743 entries
- **Indexes**: Primary key on strong_number, text search indexes

#### `greek_words`  
- **Purpose**: Greek lexicon with detailed analysis
- **Fields**: strong_number, word, transliteration, pronunciation, definition, usage
- **Size**: 160,185 entries
- **Indexes**: Primary key on strong_number, lexical indexes

#### `bible_verses`
- **Purpose**: Complete Biblical text with metadata
- **Fields**: book, chapter, verse, text, translation, cross_references
- **Indexes**: Book/chapter/verse composite index, full-text search

#### `verse_embeddings`
- **Purpose**: Vector embeddings for semantic search
- **Fields**: verse_id, embedding (vector), model_used, created_at
- **Technology**: pgvector extension for similarity search
- **Model**: BGE-M3 embeddings via LM Studio

### Supporting Tables
- `versification_mappings` - Cross-reference systems
- `translation_variants` - Multiple Bible translations
- `morphology_data` - Detailed grammatical analysis
- `cross_references` - Inter-verse relationships

## 🔍 Data Population

### Method 1: From Backup (Recommended)
```bash
# If you have access to data backup files
psql -d bible_db -f complete_data_backup.sql
```

### Method 2: ETL Pipeline
```bash
# Run the ETL scripts to populate from source data
cd ../scripts/
python populate_hebrew_lexicon.py
python populate_greek_lexicon.py
python populate_verses.py
python generate_embeddings.py
```

### Method 3: API Import
```bash
# Use the API endpoints to import data
curl -X POST http://localhost:5000/api/import/hebrew -d @hebrew_data.json
curl -X POST http://localhost:5000/api/import/greek -d @greek_data.json
```

## 📈 Performance Optimization

### Indexes Created
```sql
-- Text search indexes
CREATE INDEX idx_hebrew_words_fts ON hebrew_words USING gin(to_tsvector('english', definition));
CREATE INDEX idx_greek_words_fts ON greek_words USING gin(to_tsvector('english', definition));

-- Vector similarity indexes  
CREATE INDEX idx_verse_embeddings_vector ON verse_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Lookup indexes
CREATE INDEX idx_bible_verses_reference ON bible_verses(book, chapter, verse);
CREATE INDEX idx_hebrew_strong ON hebrew_words(strong_number);
CREATE INDEX idx_greek_strong ON greek_words(strong_number);
```

### Query Performance
- **Vector search**: ~50ms for semantic similarity
- **Text search**: ~10ms for lexicon lookups  
- **Reference lookup**: ~1ms for verse retrieval

## 🔐 Security & Access

### Database Permissions
```sql
-- Read-only user for API
CREATE USER bible_reader WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE bible_db TO bible_reader;
GRANT USAGE ON SCHEMA public TO bible_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bible_reader;

-- Application user with limited write access
CREATE USER bible_app WITH PASSWORD 'app_password';
GRANT CONNECT ON DATABASE bible_db TO bible_app;
GRANT USAGE ON SCHEMA public TO bible_app;
GRANT SELECT, INSERT, UPDATE ON specific_tables TO bible_app;
```

## 🧹 Maintenance

### Regular Tasks
```sql
-- Analyze tables for query optimization
ANALYZE hebrew_words;
ANALYZE greek_words;
ANALYZE bible_verses;
ANALYZE verse_embeddings;

-- Vacuum to reclaim space
VACUUM ANALYZE;

-- Reindex if needed
REINDEX DATABASE bible_db;
```

### Backup Strategy
```bash
# Structure only (small, fast)
pg_dump --schema-only bible_db > bible_db_structure.sql

# Data only (large, for complete backups)
pg_dump --data-only bible_db > bible_db_data.sql

# Complete backup with compression
pg_dump -Fc bible_db > bible_db_complete.backup
```

## 🔧 Development

### Schema Changes
1. Test changes on development database
2. Create migration scripts in `migrations/` directory
3. Update structure files after successful migration
4. Document changes in version control

### Adding New Tables
```sql
-- Example: Adding commentary table
CREATE TABLE commentaries (
    id SERIAL PRIMARY KEY,
    verse_id INTEGER REFERENCES bible_verses(id),
    commentary_text TEXT NOT NULL,
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add appropriate indexes
CREATE INDEX idx_commentaries_verse ON commentaries(verse_id);
```

## 📚 Resources

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **pgvector Documentation**: https://github.com/pgvector/pgvector
- **Strong's Concordance**: https://www.blueletterbible.org/lang/lexicon/
- **Biblical Text Sources**: Various public domain translations

## 🐛 Troubleshooting

### Common Issues

1. **pgvector not found**
   ```bash
   # Install pgvector extension
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Permission denied**
   ```bash
   # Check user permissions
   \du
   GRANT USAGE ON SCHEMA public TO username;
   ```

3. **Large query timeouts**
   ```sql
   -- Increase statement timeout
   SET statement_timeout = '60s';
   ```

4. **Vector similarity slow**
   ```sql
   -- Ensure vector index exists
   CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
   ON verse_embeddings USING ivfflat (embedding vector_cosine_ops);
   ```

---

**Last Updated**: 2025-06-10  
**Schema Version**: 1.0  
**PostgreSQL Version**: 13+  
**Extensions Required**: pgvector 