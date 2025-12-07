#!/usr/bin/env python
"""
generate_pm_bootstrap_state.py

Generate share/PM_BOOTSTRAP_STATE.json — a minimal index of critical SSOT docs
for new PM chats.

This script is **non-destructive**: it only writes a small JSON summary.
If a referenced file is missing, it logs a warning but still writes the file.

Upgraded to:
- Dynamically detect all PHASE*.md files (phase and sub-phase patterns)
- Use KB registry as canonical source (filter by ssot tag + importance=high)
- Exclude archived/disabled docs (enabled: false)
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, UTC
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Pre-flight DB check (mandatory - Rule 050 evidence-first)
# Note: This script calls check_alignment_status() which runs guard_dms_share_alignment.py,
# which itself queries control.doc_registry. Pre-flight ensures DB is available.
preflight_script = ROOT / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight_script), "--mode", "strict"], capture_output=True)
if result.returncode != 0:
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)

SSOT = ROOT / "docs" / "SSOT"
SHARE = ROOT / "share"
OUT = SHARE / "PM_BOOTSTRAP_STATE.json"
REGISTRY_PATH = SHARE / "kb_registry.json"
SSOT_SURFACE_PATH = SHARE / "SSOT_SURFACE_V17.json"

# Phase file pattern: PHASE[_]?(\d+)(?:_(\d+))?.*\.md
PHASE_PATTERN = re.compile(r"PHASE[_]?(\d+)(?:_(\d+))?[_.]", re.IGNORECASE)


def exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def optional(path: str):
    return path if exists(path) else None


def extract_phase_number(filename: str) -> tuple[int, int | None] | None:
    """Extract phase number from filename.

    Returns (phase, sub_phase) or None if not a phase file.
    """
    match = PHASE_PATTERN.match(filename.upper())
    if not match:
        return None
    phase = int(match.group(1))
    sub_phase = int(match.group(2)) if match.group(2) else None
    return (phase, sub_phase)


def discover_phase_files() -> dict[str, dict[str, Any]]:
    """Dynamically discover all PHASE*.md files in docs/SSOT/ and share/."""
    phase_files = {}

    search_paths = [SSOT, SHARE]

    for base_dir in search_paths:
        if not base_dir.exists():
            continue

        for file_path in base_dir.glob("PHASE*.md"):
            filename = file_path.name
            rel_path = str(file_path.relative_to(ROOT))

            phase_info = extract_phase_number(filename)
            if not phase_info:
                continue

            phase, sub_phase = phase_info
            phase_key = f"{phase}.{sub_phase}" if sub_phase else str(phase)

            phase_files[rel_path] = {
                "path": rel_path,
                "phase": phase,
                "sub_phase": sub_phase,
                "phase_key": phase_key,
            }

    return phase_files


def load_kb_registry() -> dict[str, Any] | None:
    """Load KB registry if available."""
    if not REGISTRY_PATH.exists():
        return None

    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_registry_docs_by_filter(
    registry: dict[str, Any],
    tags: list[str] | None = None,
    importance: str | None = None,
    enabled_only: bool = True,
) -> list[dict[str, Any]]:
    """Filter registry documents by tags, importance, and enabled status."""
    if "documents" not in registry:
        return []

    docs = []
    for doc in registry["documents"]:
        # Check enabled status
        if enabled_only:
            enabled = doc.get("provenance", {}).get("enabled", True)
            if not enabled:
                continue

        # Check tags
        if tags:
            doc_tags = set(doc.get("tags", []))
            if not all(tag in doc_tags for tag in tags):
                continue

        # Check importance
        if importance:
            doc_importance = doc.get("provenance", {}).get("dominant_importance", "low")
            if doc_importance != importance:
                continue

        docs.append(doc)

    return docs


def build_phase_structure(
    phase_files: dict[str, dict[str, Any]], registry: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build phase structure from discovered files and registry."""
    phases: dict[str, Any] = {}

    # Group by phase key
    for rel_path, metadata in phase_files.items():
        phase_key = metadata["phase_key"]
        if phase_key not in phases:
            phases[phase_key] = {}

        # Use filename to create a semantic key
        filename = Path(rel_path).stem
        # Remove PHASE prefix and normalize
        key = filename.replace("PHASE", "").replace("PHASE_", "").lower()
        # Use a simple key based on filename pattern
        if "diagnostic" in filename.lower():
            semantic_key = "diagnostic"
        elif "plan" in filename.lower():
            semantic_key = "plan"
        elif "wiring" in filename.lower():
            semantic_key = "wiring"
        elif "status" in filename.lower():
            semantic_key = "status"
        elif "complete" in filename.lower():
            semantic_key = "complete"
        elif "structural" in filename.lower():
            semantic_key = "structural_gap"
        elif "correction" in filename.lower():
            semantic_key = "status_correction"
        elif "self_assessment" in filename.lower():
            semantic_key = "self_assessment"
        elif "recon" in filename.lower():
            semantic_key = "recon"
        else:
            # Fallback: use sanitized filename
            semantic_key = filename.lower().replace("phase", "").replace("_", "").replace("-", "")

        phases[phase_key][semantic_key] = optional(rel_path)

    # If registry is available, enhance with registry metadata
    if registry:
        registry_docs = get_registry_docs_by_filter(registry, tags=["ssot"], importance="high", enabled_only=True)
        for doc in registry_docs:
            path = doc.get("path", "")
            if not path.startswith("docs/SSOT/"):
                continue

            # Extract phase from provenance or path
            provenance = doc.get("provenance", {})
            phase_key = provenance.get("phase_key")
            if not phase_key:
                # Try to extract from filename
                filename = Path(path).name
                phase_info = extract_phase_number(filename)
                if phase_info:
                    phase, sub_phase = phase_info
                    phase_key = f"{phase}.{sub_phase}" if sub_phase else str(phase)
                else:
                    continue

            if phase_key not in phases:
                phases[phase_key] = {}

            # Add document if not already present
            # Use a generic key if we can't determine semantic key
            if path not in [v for v in phases[phase_key].values() if v]:
                # Find a key for this document
                filename = Path(path).stem
                semantic_key = filename.lower().replace("phase", "").replace("_", "").replace("-", "")
                phases[phase_key][semantic_key] = optional(path)

    return phases


