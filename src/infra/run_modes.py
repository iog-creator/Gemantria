"""
Run Mode Controls

Provides dry-run functionality and other execution mode controls.
"""

import os


DRY_RUN = os.getenv("DRY_RUN", "0") == "1"


def maybe_write(write_fn, *, dry=DRY_RUN):
    """
    Call write_fn() unless dry-run is enabled; return True if actually wrote.

    Args:
        write_fn: Function that performs the write operation (no args)
        dry: Whether to skip writes (defaults to DRY_RUN env var)

    Returns:
        bool: True if write_fn was called, False if skipped due to dry-run
    """
    if dry:
        return False

    write_fn()
    return True
