# concepts table lacks verse metadata

**Hint ID**: `HINT-SCHEMA-001`  
**Scope**: database  
**Kind**: REQUIRED  
**Priority**: 5  

## Problem

Code analysis suggests concepts has book/chapter/verse but it does not

## Fix

Use LEFT JOIN v_concepts_with_verses not concepts for verse data

**Severity**: CRITICAL

