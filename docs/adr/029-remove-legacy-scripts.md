# ADR-029: Remove legacy offline scripts in favor of LangGraph orchestrator

Context: Legacy one-off scripts duplicate agentic pipeline behavior and confuse Cursor.

Decision: Deprecate and remove scripts that bypass SSOT envelopes and guards.

List: scripts/build_graph_from_ai_nouns.py,
      scripts/eval/apply_rerank_blend.py,
      scripts/eval/apply_rerank_refresh.py

Consequences: Enforce pipeline-only via Make targets; add stub guards to fail-fast if invoked.

Verification: ruff checks pass; make ai.nouns→guards.all green; CI runs hermetically.
