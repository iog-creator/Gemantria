# ai_nouns.json silently overrides DB nodes

**Hint ID**: `HINT-GRAPH-001`  
**Scope**: graph_export  
**Kind**: REQUIRED  
**Priority**: 10  

## Problem

export_graph.py prioritizes ai_nouns.json over database, causing 1-node graphs if file is stale

## Symptom

graph_latest.json has 1 node despite DB having 1000s

## Fix

Check exports/ai_nouns.json - if stale/test data, rename to .bak to force DB fallback

**Severity**: HIGH

**Code Reference**: `scripts/export_graph.py:262-273`

