# Recover Missing Greek Data for Mark 1:1-3

**Purpose**: Fix critical data gap in `bible_db` where Greek New Testament words for Mark 1:1-3 are missing, blocking Phase 14 PR 14.3 verification.

## Problem

- **Missing Data**: `bible.greek_nt_words` table lacks entries for Mark 1:1-3
- **Blocking**: Phase 14 PR 14.3 verification cannot proceed
- **Connection Issue**: Cannot connect to PostgreSQL at localhost:5432 (password authentication failed)

## Solution Overview

1. **Diagnose Connection**: Use diagnostic script to identify working connection method
2. **Recover Data**: Extract missing Greek words from existing database
3. **Populate Data**: Insert recovered words into `bible.greek_nt_words` table
4. **Verify**: Confirm data is present and Phase 14 verification can proceed

## Step-by-Step Recovery Process

### Step 1: Diagnose Database Connection

Run the diagnostic script to identify connection issues:

```bash
cd /home/mccoy/Projects/Gemantria.v2
python scripts/db/diagnose_bible_db_connection.py
```

This script will:
- Check DSN configuration from `.env`
- Test multiple connection methods (Unix socket, TCP with different users)
- Check PostgreSQL service status
- Provide recommendations for fixing connection issues

**Common Issues & Solutions**:

1. **Unix Socket Authentication** (from `.env`):
   ```bash
   # .env uses: postgresql://mccoy@/bible_db?host=/var/run/postgresql
   # This requires peer authentication (no password)
   # Check: /etc/postgresql/*/main/pg_hba.conf
   ```

2. **Password Authentication**:
   ```bash
   # If using TCP with password:
   # Reset postgres password:
   sudo -u postgres psql
   ALTER USER postgres PASSWORD 'your_password';
   ```

3. **PostgreSQL Not Running**:
   ```bash
   sudo systemctl status postgresql
   sudo systemctl start postgresql
   ```

### Step 2: Recover Missing Data

Once connection is working, run the recovery script:

```bash
python scripts/db/recover_mark_greek_words.py
```

This script will:
1. Connect to the database (tries multiple methods automatically)
2. Extract Greek words for Mark 1:1-3 from existing data
3. Populate missing entries in `bible.greek_nt_words` table
4. Report statistics (inserted, skipped, errors)

**Expected Output**:
```
Step 1: Connecting to database...
✓ Connected successfully!

Step 2: Extracting Greek words for Mark 1:1-3...
Found 3 verse(s) for Mark 1:1-3
  Mark 1:1 - Found 8 Greek word(s)
  Mark 1:2 - Found 12 Greek word(s)
  Mark 1:3 - Found 10 Greek word(s)
Extracted 30 Greek word(s)

Step 3: Populating target database...
  Inserted word_id=12345 for Mark 1:1 position=1
  ...

Results:
  Total words: 30
  Inserted: 30
  Skipped (already exist): 0
  Errors: 0

✓ Successfully populated missing Greek words!
```

### Step 3: Verify Data

Verify the data was inserted correctly:

```sql
-- Check verses exist
SELECT verse_id, book_name, chapter_num, verse_num, translation_source
FROM bible.verses
WHERE book_name = 'Mark'
  AND chapter_num = 1
  AND verse_num BETWEEN 1 AND 3
ORDER BY verse_num;

-- Check Greek words exist
SELECT w.word_id, w.verse_id, w.word_position, w.word_text, w.strongs_id,
       v.book_name, v.chapter_num, v.verse_num
FROM bible.greek_nt_words w
JOIN bible.verses v ON w.verse_id = v.verse_id
WHERE v.book_name = 'Mark'
  AND v.chapter_num = 1
  AND v.verse_num BETWEEN 1 AND 3
ORDER BY v.verse_num, w.word_position;
```

### Step 4: Test Phase 14 PR 14.3

After data is recovered, verify Phase 14 functionality:

```bash
# Run Phase 14 tests
python -m pytest agentpm/biblescholar/tests/test_cross_language.py -v

# Or test manually
python -c "
from agentpm.biblescholar.cross_language_flow import analyze_word_in_context
result = analyze_word_in_context('Mark 1:1', 'G2316')
print(result)
"
```

