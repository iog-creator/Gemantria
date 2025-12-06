"""
Control-plane widget adapters for downstream apps.

Provides hermetic, fail-closed adapters for control-plane exports:
- Graph compliance metrics
- BibleScholar reference questions/answers

See Phase-6D for integration guidance.
"""

from pmagent.control_widgets.adapter import (
    load_biblescholar_reference_widget_props,
    load_graph_compliance_widget_props,
    load_mcp_status_cards_widget_props,
)

__all__ = [
    "load_biblescholar_reference_widget_props",
    "load_graph_compliance_widget_props",
    "load_mcp_status_cards_widget_props",
]