def load_ssot_surface() -> dict[str, Any] | None:
    """Load SSOT surface for canonical phase state."""
    if not SSOT_SURFACE_PATH.exists():
        return None
    try:
        with open(SSOT_SURFACE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def check_alignment_status() -> str:
    """Check DMS-Share alignment status via guard."""
    import subprocess

    try:
        # Run guard in HINT mode to get report (JSON output)
        result = subprocess.run(
            ["python3", "scripts/guards/guard_dms_share_alignment.py", "--mode", "HINT"],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        return data.get("dms_share_alignment", "UNKNOWN")
    except Exception:
        return "UNKNOWN"


def main() -> int:
    branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip() or None
    ts = datetime.now(UTC).isoformat()

    # Discover phase files dynamically
    print(f"[PM_BOOTSTRAP] Discovering phase files in {SSOT}...")
    phase_files = discover_phase_files()
    print(f"[PM_BOOTSTRAP] Found {len(phase_files)} phase files")

    # Load KB registry if available
    registry = load_kb_registry()
    if registry:
        print(f"[PM_BOOTSTRAP] Loaded KB registry with {len(registry.get('documents', []))} documents")
    else:
        print("[PM_BOOTSTRAP] KB registry not found, using file discovery only")

    # Build phase structure
    phases = build_phase_structure(phase_files, registry)

    # Load SSOT surface
    ssot_surface = load_ssot_surface() or {}
    if not ssot_surface:
        print("[PM_BOOTSTRAP] WARNING: SSOT_SURFACE not found. Phase state may be stale.")

    data = {
        "version": "2025-12-03",
        "generated_at_utc": ts,
        "branch": branch,
        "description": "Minimal PM bootstrap index for new chats. All paths are repo-relative. Phases are auto-discovered.",
        "core_governance": {
            "pm_contract": optional("docs/SSOT/PM_CONTRACT.md"),
            "execution_contract": optional("docs/SSOT/EXECUTION_CONTRACT.md"),
            "cursor_behavior_patch": optional("docs/SSOT/CURSOR_BEHAVIORAL_PATCH.md"),
        },
        "gotchas": {
            "index": optional("docs/SSOT/GOTCHAS_INDEX.md"),
            "share_folder": optional("docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md"),
            "share_gate_status": optional("docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md"),
        },
        "projects": {
            "inventory": optional("docs/SSOT/PROJECTS_INVENTORY.md"),
        },
        "infra": {
            "housekeeping_gpu": optional("docs/SSOT/HOUSEKEEPING_GPU_ACCELERATION.md"),
            "housekeeping_perf": optional("docs/SSOT/HOUSEKEEPING_PERFORMANCE_OPTIMIZATION.md"),
            "postgres_review": optional("docs/SSOT/POSTGRES_OPTIMIZATION_REVIEW.md"),
            "dsn_governance": optional("docs/SSOT/GEMATRIA_DSN_GOVERNANCE.md"),
        },
        "phases": phases,
        "surfaces": {
            "ssot_surface": optional("share/SSOT_SURFACE_V17.json"),
            "phase16_purge_plan": optional("docs/SSOT/PHASE16_LEGACY_PURGE_PLAN.md"),
            "kb_registry": optional("share/kb_registry.json"),
        },
        "meta": {
            "current_phase": ssot_surface.get("current_phase", "23"),
            "last_completed_phase": ssot_surface.get("last_completed_phase", "23"),
            "kb_registry_path": "share/kb_registry.json",
            "dms_share_alignment": ssot_surface.get("dms_share_alignment", check_alignment_status()),
        },
        "kb": {
            "registry_course_correction": optional("docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md"),
            "share_layout_phase15": optional("docs/SSOT/PM_SHARE_LAYOUT_PHASE15.md"),
        },
        "notes": [
            "This file is the only thing a new PM chat strictly needs to start.",
            "If a path is null, that doc does not exist in this branch.",
            "Generated by scripts/pm/generate_pm_bootstrap_state.py.",
            "Phases are auto-discovered from docs/SSOT/PHASE*.md files.",
            "KB registry is used as canonical source when available (ssot + high importance).",
            "Phase 17: Post-purge SSOT surface regeneration and bootstrap refresh.",
        ],
        "webui": {
            "console_v2": {
                "source": "webui/orchestrator-console-v2/",
                "schema": optional("share/orchestrator/CONSOLE_SCHEMA.json"),
                "view_model": optional("share/orchestrator/VIEW_MODEL.json"),
                "dev_server": optional("scripts/dev/serve_console_v2.py"),
                "ci_check": optional("scripts/pm/check_console_v2.py"),
                "dev_url": "http://localhost:8080/console-v2/",
                "surfaces_consumed": [
                    optional("share/SSOT_SURFACE_V17.json"),
                    optional("share/PM_BOOTSTRAP_STATE.json"),
                    optional("share/PHASE18_INDEX.md"),
                    optional("share/PHASE18_AGENTS_SYNC_SUMMARY.json"),
                    optional("share/PHASE18_SHARE_EXPORTS_SUMMARY.json"),
                    optional("share/PHASE18_LEDGER_REPAIR_SUMMARY.json"),
                    optional("share/PHASE19_SHARE_HYGIENE_SUMMARY.json"),
                    optional("share/PHASE20_UI_RESET_DECISION.md"),
                    optional("share/PHASE20_ORCHESTRATOR_UI_MODEL.md"),
                    optional("share/PHASE21_CONSOLE_SERVE_PLAN.md"),
                    optional("share/orchestrator/STATE.json"),
                    optional("share/orchestrator_assistant/STATE.json"),
                    optional("share/atlas/control_plane/system_health.json"),
                    optional("share/atlas/control_plane/lm_indicator.json"),
                    optional("share/exports/docs-control/canonical.json"),
                    optional("share/exports/docs-control/summary.json"),
                    optional("share/kb_registry.json"),
                ],
            }
        },
    }

    # Drop keys with null values to keep the file small
    def prune(obj):
        if isinstance(obj, dict):
            return {k: prune(v) for k, v in obj.items() if v is not None}
        if isinstance(obj, list):
            return [prune(x) for x in obj]
        return obj

    pruned = prune(data)
    SHARE.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(pruned, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[PM_BOOTSTRAP] Wrote {OUT.relative_to(ROOT)} with {len(phases)} phases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
