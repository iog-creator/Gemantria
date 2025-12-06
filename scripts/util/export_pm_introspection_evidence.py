#!/usr/bin/env python3
"""
PM System Introspection Evidence Pack Generator

Generates a comprehensive evidence pack describing how the pmagent + AGENTS +
share + planning + KB + tracking/self-healing systems currently work together.
This is a raw evidence bundle for PM analysis, not a designed doc.

Usage:
    python scripts/util/export_pm_introspection_evidence.py [--output <path>]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

OUT_DIR = REPO / "share"
OUT_FILE = OUT_DIR / "pm_system_introspection_evidence.md"


def run_cmd(cmd: list[str] | str, capture_output: bool = True) -> tuple[str, int]:
    """Run a command and return output and exit code."""
    try:
        if isinstance(cmd, str):
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                cwd=REPO,
                timeout=60,
            )
        else:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                cwd=REPO,
                timeout=60,
            )
        output = result.stdout if capture_output else ""
        return output, result.returncode
    except subprocess.TimeoutExpired:
        return "(command timed out)", 1
    except Exception as e:
        return f"(command failed: {e})", 1


def get_git_status() -> str:
    """Get git status output."""
    output, _ = run_cmd(["git", "status", "-sb"])
    return output


def get_pmagent_help() -> dict[str, str]:
    """Get all pmagent command help text."""
    helps = {}
    commands = [
        ("pmagent", "--help"),
        ("pmagent plan", "--help"),
        ("pmagent kb", "--help"),
        ("pmagent status", "--help"),
        ("pmagent status snapshot", "--help"),
        ("pmagent status kb", "--help"),
        ("pmagent status explain", "--help"),
        ("pmagent hints", "--help"),
        ("pmagent health", "--help"),
        ("pmagent health system", "--help"),
        ("pmagent reality-check", "--help"),
        ("pmagent reality-check check", "--help"),
    ]
    for cmd, flag in commands:
        full_cmd = f"{cmd} {flag}"
        output, _ = run_cmd(full_cmd)
        helps[cmd] = output
    return helps


def get_planning_state() -> dict[str, str]:
    """Get current planning state."""
    state = {}
    commands = [
        ("pmagent plan next --with-status", "plan_next_with_status"),
        ("pmagent plan history --limit 10", "plan_history"),
        ("pmagent plan next --json-only", "plan_next_json"),
    ]
    for cmd, key in commands:
        output, _ = run_cmd(cmd)
        state[key] = output
    return state


def get_status_snapshots() -> dict[str, str]:
    """Get status snapshots."""
    snapshots = {}
    commands = [
        ("pmagent status kb --json-only", "status_kb"),
        ("pmagent status explain --json-only", "status_explain"),
        ("pmagent health system --json-only", "health_system"),
        ("pmagent reality-check check --mode hint --json-only", "reality_check_hint"),
    ]
    for cmd, key in commands:
        output, _ = run_cmd(cmd)
        snapshots[key] = output
    return snapshots


def get_agents_samples() -> dict[str, str]:
    """Get AGENTS.md samples."""
    samples = {}
    # Core AGENTS.md
    agents_md = REPO / "AGENTS.md"
    if agents_md.exists():
        content = agents_md.read_text()
        samples["AGENTS.md_head"] = "\n".join(content.split("\n")[:200])
    # scripts_AGENTS.md
    scripts_agents = REPO / "scripts_AGENTS.md"
    if scripts_agents.exists():
        content = scripts_agents.read_text()
        samples["scripts_AGENTS.md_head"] = "\n".join(content.split("\n")[:200])
    # Sample from share/agents_md
    agents_md_dir = REPO / "share" / "agents_md"
    if agents_md_dir.exists():
        md_files = list(agents_md_dir.glob("*.md"))[:3]
        for md_file in md_files:
            content = md_file.read_text()
            samples[f"share_agents_md_{md_file.stem}"] = "\n".join(content.split("\n")[:160])
    return samples


def get_codebase_refs() -> dict[str, str]:
    """Get codebase references via ripgrep."""
    refs = {}
    searches = [
        ("tracking agent", "tracking_agent_refs"),
        ("envelope", "envelope_refs"),
        ("housekeeping", "housekeeping_refs"),
        ("pm.snapshot", "pm_snapshot_refs"),
        ("planning_context", "planning_context_refs"),
        ("kb_registry", "kb_registry_refs"),
        ("hint_registry", "hint_registry_refs"),
        ("reality.check", "reality_check_refs"),
        ("self-healing", "self_healing_refs"),
        ("gotchas", "gotchas_refs"),
    ]
    for pattern, key in searches:
        output, _ = run_cmd(f"rg '{pattern}' -n pmagent scripts docs .cursor 2>/dev/null | head -100")
        refs[key] = output
    return refs


def get_contracts_heads() -> dict[str, str]:
    """Get head sections from contract/gotchas docs."""
    heads = {}
    docs = [
        ("docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md", "PM_SHARE_FOLDER_GOTCHAS"),
        ("docs/SSOT/PM_CONTRACT.md", "PM_CONTRACT"),
        ("docs/SSOT/PM_CONTRACT_STRICT_SSOT_DMS.md", "PM_CONTRACT_STRICT"),
        ("MASTER_PLAN.md", "MASTER_PLAN"),
        ("NEXT_STEPS.md", "NEXT_STEPS"),
        ("docs/SSOT/SHARE_FOLDER_STRUCTURE.md", "SHARE_FOLDER_STRUCTURE"),
    ]
    for path, key in docs:
        doc_path = REPO / path
        if doc_path.exists():
            content = doc_path.read_text()
            heads[key] = "\n".join(content.split("\n")[:260])
    return heads


def get_share_folder_contents() -> dict[str, Any]:
    """Get share folder structure and key file info."""
    share_dir = REPO / "share"
    contents = {
        "total_files": 0,
        "json_files": [],
        "md_files": [],
        "directories": [],
    }
    if share_dir.exists():
        for item in share_dir.iterdir():
            if item.is_file():
                contents["total_files"] += 1
                if item.suffix == ".json":
                    contents["json_files"].append(item.name)
                elif item.suffix == ".md":
                    contents["md_files"].append(item.name)
            elif item.is_dir():
                contents["directories"].append(item.name)
    # Limit lists for readability
    contents["json_files"] = sorted(contents["json_files"])[:50]
    contents["md_files"] = sorted(contents["md_files"])[:50]
    contents["directories"] = sorted(contents["directories"])[:20]
    return contents


def generate_evidence_pack() -> str:
    """Generate the complete evidence pack markdown."""
    lines = [
        "# PM System Introspection — Raw Evidence Bundle",
        "",
        "This file aggregates raw evidence about how the pmagent + AGENTS + share +",
        "planning + KB + tracking/self-healing systems currently behave. It is NOT a",
        "designed doc; it is an evidence pack for the PM to read and interpret.",
        "",
        f"**Generated**: {datetime.now(UTC).isoformat()}",
        "",
        "## 1. Repo / branch / status",
        "",
        "```",
        get_git_status(),
        "```",
        "",
        "## 2. pmagent commands (help text)",
        "",
    ]
    # Add all help text
    helps = get_pmagent_help()
    for cmd, help_text in helps.items():
        lines.extend(
            [
                f"### {cmd}",
                "",
                "```",
                help_text,
                "```",
                "",
            ]
        )
    # Planning state
    lines.extend(
        [
            "## 3. Current planning state",
            "",
        ]
    )
    planning = get_planning_state()
    for key, output in planning.items():
        lines.extend(
            [
                f"### {key}",
                "",
                "```",
                output,
                "```",
                "",
            ]
        )
    # Status snapshots
    lines.extend(
        [
            "## 4. Status snapshots (JSON)",
            "",
        ]
    )
    snapshots = get_status_snapshots()
    for key, output in snapshots.items():
        lines.extend(
            [
                f"### {key}",
                "",
                "```json",
                output,
                "```",
                "",
            ]
        )
    # AGENTS samples
    lines.extend(
        [
            "## 5. AGENTS docs (core and samples)",
            "",
        ]
    )
    agents = get_agents_samples()
    for key, content in agents.items():
        lines.extend(
            [
                f"### {key}",
                "",
                "```",
                content,
                "```",
                "",
            ]
        )
    # Codebase refs
    lines.extend(
        [
            "## 6. Tracking / self-healing references (rg outputs)",
            "",
        ]
    )
    refs = get_codebase_refs()
    for key, output in refs.items():
        lines.extend(
            [
                f"### {key}",
                "",
                "```",
                output if output.strip() else "(no references found)",
                "```",
                "",
            ]
        )
    # Contracts/gotchas
    lines.extend(
        [
            "## 7. Gotchas and contracts (heads)",
            "",
        ]
    )
    contracts = get_contracts_heads()
    for key, content in contracts.items():
        lines.extend(
            [
                f"### {key}",
                "",
                "```",
                content,
                "```",
                "",
            ]
        )
    # Share folder structure
    lines.extend(
        [
            "## 8. Share folder structure",
            "",
            "```json",
            json.dumps(get_share_folder_contents(), indent=2),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description="Generate PM system introspection evidence pack")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: share/pm_system_introspection_evidence.md)",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = args.output or OUT_FILE

    try:
        evidence = generate_evidence_pack()
        output_file.write_text(evidence)
        print(f"✅ PM system introspection evidence pack generated: {output_file}")
        print(f"   Size: {len(evidence)} characters, {len(evidence.splitlines())} lines")
        return 0
    except Exception as e:
        print(f"❌ Failed to generate evidence pack: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
