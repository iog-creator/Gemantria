"""Capability Session Envelope Validator

Hermetic validator for capability_session envelopes (from pmagent plan reality-loop).
Checks envelopes against the future AI tracking mapping contract without writing to DB.

See docs/SSOT/CAPABILITY_SESSION_AI_TRACKING_MAPPING.md for the mapping design.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


def validate_capability_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    """Validate a capability_session envelope against the AI tracking mapping contract.

    Hermetic: read-only, no DB writes, no side effects.

    Args:
        envelope: Capability session envelope dict (from JSON file)

    Returns:
        Validation result dict with:
        - ok: bool (True if all required fields present and valid)
        - errors: list[str] (structural errors that prevent mapping)
        - warnings: list[str] (missing optional fields or inconsistencies)
        - derived_tracking: dict (computed fields for future DB mapping):
          - command: str (for control.agent_run_cli.command)
          - request_json: dict (full envelope for control.agent_run_cli.request_json)
          - timestamp: str (RFC3339 timestamp)
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Required fields
    if envelope.get("type") != "capability_session":
        errors.append(f'type must be "capability_session", got: {envelope.get("type")}')

    if envelope.get("version") != "1.0":
        errors.append(f'version must be "1.0", got: {envelope.get("version")}')

    envelope_id = envelope.get("id")
    if not envelope_id or not isinstance(envelope_id, str):
        errors.append("id must be present and non-empty string")

    title = envelope.get("title")
    if not title or not isinstance(title, str):
        errors.append("title must be present and non-empty string")

    source = envelope.get("source")
    if not source or not isinstance(source, str):
        errors.append("source must be present and non-empty string")

    # Required: plan block
    plan = envelope.get("plan")
    if not plan or not isinstance(plan, dict):
        errors.append("plan must be present and a dict")
    else:
        # plan fields are optional but should be strings or null
        if "current_focus" in plan and plan["current_focus"] is not None:
            if not isinstance(plan["current_focus"], str):
                warnings.append("plan.current_focus should be string or null")
        if "next_milestone" in plan and plan["next_milestone"] is not None:
            if not isinstance(plan["next_milestone"], str):
                warnings.append("plan.next_milestone should be string or null")
        if "raw_line" in plan and plan["raw_line"] is not None:
            if not isinstance(plan["raw_line"], str):
                warnings.append("plan.raw_line should be string or null")

        # Optional: dry_run_command (if present, must be non-empty string)
        dry_run_command = plan.get("dry_run_command")
        if dry_run_command is not None:
            if not isinstance(dry_run_command, str) or not dry_run_command:
                errors.append("plan.dry_run_command must be non-empty string if present")

    # Required: posture block
    posture = envelope.get("posture")
    if not posture or not isinstance(posture, dict):
        errors.append("posture must be present and a dict")
    else:
        posture_mode = posture.get("mode")
        if posture_mode not in ("live", "hermetic"):
            errors.append(f'posture.mode must be "live" or "hermetic", got: {posture_mode}')

        # If mode is "live", check for reality and status
        if posture_mode == "live":
            reality = posture.get("reality")
            if not reality or not isinstance(reality, dict):
                warnings.append("posture.reality should be present when mode is 'live'")
            elif "overall_ok" not in reality:
                warnings.append("posture.reality.overall_ok should be present when mode is 'live'")

            status = posture.get("status")
            if not status or not isinstance(status, dict):
                warnings.append("posture.status should be present when mode is 'live'")
            else:
                if "level" not in status:
                    warnings.append("posture.status.level should be present when mode is 'live'")
                if "headline" not in status:
                    warnings.append("posture.status.headline should be present when mode is 'live'")

    # Compute derived tracking fields (for future DB mapping)
    derived_tracking: dict[str, Any] = {}
    if not errors:
        # command: use dry_run_command if present, else "plan.reality-loop"
        plan_dict = envelope.get("plan", {})
        dry_run_cmd = plan_dict.get("dry_run_command")
        derived_tracking["command"] = dry_run_cmd if dry_run_cmd else "plan.reality-loop"

        # request_json: full envelope structure
        derived_tracking["request_json"] = envelope

        # timestamp: try to extract from envelope or use current time
        # (envelopes don't have a timestamp field, but files have it in filename)
        derived_tracking["timestamp"] = datetime.now(UTC).isoformat()

    ok = len(errors) == 0

    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "derived_tracking": derived_tracking,
    }


