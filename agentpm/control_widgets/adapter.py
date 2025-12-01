"""
Control-plane widget adapters for downstream apps (StoryMaker, BibleScholar).

Transforms control-plane exports (graph_compliance.json, biblescholar_reference.json)
into widget props for UI consumption. Hermetic (file-only, no DB/LM calls) and
fail-closed (offline-safe defaults when files are missing or invalid).

See Phase-6D for integration guidance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, TypedDict

# Export paths
GRAPH_COMPLIANCE_PATH = Path("share/atlas/control_plane/graph_compliance.json")
BIBLESCHOLAR_REFERENCE_PATH = Path("share/atlas/control_plane/biblescholar_reference.json")
MCP_STATUS_CARDS_PATH = Path("share/atlas/control_plane/mcp_status_cards.json")

# Type aliases
ComplianceStatus = Literal["ok", "degraded", "unknown"]
ReferenceStatus = Literal["active", "empty", "unknown"]


class GraphComplianceMetrics(TypedDict):
    """Graph compliance metrics for widget contract."""

    totalRunsWithViolations: int
    byTool: Dict[str, int]
    byNode: Dict[str, int]
    byPattern: Dict[str, int]
    byBatch: Dict[str, int]
    windowDays: int
    generatedAt: str


class GraphComplianceWidgetProps(TypedDict):
    """Graph compliance widget props."""

    status: ComplianceStatus
    label: str
    color: str
    icon: str
    tooltip_lines: List[str]
    metrics: GraphComplianceMetrics
    source: Dict[str, str]


class BibleScholarReferenceMetrics(TypedDict):
    """BibleScholar reference metrics for widget contract."""

    totalQuestions: int
    byMode: Dict[str, int]
    byVerseRef: Dict[str, int]
    windowDays: int
    generatedAt: str


class BibleScholarReferenceWidgetProps(TypedDict):
    """BibleScholar reference widget props."""

    status: ReferenceStatus
    label: str
    color: str
    icon: str
    tooltip_lines: List[str]
    metrics: BibleScholarReferenceMetrics
    source: Dict[str, str]


class MCPStatusCardsMetrics(TypedDict):
    """MCP status cards metrics for widget contract."""

    totalCards: int
    okCount: int
    failedCount: int
    generatedAt: str


class MCPStatusCardsWidgetProps(TypedDict):
    """MCP status cards widget props."""

    status: Literal["ok", "degraded", "unknown"]
    label: str
    color: str
    icon: str
    tooltip_lines: List[str]
    metrics: MCPStatusCardsMetrics
    source: Dict[str, str]


@dataclass
class RawGraphCompliance:
    """Raw graph compliance data parsed from JSON file."""

    schema: str
    generated_at: str
    ok: bool
    connection_ok: bool
    total_runs_with_violations: int
    by_tool: Dict[str, int]
    by_node: Dict[str, int]
    by_pattern: Dict[str, int]
    by_batch: Dict[str, int]
    window_days: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RawGraphCompliance:
        """Parse raw graph compliance from dict with safe defaults."""
        metrics = data.get("metrics", {})
        return cls(
            schema=str(data.get("schema", "graph_compliance_v1")),
            generated_at=str(data.get("generated_at", "1970-01-01T00:00:00Z")),
            ok=bool(data.get("ok", False)),
            connection_ok=bool(data.get("connection_ok", False)),
            total_runs_with_violations=int(data.get("total_runs_with_violations", 0)),
            by_tool=dict(metrics.get("by_tool", {})),
            by_node=dict(metrics.get("by_node", {})),
            by_pattern=dict(metrics.get("by_pattern", {})),
            by_batch=dict(metrics.get("by_batch", {})),
            window_days=int(data.get("window_days", 30)),
        )


@dataclass
class RawBibleScholarReference:
    """Raw BibleScholar reference data parsed from JSON file."""

    schema: str
    generated_at: str
    ok: bool
    connection_ok: bool
    total_questions: int
    by_mode: Dict[str, int]
    by_verse_ref: Dict[str, int]
    window_days: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RawBibleScholarReference:
        """Parse raw BibleScholar reference from dict with safe defaults."""
        summary = data.get("summary", {})
        return cls(
            schema=str(data.get("schema", "biblescholar_reference_v1")),
            generated_at=str(data.get("generated_at", "1970-01-01T00:00:00Z")),
            ok=bool(data.get("ok", False)),
            connection_ok=bool(data.get("connection_ok", False)),
            total_questions=int(summary.get("total_questions", 0)),
            by_mode=dict(summary.get("by_mode", {})),
            by_verse_ref=dict(summary.get("by_verse_ref", {})),
            window_days=int(data.get("window_days", 30)),
        )


# Offline-safe default widget props
OFFLINE_SAFE_GRAPH_COMPLIANCE: GraphComplianceWidgetProps = {
    "status": "unknown",
    "label": "Graph compliance unknown (offline-safe mode)",
    "color": "grey",
    "icon": "status-offline",
    "tooltip_lines": [
        "Graph compliance data unavailable",
        "Operating in offline-safe mode",
    ],
    "metrics": {
        "totalRunsWithViolations": 0,
        "byTool": {},
        "byNode": {},
        "byPattern": {},
        "byBatch": {},
        "windowDays": 30,
        "generatedAt": "1970-01-01T00:00:00Z",
    },
    "source": {"path": str(GRAPH_COMPLIANCE_PATH)},
}

OFFLINE_SAFE_BIBLESCHOLAR_REFERENCE: BibleScholarReferenceWidgetProps = {
    "status": "unknown",
    "label": "BibleScholar reference data unknown (offline-safe mode)",
    "color": "grey",
    "icon": "status-offline",
    "tooltip_lines": [
        "BibleScholar reference data unavailable",
        "Operating in offline-safe mode",
    ],
    "metrics": {
        "totalQuestions": 0,
        "byMode": {},
        "byVerseRef": {},
        "windowDays": 30,
        "generatedAt": "1970-01-01T00:00:00Z",
    },
    "source": {"path": str(BIBLESCHOLAR_REFERENCE_PATH)},
}

OFFLINE_SAFE_MCP_STATUS_CARDS: MCPStatusCardsWidgetProps = {
    "status": "unknown",
    "label": "MCP status cards unknown (offline-safe mode)",
    "color": "grey",
    "icon": "status-offline",
    "tooltip_lines": [
        "MCP status cards data unavailable",
        "Operating in offline-safe mode",
    ],
    "metrics": {
        "totalCards": 0,
        "okCount": 0,
        "failedCount": 0,
        "generatedAt": "1970-01-01T00:00:00Z",
    },
    "source": {"path": str(MCP_STATUS_CARDS_PATH)},
}


def _normalize_compliance_status(ok: bool, total_violations: int) -> ComplianceStatus:
    """Normalize compliance status."""
    if not ok:
        return "unknown"
    if total_violations == 0:
        return "ok"
    return "degraded"


def _normalize_reference_status(ok: bool, total_questions: int) -> ReferenceStatus:
    """Normalize reference status."""
    if not ok:
        return "unknown"
    if total_questions == 0:
        return "empty"
    return "active"


def _generate_compliance_label(status: ComplianceStatus, total_violations: int) -> str:
    """Generate human-readable label for compliance status."""
    if status == "ok":
        return "Graph compliance: No violations"
    if status == "degraded":
        return f"Graph compliance: {total_violations} violation(s)"
    return "Graph compliance: Unknown"


def _generate_reference_label(status: ReferenceStatus, total_questions: int) -> str:
    """Generate human-readable label for reference status."""
    if status == "active":
        return f"BibleScholar: {total_questions} question(s)"
    if status == "empty":
        return "BibleScholar: No questions yet"
    return "BibleScholar: Unknown"


def _generate_compliance_color(status: ComplianceStatus) -> str:
    """Generate color from compliance status."""
    if status == "ok":
        return "green"
    if status == "degraded":
        return "yellow"
    return "grey"


def _generate_reference_color(status: ReferenceStatus) -> str:
    """Generate color from reference status."""
    if status == "active":
        return "green"
    if status == "empty":
        return "grey"
    return "grey"


def _generate_compliance_icon(status: ComplianceStatus) -> str:
    """Generate icon name from compliance status."""
    if status == "ok":
        return "status-healthy"
    if status == "degraded":
        return "status-warning"
    return "status-offline"


def _generate_reference_icon(status: ReferenceStatus) -> str:
    """Generate icon name from reference status."""
    if status == "active":
        return "status-active"
    if status == "empty":
        return "status-empty"
    return "status-offline"


def _generate_compliance_tooltip_lines(compliance: RawGraphCompliance) -> List[str]:
    """Generate tooltip lines from compliance data."""
    lines: List[str] = []

    status = _normalize_compliance_status(compliance.ok, compliance.total_runs_with_violations)
    label = _generate_compliance_label(status, compliance.total_runs_with_violations)
    lines.append(label)

    if compliance.total_runs_with_violations > 0:
        lines.append(f"Total violations: {compliance.total_runs_with_violations}")

        # Show top categories
        if compliance.by_tool:
            top_tool = max(compliance.by_tool.items(), key=lambda x: x[1], default=None)
            if top_tool:
                lines.append(f"Top tool: {top_tool[0]} ({top_tool[1]})")

        if compliance.by_node:
            top_node = max(compliance.by_node.items(), key=lambda x: x[1], default=None)
            if top_node:
                lines.append(f"Top node: {top_node[0]} ({top_node[1]})")

    lines.append(f"Window: {compliance.window_days} days")

    return lines


def _generate_reference_tooltip_lines(reference: RawBibleScholarReference) -> List[str]:
    """Generate tooltip lines from reference data."""
    lines: List[str] = []

    status = _normalize_reference_status(reference.ok, reference.total_questions)
    label = _generate_reference_label(status, reference.total_questions)
    lines.append(label)

    if reference.total_questions > 0:
        lines.append(f"Total questions: {reference.total_questions}")

        if reference.by_mode:
            mode_summary = ", ".join(
                f"{mode}: {count}" for mode, count in reference.by_mode.items()
            )
            lines.append(f"Modes: {mode_summary}")

        if reference.by_verse_ref:
            top_ref = max(reference.by_verse_ref.items(), key=lambda x: x[1], default=None)
            if top_ref:
                lines.append(f"Top reference: {top_ref[0]} ({top_ref[1]})")

    lines.append(f"Window: {reference.window_days} days")

    return lines


def load_graph_compliance_widget_props() -> GraphComplianceWidgetProps:
    """
    Load graph compliance widget props from canonical JSON file.

    Returns widget props for graph compliance metrics. Hermetic (file-only,
    no DB/LM calls) and fail-closed (offline-safe defaults when file is missing
    or invalid).

    Returns:
        GraphComplianceWidgetProps: Widget props with status, label, color,
            icon, tooltip_lines, metrics, and source fields.
    """
    # Read compliance file
    try:
        if not GRAPH_COMPLIANCE_PATH.exists():
            return OFFLINE_SAFE_GRAPH_COMPLIANCE

        raw_json = json.loads(GRAPH_COMPLIANCE_PATH.read_text(encoding="utf-8"))
        raw_compliance = RawGraphCompliance.from_dict(raw_json)

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return OFFLINE_SAFE_GRAPH_COMPLIANCE

    # Normalize status
    status = _normalize_compliance_status(
        raw_compliance.ok, raw_compliance.total_runs_with_violations
    )

    # Generate widget props
    props: GraphComplianceWidgetProps = {
        "status": status,
        "label": _generate_compliance_label(status, raw_compliance.total_runs_with_violations),
        "color": _generate_compliance_color(status),
        "icon": _generate_compliance_icon(status),
        "tooltip_lines": _generate_compliance_tooltip_lines(raw_compliance),
        "metrics": {
            "totalRunsWithViolations": raw_compliance.total_runs_with_violations,
            "byTool": raw_compliance.by_tool,
            "byNode": raw_compliance.by_node,
            "byPattern": raw_compliance.by_pattern,
            "byBatch": raw_compliance.by_batch,
            "windowDays": raw_compliance.window_days,
            "generatedAt": raw_compliance.generated_at,
        },
        "source": {"path": str(GRAPH_COMPLIANCE_PATH)},
    }

    return props


def load_biblescholar_reference_widget_props() -> BibleScholarReferenceWidgetProps:
    """
    Load BibleScholar reference widget props from canonical JSON file.

    Returns widget props for BibleScholar reference metrics. Hermetic (file-only,
    no DB/LM calls) and fail-closed (offline-safe defaults when file is missing
    or invalid).

    Returns:
        BibleScholarReferenceWidgetProps: Widget props with status, label, color,
            icon, tooltip_lines, metrics, and source fields.
    """
    # Read reference file
    try:
        if not BIBLESCHOLAR_REFERENCE_PATH.exists():
            return OFFLINE_SAFE_BIBLESCHOLAR_REFERENCE

        raw_json = json.loads(BIBLESCHOLAR_REFERENCE_PATH.read_text(encoding="utf-8"))
        raw_reference = RawBibleScholarReference.from_dict(raw_json)

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return OFFLINE_SAFE_BIBLESCHOLAR_REFERENCE

    # Normalize status
    status = _normalize_reference_status(raw_reference.ok, raw_reference.total_questions)

    # Generate widget props
    props: BibleScholarReferenceWidgetProps = {
        "status": status,
        "label": _generate_reference_label(status, raw_reference.total_questions),
        "color": _generate_reference_color(status),
        "icon": _generate_reference_icon(status),
        "tooltip_lines": _generate_reference_tooltip_lines(raw_reference),
        "metrics": {
            "totalQuestions": raw_reference.total_questions,
            "byMode": raw_reference.by_mode,
            "byVerseRef": raw_reference.by_verse_ref,
            "windowDays": raw_reference.window_days,
            "generatedAt": raw_reference.generated_at,
        },
        "source": {"path": str(BIBLESCHOLAR_REFERENCE_PATH)},
    }

    return props


def load_mcp_status_cards_widget_props() -> MCPStatusCardsWidgetProps:
    """
    Load MCP status cards widget props from canonical JSON file.

    Returns widget props for MCP status cards (E21-E25 proofs). Hermetic (file-only,
    no DB/LM calls) and fail-closed (offline-safe defaults when file is missing
    or invalid).

    Returns:
        MCPStatusCardsWidgetProps: Widget props with status, label, color,
            icon, tooltip_lines, metrics, and source fields.
    """
    # Read status cards file
    try:
        if not MCP_STATUS_CARDS_PATH.exists():
            return OFFLINE_SAFE_MCP_STATUS_CARDS

        raw_json = json.loads(MCP_STATUS_CARDS_PATH.read_text(encoding="utf-8"))
        ok = raw_json.get("ok", False)
        summary = raw_json.get("summary", {})
        total_cards = summary.get("total_cards", 0)
        ok_count = summary.get("ok_count", 0)
        failed_count = summary.get("failed_count", 0)
        generated_at = raw_json.get("generated_at", "1970-01-01T00:00:00Z")

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return OFFLINE_SAFE_MCP_STATUS_CARDS

    # Normalize status
    if not ok:
        status: Literal["ok", "degraded", "unknown"] = "unknown"
    elif failed_count > 0:
        status = "degraded"
    else:
        status = "ok"

    # Generate label
    if status == "ok":
        label = f"MCP Status Cards: {ok_count}/{total_cards} OK"
    elif status == "degraded":
        label = f"MCP Status Cards: {failed_count} failed"
    else:
        label = "MCP Status Cards: Unknown"

    # Generate color
    color = "green" if status == "ok" else ("yellow" if status == "degraded" else "grey")

    # Generate icon
    icon = (
        "status-healthy"
        if status == "ok"
        else ("status-warning" if status == "degraded" else "status-offline")
    )

    # Generate tooltip lines
    tooltip_lines = [
        label,
        f"Total cards: {total_cards}",
        f"OK: {ok_count}, Failed: {failed_count}",
        f"Generated: {generated_at}",
    ]

    # Generate widget props
    props: MCPStatusCardsWidgetProps = {
        "status": status,
        "label": label,
        "color": color,
        "icon": icon,
        "tooltip_lines": tooltip_lines,
        "metrics": {
            "totalCards": total_cards,
            "okCount": ok_count,
            "failedCount": failed_count,
            "generatedAt": generated_at,
        },
        "source": {"path": str(MCP_STATUS_CARDS_PATH)},
    }

    return props
