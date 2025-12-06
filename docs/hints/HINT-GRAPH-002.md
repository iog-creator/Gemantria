# Fast-lane check blocks graph re-export

**Hint ID**: `HINT-GRAPH-002`  
**Scope**: graph_export  
**Kind**: SUGGESTED  
**Priority**: 20  

## Problem

export_graph.py detects existing graph_latest.json and skips DB rebuild

## Symptom

Script runs but graph not updated despite DB changes

## Fix

Remove or rename exports/graph_latest.json before running export

**Severity**: MEDIUM

**Code Reference**: `grep fast.lane scripts/export_graph.py`

