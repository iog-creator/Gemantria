# UUID joins require ::text casting

**Hint ID**: `HINT-SCHEMA-003`  
**Scope**: database  
**Kind**: REQUIRED  
**Priority**: 8  

## Problem

concept_id is UUID, joining to text fields fails without cast

## Symptom

ERROR: operator does not exist: uuid = text

**Severity**: HIGH

