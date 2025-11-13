from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
EVIDENCE_DIR = REPO_ROOT / "evidence"
VERDICT_PATH = EVIDENCE_DIR / "guard_control_knowledge_mcp_exports.json"


@dataclass
class FileCheck:
    name: str
    exists: bool
    ok: bool
    errors: list[str]


@dataclass
class GuardVerdict:
    ok: bool
    files: list[FileCheck]
    errors: list[str]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _check_mcp_catalog(path: Path) -> FileCheck:
    errors: list[str] = []
    exists = path.exists()
    if not exists:
        errors.append("missing mcp_catalog.json")
        return FileCheck(name="mcp_catalog.json", exists=False, ok=False, errors=errors)

    try:
        data = _load_json(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {exc!s}")
        return FileCheck(name="mcp_catalog.json", exists=True, ok=False, errors=errors)

    if not isinstance(data, dict):
        errors.append("top-level JSON is not an object")
    for key in ("schema", "generated_at", "ok", "connection_ok", "tools", "error"):
        if key not in data:
            errors.append(f"missing key: {key}")
    if "schema" in data and data["schema"] != "control":
        errors.append(f"schema must be 'control', got {data['schema']!r}")
    if "tools" in data and not isinstance(data["tools"], list):
        errors.append("tools must be a list")

    return FileCheck(
        name="mcp_catalog.json",
        exists=True,
        ok=not errors,
        errors=errors,
    )


def _check_capability_rules(path: Path) -> FileCheck:
    errors: list[str] = []
    exists = path.exists()
    if not exists:
        errors.append("missing capability_rules.json")
        return FileCheck(name="capability_rules.json", exists=False, ok=False, errors=errors)

    try:
        data = _load_json(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {exc!s}")
        return FileCheck(name="capability_rules.json", exists=True, ok=False, errors=errors)

    if not isinstance(data, dict):
        errors.append("top-level JSON is not an object")
    for key in ("schema", "generated_at", "ok", "connection_ok", "rules", "error"):
        if key not in data:
            errors.append(f"missing key: {key}")
    if "schema" in data and data["schema"] != "control":
        errors.append(f"schema must be 'control', got {data['schema']!r}")
    if "rules" in data and not isinstance(data["rules"], list):
        errors.append("rules must be a list")

    return FileCheck(
        name="capability_rules.json",
        exists=True,
        ok=not errors,
        errors=errors,
    )


def _check_agent_runs_7d(path: Path) -> FileCheck:
    errors: list[str] = []
    exists = path.exists()
    if not exists:
        errors.append("missing agent_runs_7d.json")
        return FileCheck(name="agent_runs_7d.json", exists=False, ok=False, errors=errors)

    try:
        data = _load_json(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {exc!s}")
        return FileCheck(name="agent_runs_7d.json", exists=True, ok=False, errors=errors)

    if not isinstance(data, dict):
        errors.append("top-level JSON is not an object")
    for key in (
        "schema",
        "generated_at",
        "window_days",
        "since",
        "ok",
        "connection_ok",
        "runs",
        "sessions",
        "error",
    ):
        if key not in data:
            errors.append(f"missing key: {key}")
    if "schema" in data and data["schema"] != "control":
        errors.append(f"schema must be 'control', got {data['schema']!r}")
    if "window_days" in data and data["window_days"] != 7:
        errors.append(f"window_days must be 7, got {data['window_days']!r}")
    if "runs" in data and not isinstance(data["runs"], list):
        errors.append("runs must be a list")
    if "sessions" in data and not isinstance(data["sessions"], list):
        errors.append("sessions must be a list")

    return FileCheck(
        name="agent_runs_7d.json",
        exists=True,
        ok=not errors,
        errors=errors,
    )


def run_guard() -> GuardVerdict:
    files: list[FileCheck] = []

    mcp_catalog_file = CONTROL_DIR / "mcp_catalog.json"
    capability_rules_file = CONTROL_DIR / "capability_rules.json"
    agent_runs_file = CONTROL_DIR / "agent_runs_7d.json"

    files.append(_check_mcp_catalog(mcp_catalog_file))
    files.append(_check_capability_rules(capability_rules_file))
    files.append(_check_agent_runs_7d(agent_runs_file))

    errors: list[str] = []
    for fc in files:
        errors.extend(f"{fc.name}: {e}" for e in fc.errors)

    ok = not errors
    return GuardVerdict(ok=ok, files=files, errors=errors)


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    verdict = run_guard()
    VERDICT_PATH.write_text(
        json.dumps(asdict(verdict), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    # HINT/STRICT behavior is controlled by callers; script itself exits 0.


if __name__ == "__main__":
    main()
