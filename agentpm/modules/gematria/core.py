from __future__ import annotations

"""
Core Gematria value logic (skeleton).

Real implementations will be extracted from the Gemantria.v2 numerics pipeline.
See docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md and
docs/SSOT/GEMATRIA_NUMERICS_INTAKE.md for migration details.
"""

from typing import Iterable

DEFAULT_SYSTEM_NAME = "mispar_hechrachi"


def gematria_value(letters: Iterable[str], system: str = DEFAULT_SYSTEM_NAME) -> int:
    """Compute gematria value for a normalized sequence of Hebrew letters.

    This is a placeholder; the real implementation will be ported from
    the existing numerics code.
    """
    raise NotImplementedError("gematria_value is not yet implemented; see Gematria module plan.")


def system_names() -> list[str]:
    """Return the supported Gematria systems in this module.

    Skeleton stub for future expansion.
    """
    return [DEFAULT_SYSTEM_NAME]
