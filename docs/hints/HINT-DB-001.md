# Missing DSN is fatal error

**Hint ID**: `HINT-DB-001`  
**Scope**: database  
**Kind**: REQUIRED  
**Priority**: 5  

## Problem

Agent accepted missing GEMATRIA_DSN/BIBLE_DB_DSN as warning instead of blocking

## Fix

1. STOP immediately if DSN missing
2. Add to .env: GEMATRIA_DSN=postgresql://mccoy@/gematria?host=/var/run/postgresql
3. Verify: psql $GEMATRIA_DSN -c SELECT current_database();

**Severity**: CRITICAL