def validate_capability_envelope_file(path: Path) -> dict[str, Any]:
    """Validate a capability_session envelope file.

    Hermetic: read-only, no DB writes.

    Args:
        path: Path to capability_session JSON file

    Returns:
        Validation result dict (same as validate_capability_envelope) plus:
        - file_path: str (path to the file)
        - file_error: str | None (if file read/parse failed)
    """
    result: dict[str, Any] = {
        "file_path": str(path),
        "file_error": None,
    }

    if not path.exists():
        result["ok"] = False
        result["file_error"] = f"File does not exist: {path}"
        result["errors"] = [result["file_error"]]
        result["warnings"] = []
        result["derived_tracking"] = {}
        return result

    try:
        envelope_data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result["ok"] = False
        result["file_error"] = f"Invalid JSON: {e}"
        result["errors"] = [result["file_error"]]
        result["warnings"] = []
        result["derived_tracking"] = {}
        return result
    except OSError as e:
        result["ok"] = False
        result["file_error"] = f"File read error: {e}"
        result["errors"] = [result["file_error"]]
        result["warnings"] = []
        result["derived_tracking"] = {}
        return result

    # Extract timestamp from filename if possible
    validation_result = validate_capability_envelope(envelope_data)
    result.update(validation_result)

    # Try to extract timestamp from filename
    filename = path.name
    if filename.startswith("capability_session-") and filename.endswith(".json"):
        timestamp_str = filename.replace("capability_session-", "").replace(".json", "")
        try:
            # Convert filename format back to ISO format
            timestamp_iso = timestamp_str.replace("-", ":", 2).replace("+00-00", "+00:00")
            timestamp = datetime.fromisoformat(timestamp_iso).isoformat()
            result["derived_tracking"]["timestamp"] = timestamp
        except (ValueError, AttributeError):
            # Fallback to file modification time
            try:
                timestamp = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
                result["derived_tracking"]["timestamp"] = timestamp
            except OSError:
                pass  # Keep default timestamp

    return result


def scan_capability_envelopes(
    *,
    evidence_dir: Path | None = None,
) -> dict[str, Any]:
    """Scan all capability_session envelopes in evidence/pmagent/ and validate them.

    Hermetic: read-only, no DB writes.

    Args:
        evidence_dir: Directory containing capability_session files (defaults to evidence/pmagent/)

    Returns:
        Summary report dict with:
        - total_files: int (total JSON files found)
        - ok_count: int (files that passed validation)
        - error_count: int (files with structural errors)
        - warning_count: int (files with warnings but no errors)
        - files_with_errors: list[dict] (file paths and error lists)
        - files_with_warnings: list[dict] (file paths and warning lists)
    """
    evidence_path = evidence_dir or (REPO_ROOT / "evidence" / "pmagent")
    if not evidence_path.exists():
        return {
            "total_files": 0,
            "ok_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "files_with_errors": [],
            "files_with_warnings": [],
        }

    # Find all capability_session JSON files
    session_files = list(evidence_path.glob("capability_session-*.json"))

    ok_count = 0
    error_count = 0
    warning_count = 0
    files_with_errors: list[dict[str, Any]] = []
    files_with_warnings: list[dict[str, Any]] = []

    for session_file in session_files:
        result = validate_capability_envelope_file(session_file)
        if result.get("ok", False):
            ok_count += 1
            if result.get("warnings"):
                warning_count += 1
                files_with_warnings.append(
                    {
                        "file_path": result["file_path"],
                        "warnings": result["warnings"],
                    }
                )
        else:
            error_count += 1
            files_with_errors.append(
                {
                    "file_path": result["file_path"],
                    "errors": result.get("errors", []),
                    "file_error": result.get("file_error"),
                }
            )

    return {
        "total_files": len(session_files),
        "ok_count": ok_count,
        "error_count": error_count,
        "warning_count": warning_count,
        "files_with_errors": files_with_errors,
        "files_with_warnings": files_with_warnings,
    }


def validate_and_optionally_persist(
    envelope: dict[str, Any],
    *,
    tracking_enabled: bool,
) -> dict[str, Any]:
    """Validate a capability_session envelope and optionally persist to DB.

    Hermetic: Validation always runs; persistence only if tracking_enabled=True and validation passes.
    DB-off behavior: Returns structured results; no exceptions raised.

    Args:
        envelope: Capability session envelope dict (from JSON file)
        tracking_enabled: If True and validation passes, attempts to persist to DB

    Returns:
        Validation result dict (same as validate_capability_envelope) plus:
        - tracking: dict | None (persistence result if tracking_enabled=True and validation passed)
    """
    # Always run validation first
    validation_result = validate_capability_envelope(envelope)

    # If validation failed or tracking disabled, return validation result only
    if not validation_result.get("ok", False) or not tracking_enabled:
        return validation_result

    # Validation passed and tracking enabled: attempt persistence
    from pmagent.reality.capability_envelope_writer import maybe_persist_capability_session  # noqa: PLC0415

    tracking_result = maybe_persist_capability_session(envelope, tracking_enabled=True)

    # Merge tracking result into validation result
    result = validation_result.copy()
    result["tracking"] = tracking_result

    return result
