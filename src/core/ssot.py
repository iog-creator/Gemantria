"""Utilities for working with the Single Source of Truth (SSOT) documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MasterPlan:
    """Represents the expectations captured in :mod:`docs/MASTER_PLAN.md`."""

    bootstrap_summary: str
    coverage_gate: float
    prohibits_db_writes: bool

    @classmethod
    def load_from_file(cls, path: Path) -> MasterPlan:
        """Load the master plan from ``path``.

        The markdown file contains a bullet list with the guarantees we care about.  The
        loader performs a tiny amount of parsing so the data can be used programmatically in
        tests without the need for a heavier markdown dependency.
        """

        if not path.exists():
            msg = f"Master plan file does not exist: {path}"
            raise FileNotFoundError(msg)

        text = path.read_text(encoding="utf-8")
        lines = [line.strip("- ") for line in text.splitlines() if line.strip("- ")]  # type: ignore[arg-type]
        if not lines:
            msg = "Master plan document is empty."
            raise ValueError(msg)

        bootstrap_summary = next((line for line in lines if line.startswith("PR-")), lines[0])

        coverage_gate = 0.0
        prohibits_db_writes = False
        for line in lines:
            if "Coverage gate" in line:
                match = re.search(r"(\d+)(?:\.\d+)?", line)
                if match:
                    coverage_gate = float(match.group(1))
            if "No writes" in line:
                prohibits_db_writes = True

        if coverage_gate == 0.0:
            msg = "Coverage gate could not be parsed from master plan."
            raise ValueError(msg)

        return cls(
            bootstrap_summary=bootstrap_summary,
            coverage_gate=coverage_gate,
            prohibits_db_writes=prohibits_db_writes,
        )

    def confirm_expectations(self, measured_coverage: float, wrote_to_db: bool) -> None:
        """Validate that the observed conditions meet the SSOT requirements."""

        if measured_coverage < self.coverage_gate:
            msg = f"Coverage requirement not met: expected ≥{self.coverage_gate}, observed {measured_coverage}."
            raise ValueError(msg)
        if wrote_to_db and self.prohibits_db_writes:
            msg = "Database writes were attempted even though they are forbidden."
            raise ValueError(msg)

    def summary(self) -> str:
        """Return a human friendly summary."""

        expectations = [
            f"Coverage ≥ {self.coverage_gate}",
            "DB writes disabled" if self.prohibits_db_writes else "DB writes allowed",
        ]
        expectations_text = ", ".join(expectations)
        return f"{self.bootstrap_summary} ({expectations_text})."
