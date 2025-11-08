# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""Light-weight node abstraction used for planning tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GraphNode:
    """Wraps a callable to provide a minimal node interface."""

    name: str
    handler: Callable[..., Any]

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        return self.handler(*args, **kwargs)
