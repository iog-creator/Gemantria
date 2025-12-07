"""
oa.tools.boot

OA-facing wrappers around pmagent boot commands.

OA (Orchestrator Assistant) should NEVER shell out directly in prompts.
Instead, the runtime or backend should expose these Python functions as tools.

Functions:

* get_kernel_status() -> dict
* get_pm_boot_envelope() -> dict

Implementation:

* Calls `pmagent handoff status-handoff --json`
* Calls `pmagent handoff boot-pm --json`
* Returns parsed JSON dicts

Behavior must match:

* docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md
* docs/SSOT/PHASE26_OA_BOOT_SPEC.md
* docs/SSOT/ORCHESTRATOR_REALITY.md
"""

from __future__ import annotations

import json
import subprocess
from typing import Any, Dict


def _run_json(cmd: list[str]) -> Dict[str, Any]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from command: {' '.join(cmd)}") from e


def get_kernel_status() -> Dict[str, Any]:
    """
    Return the kernel status envelope from `pmagent handoff status-handoff --json`.
    """
    return _run_json(["pmagent", "handoff", "status-handoff", "--json"])


def get_pm_boot_envelope() -> Dict[str, Any]:
    """
    Return the PM boot envelope from `pmagent handoff boot-pm --mode json`.
    """
    return _run_json(["pmagent", "handoff", "boot-pm", "--mode", "json"])
