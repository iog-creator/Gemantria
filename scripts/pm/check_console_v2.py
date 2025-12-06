#!/usr/bin/env python3
"""
Console v2 schema + build check.

Responsibilities:

* Load and validate:
    share/orchestrator/CONSOLE_SCHEMA.json
    share/orchestrator/VIEW_MODEL.json
* Ensure all data_sources paths:
    * start with "share/"
    * exist under the repo's share/ directory
* Optionally run:
    npm run build
    inside webui/orchestrator-console-v2 as a smoke test.

Usage (from repo root):

    python scripts/pm/check_console_v2.py
    python scripts/pm/check_console_v2.py --skip-build

Governance:
    Phase 21.2 — share/PHASE21_CONSOLE_SERVE_PLAN.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
SHARE_ROOT = REPO_ROOT / "share"
CONSOLE_SCHEMA_PATH = SHARE_ROOT / "orchestrator" / "CONSOLE_SCHEMA.json"
VIEW_MODEL_PATH = SHARE_ROOT / "orchestrator" / "VIEW_MODEL.json"
WEBUI_CONSOLE_DIR = REPO_ROOT / "webui" / "orchestrator-console-v2"


class CheckError(Exception):
    """Structured error for console v2 checks."""


def load_json(path: Path) -> Dict:
    """Load and parse a JSON file."""
    if not path.exists():
        raise CheckError(f"Missing required JSON file: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # noqa: BLE001
        raise CheckError(f"Failed to parse JSON file {path}: {exc}") from exc


def iter_data_source_paths(view_model: Dict) -> Iterable[Tuple[str, str]]:
    """
    Yield (key, path_string) for every data_sources entry in VIEW_MODEL.json.

    Handles:
        data_sources.*.path
        data_sources.*.paths[]
    """
    data_sources = view_model.get("data_sources", {})
    if not isinstance(data_sources, dict):
        raise CheckError("VIEW_MODEL.data_sources must be a JSON object")

    for key, value in data_sources.items():
        if not isinstance(value, dict):
            raise CheckError(f"VIEW_MODEL.data_sources['{key}'] must be an object")

        single_path = value.get("path")
        if isinstance(single_path, str):
            yield key, single_path

        multi_paths = value.get("paths")
        if isinstance(multi_paths, list):
            for idx, p in enumerate(multi_paths):
                if isinstance(p, str):
                    yield f"{key}[{idx}]", p
                else:
                    raise CheckError(f"VIEW_MODEL.data_sources['{key}'].paths[{idx}] must be a string")


def validate_path_under_share(label: str, path_str: str) -> None:
    """
    Ensure the given path string starts with "share/" and exists under SHARE_ROOT.

    The VIEW_MODEL paths are expected to be relative strings like:
        "share/SSOT_SURFACE_V17.json"
        "share/orchestrator/STATE.json"
        "share/atlas/control_plane/"
    """
    if not path_str.startswith("share/"):
        raise CheckError(
            f"Data source '{label}' uses path '{path_str}' which does not start with 'share/'. "
            "All console v2 data_sources must be under share/."
        )

    rel = path_str[len("share/") :].lstrip("/")
    target = SHARE_ROOT / rel

    if not target.exists():
        raise CheckError(f"Data source '{label}' points to '{path_str}' but the resolved path does not exist: {target}")


def check_schema_paths() -> int:
    """
    Load CONSOLE_SCHEMA + VIEW_MODEL and validate all data_sources paths.

    Returns the count of validated paths.
    """
    _schema = load_json(CONSOLE_SCHEMA_PATH)  # noqa: F841 — loaded for structure validation
    view_model = load_json(VIEW_MODEL_PATH)

    version = view_model.get("version")
    if version != 2:
        raise CheckError(
            f"Unexpected VIEW_MODEL.version={version!r}; expected 2. "
            "Update this check if the console schema version changes."
        )

    missing: List[str] = []
    path_count = 0

    for label, path_str in iter_data_source_paths(view_model):
        try:
            validate_path_under_share(label, path_str)
            path_count += 1
        except CheckError as exc:
            missing.append(str(exc))

    if missing:
        joined = "\n  - ".join(missing)
        raise CheckError("One or more console v2 data_sources are invalid:\n  - " + joined)

    # Basic sanity: ensure the bindings section exists and has expected structure.
    bindings = view_model.get("bindings", {})
    right_status = bindings.get("right_status", {})
    conversation_sources = bindings.get("conversation", [])

    if not isinstance(right_status, dict):
        raise CheckError("VIEW_MODEL.bindings.right_status must be an object")

    if not isinstance(conversation_sources, list):
        raise CheckError("VIEW_MODEL.bindings.conversation must be a list")

    return path_count


def run_webui_build() -> None:
    """
    Run `npm run build` inside webui/orchestrator-console-v2 as a smoke test.
    """
    if not WEBUI_CONSOLE_DIR.exists():
        raise CheckError(f"Console webui directory does not exist: {WEBUI_CONSOLE_DIR}")

    pkg_json = WEBUI_CONSOLE_DIR / "package.json"
    if not pkg_json.exists():
        raise CheckError(f"package.json not found in console webui directory: {WEBUI_CONSOLE_DIR}")

    try:
        subprocess.run(
            ["npm", "run", "build"],
            cwd=str(WEBUI_CONSOLE_DIR),
            check=True,
        )
    except FileNotFoundError as exc:
        raise CheckError(
            "Failed to run 'npm run build': npm not found in PATH. Ensure Node.js/npm are installed for this check."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise CheckError(f"'npm run build' failed with exit code {exc.returncode}") from exc


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Orchestrator Console v2 schema paths and webui build.")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the npm build smoke test; only validate schema paths.",
    )
    args = parser.parse_args(argv)

    try:
        print("[check_console_v2] Validating schema paths...")
        path_count = check_schema_paths()
        print(f"[check_console_v2] ✓ Schema paths OK ({path_count} paths validated)")

        if not args.skip_build:
            print("[check_console_v2] Running webui build smoke test (npm run build)...")
            run_webui_build()
            print("[check_console_v2] ✓ Webui build completed successfully")
        else:
            print("[check_console_v2] Skipping webui build as requested (--skip-build).")

        return 0
    except CheckError as exc:
        print(f"[check_console_v2] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
