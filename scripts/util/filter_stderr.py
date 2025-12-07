#!/usr/bin/env python3
"""
filter_stderr.py — Filter Cursor IDE integration noise from stderr.

Filters the 'dump_bash_state: command not found' error that comes from
Cursor's shell wrapper. This error is harmless but clutters output.

Usage:
    from scripts.util.filter_stderr import filter_cursor_noise, run_filtered

    # Filter existing stderr
    stderr_filtered = filter_cursor_noise(result.stderr)

    # Or use wrapper for subprocess.run
    result = run_filtered(["command", "args"], capture_output=True, text=True)
"""

import subprocess
from typing import Any


def filter_cursor_noise(stderr: str) -> str:
    """
    Filter Cursor IDE integration noise from stderr output.

    Removes lines containing 'dump_bash_state: command not found' which
    comes from Cursor's shell wrapper and is not a real error.

    Args:
        stderr: Raw stderr string from subprocess output

    Returns:
        Filtered stderr string with Cursor noise removed
    """
    if not stderr:
        return stderr

    lines = stderr.split("\n")
    filtered = [line for line in lines if "dump_bash_state: command not found" not in line]
    return "\n".join(filtered)


def run_filtered(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
    """
    Wrapper around subprocess.run that automatically filters Cursor IDE noise from stderr.

    This is a drop-in replacement for subprocess.run that filters the
    'dump_bash_state: command not found' error from stderr output.

    Args:
        *args: Positional arguments passed to subprocess.run
        **kwargs: Keyword arguments passed to subprocess.run

    Returns:
        subprocess.CompletedProcess with filtered stderr (if capture_output=True)
    """
    result = subprocess.run(*args, **kwargs)

    # Filter stderr if it was captured
    if hasattr(result, "stderr") and result.stderr:
        if isinstance(result.stderr, str):
            result.stderr = filter_cursor_noise(result.stderr)
        elif hasattr(result.stderr, "decode"):
            # Handle bytes
            decoded = result.stderr.decode("utf-8", errors="replace")
            filtered = filter_cursor_noise(decoded)
            result.stderr = filtered.encode("utf-8") if isinstance(result.stderr, bytes) else filtered

    return result
