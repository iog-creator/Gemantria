#!/usr/bin/env python3
"""
prepare_handoff.py — Generate Rule 051 handoff content for new chat sessions.

Generates the complete handoff evidence set per Rule 051 (Cursor Insight & Handoff)
and copies it to clipboard for easy pasting into a new Cursor chat.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Try to import clipboard library, fallback to platform-specific commands
try:
    import pyperclip

    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


def run_cmd(cmd: list[str], capture_output: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=True, check=False, timeout=30)
        # Filter Cursor IDE integration noise (orchestrator-friendly output)
        stderr_filtered = (
            "\n".join(line for line in result.stderr.split("\n") if "dump_bash_state: command not found" not in line)
            if capture_output and result.stderr
            else result.stderr
        )
        return result.returncode, result.stdout.strip(), stderr_filtered.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def get_git_info() -> dict[str, str]:
    """Collect git repository information."""
    repo_root = ""
    branch = ""
    status = ""

    _, repo_root, _ = run_cmd(["git", "rev-parse", "--show-toplevel"])
    _, branch, _ = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    _, status, _ = run_cmd(["git", "status", "-sb"])

    return {
        "repo_root": repo_root,
        "branch": branch,
        "status": status,
    }


def get_active_pr() -> dict | None:
    """Get active PR information if on a PR branch."""
    git_info = get_git_info()
    branch = git_info["branch"]

    # Try to detect PR branch pattern (e.g., feature/123, pr/123, or check gh)
    _, pr_list, _ = run_cmd(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--head",
            branch,
            "--json",
            "number,title,headRefName,baseRefName",
            "--limit",
            "1",
        ]
    )

    if pr_list:
        try:
            prs = json.loads(pr_list)
            if prs:
                return prs[0]
        except json.JSONDecodeError:
            pass

    return None


def generate_handoff_content() -> str:
    """Generate the complete handoff content per Rule 051."""
    git_info = get_git_info()
    pr_info = get_active_pr()
    timestamp = datetime.now().isoformat()

    # Build the handoff content
    lines = [
        "# Handoff — Rule 051 (Cursor Insight & Handoff)",
        f"Generated: {timestamp}",
        "",
        "## Goal",
        "Continue work from previous chat session with full context and baseline evidence.",
        "",
        "## Baseline Evidence",
        "",
        "### 1. Repository Information",
        "```bash",
        "git rev-parse --show-toplevel",
        "```",
        f"**Output:** `{git_info['repo_root']}`",
        "",
        "```bash",
        "git rev-parse --abbrev-ref HEAD",
        "```",
        f"**Output:** `{git_info['branch']}`",
        "",
        "```bash",
        "git status -sb",
        "```",
        "**Output:**",
        "```",
        git_info["status"],
        "```",
        "",
        "### 2. Hermetic Test Bundle",
        "",
        "```bash",
        "ruff format --check . && ruff check .",
        "```",
        "*Run and paste output*",
        "",
        "```bash",
        "make book.smoke",
        "```",
        "*Run and paste output*",
        "",
        "```bash",
        "make ci.exports.smoke",
        "```",
        "*Run and paste output*",
        "",
    ]

    # Add PR information if available
    if pr_info:
        pr_num = pr_info["number"]
        lines.extend(
            [
                "### 3. Active PR Information",
                "",
                f"**PR #{pr_num}:** {pr_info.get('title', 'N/A')}",
                f"**Branch:** {pr_info.get('headRefName', 'N/A')} → {pr_info.get('baseRefName', 'N/A')}",
                "",
                "```bash",
                f"gh pr view {pr_num} --json number,title,headRefName,baseRefName,state,author,reviews,reviewDecision,mergeable,mergeStateStatus,checks",
                "```",
                "*Run and paste output*",
                "",
                "```bash",
                f"gh pr checks {pr_num} --required --json name,state",
                "```",
                "*Run and paste output*",
                "",
            ]
        )

    lines.extend(
        [
            "## Next Steps",
            "",
            "1. Run the commands above and paste their outputs",
            "2. Review git status and PR state (if applicable)",
            "3. Continue with the next task",
            "",
            "---",
            "",
            "*Source: AGENTS.md + RULES_INDEX.md + .cursor/rules/050 + .cursor/rules/051*",
        ]
    )

    return "\n".join(lines)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using available method."""
    if HAS_PYPERCLIP:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            pass

    # Fallback to platform-specific commands
    platform = sys.platform
    try:
        if platform == "darwin":  # macOS
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True
        elif platform == "linux":
            # Try xclip first, then xsel
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        elif platform == "win32":  # Windows
            subprocess.run(["clip"], input=text, text=True, check=True)
            return True
    except Exception:
        pass

    return False


def main():
    """Main entry point."""
    print("🔄 Preparing handoff content (Rule 051)...")
    print()

    # Generate handoff content
    content = generate_handoff_content()

    # Copy to clipboard
    if copy_to_clipboard(content):
        print("✅ Handoff content copied to clipboard!")
        print()
        print("📋 Next steps:")
        print("   1. Open a new Cursor chat tab (Cmd/Ctrl + L, then click 'New Chat')")
        print("   2. Paste the handoff content (Cmd/Ctrl + V)")
        print("   3. The new chat will have full context")
        print()
    else:
        print("⚠️  Could not copy to clipboard automatically.")
        print("   Please copy the content below manually:")
        print()
        print("=" * 80)
        print(content)
        print("=" * 80)
        return 1

    # Also save to file for reference
    handoff_file = Path("share/handoff_latest.md")
    handoff_file.parent.mkdir(parents=True, exist_ok=True)
    handoff_file.write_text(content)
    print(f"💾 Handoff also saved to: {handoff_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
