#!/usr/bin/env python3
"""
filter_stderr.py — Filter Cursor IDE integration noise from stderr.

Filters the 'dump_bash_state: command not found' error that comes from
Cursor's shell wrapper. This error is harmless but clutters output.

Usage:
    from scripts.util.filter_stderr import filter_cursor_noise
    
    stderr_filtered = filter_cursor_noise(result.stderr)
"""


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
