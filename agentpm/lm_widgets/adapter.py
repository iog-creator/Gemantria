"""
Stub for Phase-5 LM Indicator Widget adapter.

Cursor will implement the full logic in PR #2.
"""

from __future__ import annotations

import json

from pathlib import Path

INDICATOR_PATH = Path("share/atlas/control_plane/lm_indicator.json")


def load_lm_indicator_widget_props():
    """
    Placeholder. Cursor will fill in full hermetic + fail-closed logic.

    Returns a dict matching LM_WIDGETS.md contract.
    """
    try:
        raw = json.loads(INDICATOR_PATH.read_text())
        return {"_stub": True, "indicator_raw": raw}
    except Exception:
        return {"_stub": True, "offline_safe": True}
