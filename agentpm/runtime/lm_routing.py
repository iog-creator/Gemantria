#!/usr/bin/env python3
"""
LM Routing Helper

Phase-3C P0: Config-based backend selection (lm_studio vs remote).
Pure Python helper; no network calls.
"""

from __future__ import annotations

from scripts.config.env import get_lm_studio_settings


def select_lm_backend(prefer_local: bool = True) -> str:
    """
    Decide whether to use 'lm_studio' or 'remote' backend.

    P0: purely config-based; no live ping.
    Future: may consider pmagent health lm output or cached health probe.

    Args:
        prefer_local: If True, prefer LM Studio when enabled (default: True).

    Returns:
        "lm_studio" if LM Studio is enabled and prefer_local is True, else "remote".
    """
    settings = get_lm_studio_settings()

    if prefer_local and settings["enabled"]:
        return "lm_studio"

    return "remote"
