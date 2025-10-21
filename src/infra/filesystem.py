"""Filesystem utilities."""

from __future__ import annotations

from pathlib import Path


def read_text(path: Path) -> str:
    """Return the text content from ``path``.

    The helper enforces that bootstrap fixtures are never empty which avoids flaky tests later
    in the project.
    """

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        msg = f"File at {path} is empty."
        raise ValueError(msg)
    return text
