"""
Knowledge-Base Document Registry (KB-Reg:M1)

Registry for tracking KB documents (AGENTS.md, SSOT docs, rules, etc.) with
metadata including id/handle, title, path/URI, type, tags, owning subsystem,
and provenance.

SSOT: Registry entries live in share/kb_registry.json (read-only in CI per Rule-044).
"""

from __future__ import annotations

from agentpm.kb.classify import classify_fragment
from agentpm.kb.registry import (
    KBDocument,
    KBDocumentRegistry,
    analyze_freshness,
    load_registry,
    save_registry,
    validate_registry,
)

__all__ = [
    "KBDocument",
    "KBDocumentRegistry",
    "analyze_freshness",
    "classify_fragment",
    "load_registry",
    "save_registry",
    "validate_registry",
]
