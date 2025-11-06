"""
Cache Signature Utilities

Provides stable signature generation for deterministic caching.
"""

import hashlib
import json


def sig(*parts):
    """
    Generate a stable signature for a run based on input parameters.

    Args:
        *parts: Variable number of dict/list/string arguments to include in signature

    Returns:
        str: First 16 characters of SHA256 hash
    """
    m = hashlib.sha256()

    for p in parts:
        # Convert to stable JSON representation
        m.update(json.dumps(p, sort_keys=True, ensure_ascii=False).encode("utf-8"))

    return m.hexdigest()[:16]
