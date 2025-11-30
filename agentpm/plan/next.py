"""Plan Next - Suggest next work items from MASTER_PLAN + NEXT_STEPS.

Hermetic: file-only, no DB/LM calls, no writes.
With --with-status: optionally includes system posture (reality-check + status.explain).
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Import hint registry (graceful degradation if unavailable)
try:
    from agentpm.hints.registry import embed_hints_in_envelope, load_hints_for_flow

    HAS_HINT_REGISTRY = True
except ImportError:
    HAS_HINT_REGISTRY = False

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MASTER_PLAN_PATH = REPO_ROOT / "docs" / "SSOT" / "MASTER_PLAN.md"
DEFAULT_NEXT_STEPS_PATH = REPO_ROOT / "NEXT_STEPS.md"


def _read_lines(path: Path) -> list[str]:
    """Read file lines, returning empty list if file not found."""
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []


def _extract_line_value(lines: list[str], marker: str) -> str | None:
    """Extract value from a line containing marker (e.g., '**Current Focus**: Phase 8')."""
    for line in lines:
        if marker in line:
            # e.g. "**Current Focus**: Phase 8 ..."
            if ":" in line:
                return line.split(":", 1)[1].strip()
    return None


def _extract_next_steps_candidates(lines: list[str]) -> list[dict[str, Any]]:
    """Find the last '# Next Gate' / '# Next Steps' heading in NEXT_STEPS.md.

    Treat following bullet points as candidate tasks.
    """
    heading_idx: int | None = None
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("# Next Gate") or stripped.startswith("# Next Steps"):
            heading_idx = idx

    if heading_idx is None:
        return []

    candidates: list[dict[str, Any]] = []
    priority = 1
    for line in lines[heading_idx + 1 :]:
        stripped = line.strip()
        if stripped.startswith("# "):
            break
        if stripped.startswith("- "):
            title = stripped[2:].strip()
            candidates.append(
                {
                    "id": f"NEXT_STEPS:{priority}",
                    "title": title,
                    "source": "NEXT_STEPS",
                    "priority": priority,
                    "raw_line": stripped,
                }
            )
            priority += 1

    return candidates


def _fetch_posture() -> dict[str, Any]:
    """Fetch system posture from reality-check and status explain.

    Returns:
        Dictionary with:
        - mode: "hermetic" if commands unavailable, "live" if successful
        - reality: dict from pmagent reality-check check --mode hint --json-only
        - status: dict from pmagent status explain --json-only
        - error: str if commands failed (only in hermetic mode)
    """
    posture: dict[str, Any] = {
        "mode": "hermetic",
        "reality": None,
        "status": None,
    }

    # Try to fetch reality-check
    try:
        result = subprocess.run(
            ["pmagent", "reality-check", "check", "--mode", "hint", "--json-only"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0:
            try:
                posture["reality"] = json.loads(result.stdout)
            except json.JSONDecodeError:
                posture["error"] = "reality-check returned invalid JSON"
        else:
            posture["error"] = f"reality-check failed: {result.stderr[:200]}"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        posture["error"] = f"reality-check unavailable: {e!s}"

    # Try to fetch status explain
    try:
        result = subprocess.run(
            ["pmagent", "status", "explain", "--json-only"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            try:
                posture["status"] = json.loads(result.stdout)
            except json.JSONDecodeError:
                if "error" not in posture:
                    posture["error"] = "status explain returned invalid JSON"
        else:
            if "error" not in posture:
                posture["error"] = f"status explain failed: {result.stderr[:200]}"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        if "error" not in posture:
            posture["error"] = f"status explain unavailable: {e!s}"

    # Determine mode: "live" if both succeeded, "hermetic" otherwise
    if posture.get("reality") and posture.get("status"):
        posture["mode"] = "live"
        posture.pop("error", None)
    else:
        posture["mode"] = "hermetic"

    return posture


def build_next_plan(
    *,
    limit: int = 3,
    master_plan_path: Path | None = None,
    next_steps_path: Path | None = None,
    with_status: bool = False,
) -> dict[str, Any]:
    """Build a small 'next work items' suggestion from MASTER_PLAN + NEXT_STEPS.

    Hermetic: file-only, no DB/LM calls, no writes.
    With with_status=True: optionally includes system posture (reality-check + status.explain).

    Args:
        limit: Maximum number of candidates to return (0 = all)
        master_plan_path: Path to MASTER_PLAN.md (defaults to docs/SSOT/MASTER_PLAN.md)
        next_steps_path: Path to NEXT_STEPS.md (defaults to repo root NEXT_STEPS.md)
        with_status: If True, include system posture (reality-check + status.explain)

    Returns:
        Dictionary with:
        - available: bool (True if both files exist and have content)
        - master_plan_path: str
        - next_steps_path: str
        - current_focus: str | None
        - next_milestone: str | None
        - candidates: list of {id, title, source, priority, raw_line}
        - posture: dict (if with_status=True) with mode, reality, status, error
        - note: str (if unavailable)
    """
    mp_path = master_plan_path or DEFAULT_MASTER_PLAN_PATH
    ns_path = next_steps_path or DEFAULT_NEXT_STEPS_PATH

    master_lines = _read_lines(mp_path)
    next_steps_lines = _read_lines(ns_path)

    if not master_lines or not next_steps_lines:
        return {
            "available": False,
            "master_plan_path": str(mp_path),
            "next_steps_path": str(ns_path),
            "current_focus": None,
            "next_milestone": None,
            "candidates": [],
            "note": "MASTER_PLAN.md or NEXT_STEPS.md missing or empty",
        }

    current_focus = _extract_line_value(master_lines, "Current Focus")
    next_milestone = _extract_line_value(master_lines, "Next Milestone")

    candidates = _extract_next_steps_candidates(next_steps_lines)
    if limit > 0:
        candidates = candidates[:limit]

    result: dict[str, Any] = {
        "available": True,
        "master_plan_path": str(mp_path),
        "next_steps_path": str(ns_path),
        "current_focus": current_focus,
        "next_milestone": next_milestone,
        "candidates": candidates,
    }

    if with_status:
        result["posture"] = _fetch_posture()

    return result


def build_capability_session(
    candidate_id: str,
    *,
    master_plan_path: Path | None = None,
    next_steps_path: Path | None = None,
    with_status: bool = True,
) -> dict[str, Any]:
    """Build a capability_session envelope for a specific NEXT_STEPS candidate.

    Hermetic: file-only, no DB/LM calls, no writes.
    With with_status=True: optionally includes system posture (reality-check + status.explain).

    Args:
        candidate_id: ID from NEXT_STEPS (e.g., "NEXT_STEPS:1")
        master_plan_path: Path to MASTER_PLAN.md (defaults to docs/SSOT/MASTER_PLAN.md)
        next_steps_path: Path to NEXT_STEPS.md (defaults to repo root NEXT_STEPS.md)
        with_status: If True, include system posture (reality-check + status.explain)

    Returns:
        Dictionary with:
        - type: "capability_session"
        - version: "1.0"
        - id: candidate_id
        - title: candidate title
        - source: "NEXT_STEPS"
        - plan: {current_focus, next_milestone, raw_line}
        - posture: dict (if with_status=True) with mode, reality, status, error
        - available: bool (False if candidate not found)
        - reason: str (if unavailable, explains why)
    """
    # Get the full plan to find the candidate
    plan_result = build_next_plan(
        limit=0,  # Get all candidates
        master_plan_path=master_plan_path,
        next_steps_path=next_steps_path,
        with_status=with_status,
    )

    if not plan_result.get("available", False):
        return {
            "type": "capability_session",
            "version": "1.0",
            "id": candidate_id,
            "available": False,
            "reason": plan_result.get("note", "MASTER_PLAN.md or NEXT_STEPS.md missing or empty"),
        }

    # Find the matching candidate
    candidates = plan_result.get("candidates", [])
    matching_candidate = None
    for cand in candidates:
        if cand.get("id") == candidate_id:
            matching_candidate = cand
            break

    if not matching_candidate:
        return {
            "type": "capability_session",
            "version": "1.0",
            "id": candidate_id,
            "available": False,
            "reason": f"candidate_not_found: {candidate_id}",
        }

    # Build the capability session envelope
    session: dict[str, Any] = {
        "type": "capability_session",
        "version": "1.0",
        "id": candidate_id,
        "title": matching_candidate.get("title", ""),
        "source": matching_candidate.get("source", "NEXT_STEPS"),
        "plan": {
            "current_focus": plan_result.get("current_focus"),
            "next_milestone": plan_result.get("next_milestone"),
            "raw_line": matching_candidate.get("raw_line"),
        },
        "available": True,
    }

    if with_status:
        session["posture"] = plan_result.get("posture", {"mode": "hermetic"})

    # Load hints from DMS and embed into envelope (graceful degradation if unavailable)
    if HAS_HINT_REGISTRY:
        try:
            hints = load_hints_for_flow(
                scope="agentpm",
                applies_to={"flow": "capability_session", "agent": "pm"},
                mode="HINT",  # Graceful degradation
            )
            session = embed_hints_in_envelope(session, hints)
        except Exception:
            # If DMS unavailable, continue without hints
            pass

    return session


def run_reality_loop(
    *,
    limit: int = 3,
    master_plan_path: Path | None = None,
    next_steps_path: Path | None = None,
    evidence_dir: Path | None = None,
    dry_run_command: str | None = None,
) -> dict[str, Any]:
    """Run a single planning + posture loop and persist a capability_session envelope.

    Hermetic: file-only + existing pmagent commands; no direct DB writes.

    Args:
        limit: Maximum number of candidates to consider from NEXT_STEPS
        master_plan_path: Path to MASTER_PLAN.md (defaults to docs/SSOT/MASTER_PLAN.md)
        next_steps_path: Path to NEXT_STEPS.md (defaults to repo root NEXT_STEPS.md)
        evidence_dir: Directory to write capability_session envelope (defaults to evidence/pmagent/)
        dry_run_command: Optional shell/Make/pmagent command to associate with this session (NOT executed)

    Returns:
        Dictionary with:
        - available: bool (True if candidates found and envelope written)
        - candidate: dict | None (selected candidate info: id, title, source)
        - envelope_path: str | None (path to written JSON file)
        - envelope: dict | None (full capability_session envelope)
        - dry_run_command: str | None (the command string if provided)
        - error: str | None (if available=False, explains why)
    """
    # Get the plan with posture
    plan_result = build_next_plan(
        limit=limit,
        master_plan_path=master_plan_path,
        next_steps_path=next_steps_path,
        with_status=True,
    )

    if not plan_result.get("available", False):
        return {
            "available": False,
            "candidate": None,
            "envelope_path": None,
            "envelope": None,
            "error": plan_result.get("note", "MASTER_PLAN.md or NEXT_STEPS.md missing or empty"),
        }

    candidates = plan_result.get("candidates", [])
    if not candidates:
        return {
            "available": False,
            "candidate": None,
            "envelope_path": None,
            "envelope": None,
            "error": "No candidates found in NEXT_STEPS.md",
        }

    # Pick the highest-priority candidate (first one)
    selected_candidate = candidates[0]
    candidate_id = selected_candidate.get("id")

    # Build the capability session envelope
    session = build_capability_session(
        candidate_id,
        master_plan_path=master_plan_path,
        next_steps_path=next_steps_path,
        with_status=True,
    )

    if not session.get("available", False):
        return {
            "available": False,
            "candidate": {
                "id": candidate_id,
                "title": selected_candidate.get("title", ""),
                "source": selected_candidate.get("source", "NEXT_STEPS"),
            },
            "envelope_path": None,
            "envelope": None,
            "dry_run_command": dry_run_command,
            "error": session.get("reason", "Failed to build capability session"),
        }

    # Add dry_run_command to the session envelope if provided
    if dry_run_command:
        session.setdefault("plan", {})["dry_run_command"] = dry_run_command

    # Write the envelope to evidence/pmagent/
    evidence_path = evidence_dir or (REPO_ROOT / "evidence" / "pmagent")
    evidence_path.mkdir(parents=True, exist_ok=True)

    # Generate RFC3339 timestamp for filename
    timestamp = datetime.now(UTC).isoformat(timespec="seconds").replace(":", "-")
    envelope_filename = f"capability_session-{timestamp}.json"
    envelope_path = evidence_path / envelope_filename

    # Write the envelope
    envelope_path.write_text(json.dumps(session, indent=2), encoding="utf-8")

    return {
        "available": True,
        "candidate": {
            "id": candidate_id,
            "title": selected_candidate.get("title", ""),
            "source": selected_candidate.get("source", "NEXT_STEPS"),
        },
        "envelope_path": str(envelope_path),
        "envelope": session,
        "dry_run_command": dry_run_command,
        "error": None,
    }


def list_capability_sessions(
    *,
    limit: int = 10,
    evidence_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """List recent capability_session envelopes from evidence/pmagent/.

    Hermetic: read-only, file-only, no DB/LM calls.

    Args:
        limit: Maximum number of sessions to return (default: 10)
        evidence_dir: Directory containing capability_session files (defaults to evidence/pmagent/)

    Returns:
        List of session summaries, sorted newest-first, each with:
        - id: Candidate ID (e.g., "NEXT_STEPS:1")
        - title: Candidate title
        - source: Source (e.g., "NEXT_STEPS")
        - envelope_path: Full path to the envelope file
        - timestamp: RFC3339 timestamp from filename or envelope
        - dry_run_command: str | None (if present in envelope)
        - posture_mode: str | None ("live" or "hermetic" if posture present)
        - reality_overall_ok: bool | None (if posture.reality present)
        - status_level: str | None (if posture.status present)
    """
    evidence_path = evidence_dir or (REPO_ROOT / "evidence" / "pmagent")
    if not evidence_path.exists():
        return []

    # Find all capability_session JSON files
    session_files = sorted(
        evidence_path.glob("capability_session-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,  # Newest first
    )[:limit]

    sessions = []
    for session_file in session_files:
        try:
            envelope_data = json.loads(session_file.read_text(encoding="utf-8"))
            if envelope_data.get("type") != "capability_session":
                continue

            # Extract timestamp from filename (format: capability_session-2025-11-22T02-37-10+00-00.json)
            filename = session_file.name
            timestamp_str = filename.replace("capability_session-", "").replace(".json", "")
            # Try to parse timestamp, fallback to file mtime
            try:
                # Convert filename format back to ISO format
                timestamp_iso = timestamp_str.replace("-", ":", 2).replace("+00-00", "+00:00")
                timestamp = datetime.fromisoformat(timestamp_iso).isoformat()
            except (ValueError, AttributeError):
                # Fallback to file modification time
                timestamp = datetime.fromtimestamp(session_file.stat().st_mtime, tz=UTC).isoformat()

            # Extract posture info
            posture = envelope_data.get("posture", {})
            posture_mode = posture.get("mode") if posture else None
            reality_overall_ok = None
            status_level = None
            if posture and posture_mode == "live":
                reality = posture.get("reality", {})
                status = posture.get("status", {})
                reality_overall_ok = reality.get("overall_ok")
                status_level = status.get("level")

            # Extract dry_run_command from plan
            plan = envelope_data.get("plan", {})
            dry_run_command = plan.get("dry_run_command")

            sessions.append(
                {
                    "id": envelope_data.get("id", "?"),
                    "title": envelope_data.get("title", "Unknown"),
                    "source": envelope_data.get("source", "NEXT_STEPS"),
                    "envelope_path": str(session_file),
                    "timestamp": timestamp,
                    "dry_run_command": dry_run_command,
                    "posture_mode": posture_mode,
                    "reality_overall_ok": reality_overall_ok,
                    "status_level": status_level,
                }
            )
        except (json.JSONDecodeError, OSError, KeyError):
            # Skip invalid or unreadable files
            continue

    return sessions
