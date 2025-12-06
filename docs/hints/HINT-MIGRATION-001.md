# concept_correlations view not created

**Hint ID**: `HINT-MIGRATION-001`  
**Scope**: database  
**Kind**: SUGGESTED  
**Priority**: 18  

## Problem

Phase 10 expects concept_correlations view but it does not exist

## Symptom

relation concept_correlations does not exist

## Fix

Run migration: psql $GEMATRIA_DSN -f migrations/???_concept_correlations.sql

**Severity**: MEDIUM

**Code Reference**: `scripts/export_stats.py::export_correlations`