## Alternative: Access Legacy BibleScholarProjectClean Database

If the current database doesn't have the data, try accessing the legacy project:

### Location
- **Legacy Project**: `/home/mccoy/Projects/BibleScholarProjectClean`
- **Database**: Same `bible_db` database (may be on different host/port)

### Steps

1. **Check Legacy Project Configuration**:
   ```bash
   cd /home/mccoy/Projects/BibleScholarProjectClean
   cat .env  # or .env.example
   # Look for database connection details
   ```

2. **Connect to Legacy Database**:
   ```bash
   # If different DSN, update recovery script or use psql directly
   psql -U postgres -d bible_db -h localhost
   # or
   psql -U mccoy -d bible_db -h /var/run/postgresql
   ```

3. **Export Data from Legacy**:
   ```sql
   -- Export Greek words for Mark 1:1-3
   COPY (
     SELECT w.*, v.book_name, v.chapter_num, v.verse_num
     FROM bible.greek_nt_words w
     JOIN bible.verses v ON w.verse_id = v.verse_id
     WHERE v.book_name = 'Mark'
       AND v.chapter_num = 1
       AND v.verse_num BETWEEN 1 AND 3
   ) TO '/tmp/mark_1_1_3_greek_words.csv' WITH CSV HEADER;
   ```

4. **Import into Current Database**:
   ```sql
   -- Import into current database
   COPY bible.greek_nt_words (verse_id, word_position, word_text, strongs_id, grammar_code, transliteration, gloss, theological_term)
   FROM '/tmp/mark_1_1_3_greek_words.csv' WITH CSV HEADER;
   ```

## Troubleshooting

### Connection Issues

**Problem**: `FATAL: password authentication failed`

**Solutions**:
1. Check PostgreSQL authentication method in `/etc/postgresql/*/main/pg_hba.conf`
2. Try Unix socket connection (no password): `postgresql://mccoy@/bible_db?host=/var/run/postgresql`
3. Reset password: `ALTER USER postgres PASSWORD 'new_password';`
4. Use peer authentication (if user matches system user)

**Problem**: `Connection refused` or `could not connect to server`

**Solutions**:
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Check port: `sudo netstat -tlnp | grep 5432`
3. Check firewall: `sudo ufw status`
4. Check PostgreSQL listen address in `postgresql.conf`

### Data Issues

**Problem**: No Greek words found in source database

**Solutions**:
1. Check if verses exist: `SELECT * FROM bible.verses WHERE book_name='Mark' AND chapter_num=1`
2. Check translation source: Try both 'TAGNT' and 'KJV'
3. Check if data exists in legacy project database
4. Look for backup files or source data files

**Problem**: Words already exist but verification still fails

**Solutions**:
1. Check verse_id mapping (may be different between databases)
2. Verify translation_source matches ('TAGNT' vs 'KJV')
3. Check word_position values are correct
4. Verify foreign key constraints are satisfied

## Related Files

- **Diagnostic Script**: `scripts/db/diagnose_bible_db_connection.py`
- **Recovery Script**: `scripts/db/recover_mark_greek_words.py`
- **Test Script**: `test_db_connect.py` (legacy test file)
- **Database Adapter**: `agentpm/biblescholar/bible_db_adapter.py`
- **Cross-Language Flow**: `agentpm/biblescholar/cross_language_flow.py`

## References

- **Schema Documentation**: `schemas/biblescholar/README.md`
- **Migration Plan**: `docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md`
- **BibleScholar Intake**: `docs/SSOT/BIBLESCHOLAR_INTAKE.md`
- **Database Structure**: `bible_db_structure.sql`

## Next Steps After Recovery

1. ✅ Verify data is present in `bible.greek_nt_words`
2. ✅ Run Phase 14 PR 14.3 verification tests
3. ✅ Document any remaining data gaps
4. ✅ Consider automated data validation to prevent future gaps
5. ✅ Update documentation if data source changes

---

**Last Updated**: 2025-01-XX  
**Status**: Active Recovery Process  
**Blocking**: Phase 14 PR 14.3 Verification

