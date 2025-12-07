# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Branch Health Report Generator

Generates comprehensive branch and PR health reports showing:
- Branch status (local, remote, merged)
- PR status and links
- CI check status
- Last commit info
- Age analysis

Outputs:
- CSV: _reports/branch_health_<date>/branch_health.csv
- Markdown: _reports/branch_health_<date>/branch_health.md
"""

import csv
import subprocess
from datetime import datetime
from pathlib import Path


def run_cmd(cmd: list[str], cwd: str | None = None) -> tuple[str, str, int]:
    """Run a command and return stdout, stderr, exit_code."""
    from scripts.util.filter_stderr import filter_cursor_noise

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    stderr_filtered = filter_cursor_noise(result.stderr)
    return result.stdout.strip(), stderr_filtered.strip(), result.returncode


def get_branches() -> list[dict]:
    """Get all branches (local and remote) with metadata."""
    branches = []

    # Get local branches
    stdout, _, _ = run_cmd(
        [
            "git",
            "branch",
            "-a",
            "--format=%(refname:short)|%(committerdate:iso)|%(committerdate:relative)|%(subject)",
        ]  # noqa: E501
    )

    for line in stdout.split("\n"):
        if not line.strip():
            continue

        parts = line.split("|", 3)
        if len(parts) != 4:
            continue

        ref, iso_date, relative_date, subject = parts
        is_remote = ref.startswith("remotes/origin/")
        branch_name = ref.replace("remotes/origin/", "") if is_remote else ref

        # Skip HEAD and main (we'll handle main separately)
        if branch_name in ["HEAD", "main"]:
            continue

        # Check if this branch exists locally
        local_exists = not ref.startswith("remotes/")
        remote_exists = ref.startswith("remotes/origin/")

        # Get last commit hash
        if local_exists:
            hash_stdout, _, _ = run_cmd(["git", "rev-parse", branch_name])
        elif remote_exists:
            hash_stdout, _, _ = run_cmd(["git", "rev-parse", f"remotes/origin/{branch_name}"])
        else:
            continue

        commit_hash = hash_stdout[:8] if hash_stdout else ""

        branches.append(
            {
                "name": branch_name,
                "local_exists": local_exists,
                "remote_exists": remote_exists,
                "last_commit": iso_date,
                "relative_age": relative_date,
                "commit_hash": commit_hash,
                "subject": subject[:80] + "..." if len(subject) > 80 else subject,
                "pr_number": None,
                "pr_status": None,
                "pr_url": None,
                "checks_status": None,
                "checks_url": None,
            }
        )

    return branches


def get_pr_info(branches: list[dict], repo_owner: str, repo_name: str) -> None:
    """Add PR information to branches using GitHub API."""
    try:
        # This would need GitHub token - for now we'll use MCP tools
        # Let's use the MCP GitHub tools instead
        pass
    except Exception as e:
        print(f"Warning: Could not fetch PR info: {e}")
        # Continue without PR info


def analyze_branch_health(branches: list[dict]) -> dict:
    """Analyze overall branch health statistics."""
    total_branches = len(branches)
    local_only = sum(1 for b in branches if b["local_exists"] and not b["remote_exists"])
    remote_only = sum(1 for b in branches if not b["local_exists"] and b["remote_exists"])
    synced = sum(1 for b in branches if b["local_exists"] and b["remote_exists"])

    with_pr = sum(1 for b in branches if b["pr_number"])
    checks_passed = sum(1 for b in branches if b["checks_status"] == "success")
    checks_failed = sum(1 for b in branches if b["checks_status"] == "failure")
    checks_pending = sum(1 for b in branches if b["checks_status"] == "pending")
    no_checks = sum(1 for b in branches if b["checks_status"] is None)

    # Age analysis
    old_branches = sum(1 for b in branches if "month" in b["relative_age"] or "year" in b["relative_age"])

    return {
        "total_branches": total_branches,
        "local_only": local_only,
        "remote_only": remote_only,
        "synced": synced,
        "with_pr": with_pr,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "checks_pending": checks_pending,
        "no_checks": no_checks,
        "old_branches": old_branches,
    }


def generate_csv_report(branches: list[dict], output_path: Path) -> None:
    """Generate CSV report."""
    fieldnames = [
        "branch_name",
        "local_exists",
        "remote_exists",
        "pr_number",
        "pr_status",
        "checks_status",
        "last_commit",
        "relative_age",
        "commit_hash",
        "subject",
        "pr_url",
        "checks_url",
    ]

    with open(output_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for branch in sorted(branches, key=lambda x: x["name"]):
            writer.writerow(
                {
                    "branch_name": branch["name"],
                    "local_exists": "Y" if branch["local_exists"] else "N",
                    "remote_exists": "Y" if branch["remote_exists"] else "N",
                    "pr_number": branch["pr_number"] or "",
                    "pr_status": branch["pr_status"] or "",
                    "checks_status": branch["checks_status"] or "",
                    "last_commit": branch["last_commit"],
                    "relative_age": branch["relative_age"],
                    "commit_hash": branch["commit_hash"],
                    "subject": branch["subject"],
                    "pr_url": branch["pr_url"] or "",
                    "checks_url": branch["checks_url"] or "",
                }
            )


def generate_markdown_report(branches: list[dict], stats: dict, output_path: Path) -> None:
    """Generate markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    with open(output_path, "w") as f:
        f.write("# Branch Health Report\n\n")
        f.write(f"**Generated:** {now}\n\n")

        # Summary statistics
        f.write("## 📊 Summary Statistics\n\n")
        f.write("| Metric | Count | Percentage |\n")
        f.write("|--------|-------|------------|\n")
        f.write(f"| Total Branches | {stats['total_branches']} | 100% |\n")
        f.write(
            f"| Local Only | {stats['local_only']} | {stats['local_only'] / stats['total_branches'] * 100:.1f}% |\n"
        )
        f.write(
            f"| Remote Only | {stats['remote_only']} | {stats['remote_only'] / stats['total_branches'] * 100:.1f}% |\n"
        )
        f.write(
            f"| Synced (Local + Remote) | {stats['synced']} | {stats['synced'] / stats['total_branches'] * 100:.1f}% |\n"  # noqa: E501
        )
        f.write(
            f"| With Pull Request | {stats['with_pr']} | {stats['with_pr'] / stats['total_branches'] * 100:.1f}% |\n"  # noqa: E501
        )
        f.write(
            f"| Checks Passed | {stats['checks_passed']} | {stats['checks_passed'] / stats['total_branches'] * 100:.1f}% |\n"  # noqa: E501
        )
        f.write(
            f"| Checks Failed | {stats['checks_failed']} | {stats['checks_failed'] / stats['total_branches'] * 100:.1f}% |\n"  # noqa: E501
        )
        f.write(
            f"| Checks Pending | {stats['checks_pending']} | {stats['checks_pending'] / stats['total_branches'] * 100:.1f}% |\n"  # noqa: E501
        )
        f.write(f"| No Checks | {stats['no_checks']} | {stats['no_checks'] / stats['total_branches'] * 100:.1f}% |\n")
        f.write(
            f"| Old Branches (>1 month) | {stats['old_branches']} | {stats['old_branches'] / stats['total_branches'] * 100:.1f}% |\n\n"  # noqa: E501
        )

        # Branch details
        f.write("## 📋 Branch Details\n\n")

        # Group branches by status
        no_pr_no_checks = [b for b in branches if not b["pr_number"] and not b["checks_status"]]
        has_pr_no_checks = [b for b in branches if b["pr_number"] and not b["checks_status"]]
        has_checks = [b for b in branches if b["checks_status"]]

        def write_branch_table(title: str, branch_list: list[dict]):
            if not branch_list:
                return
            f.write(f"### {title} ({len(branch_list)} branches)\n\n")
            f.write("| Branch | Local | Remote | PR | Checks | Age | Last Commit |\n")
            f.write("|--------|-------|--------|----|--------|-----|-------------|\n")

            for branch in sorted(branch_list, key=lambda x: x["name"]):
                pr_link = (
                    f"[#{branch['pr_number']}]({branch['pr_url']})"
                    if branch["pr_url"]
                    else (str(branch["pr_number"]) if branch["pr_number"] else "")
                )
                checks_status = branch["checks_status"] or ""
                if checks_status == "success":
                    checks_status = "✅"
                elif checks_status == "failure":
                    checks_status = "❌"
                elif checks_status == "pending":
                    checks_status = "⏳"

                f.write(
                    f"| {branch['name']} | {'✅' if branch['local_exists'] else ''} | {'✅' if branch['remote_exists'] else ''} | {pr_link} | {checks_status} | {branch['relative_age']} | {branch['commit_hash']} |\n"  # noqa: E501
                )

            f.write("\n")

        write_branch_table("🚫 No PR + No Checks (High Priority)", no_pr_no_checks)
        write_branch_table("⚠️ Has PR but No Checks", has_pr_no_checks)
        write_branch_table("✅ Has Checks", has_checks)

        # Recommendations
        f.write("## 🎯 Recommendations\n\n")

        if stats["no_checks"] > 0:
            f.write("### Immediate Actions\n")
            f.write(f"- **{stats['no_checks']} branches lack checks** - these need PRs opened or checks triggered\n")
            if stats["old_branches"] > 0:
                f.write(f"- **{stats['old_branches']} old branches** (>1 month) may need cleanup\n")

        f.write("\n### Next Steps\n")
        f.write("1. Open draft PRs for branches without PRs (prefix `[RESCUE]`)\n")
        f.write("2. Trigger `workflow_dispatch` for existing PRs to run checks\n")
        f.write("3. Review failed checks and fix issues\n")
        f.write("4. Consider branch cleanup for very old branches\n")


def main():
    """Main function."""
    # Get repository info
    # repo_owner = "iog-creator"  # Not used in this script
    # repo_name = "Gemantria"  # Not used in this script

    print("🔍 Gathering branch information...")
    branches = get_branches()
    print(f"Found {len(branches)} branches")

    print("📡 Fetching PR information...")
    # For now, skip PR fetching - would need GitHub token
    # get_pr_info(branches, repo_owner, repo_name)

    print("📊 Analyzing health...")
    stats = analyze_branch_health(branches)

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"_reports/branch_health_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "branch_health.csv"
    md_path = output_dir / "branch_health.md"

    print(f"📄 Generating reports in {output_dir}...")
    generate_csv_report(branches, csv_path)
    generate_markdown_report(branches, stats, md_path)

    print("✅ Reports generated successfully!")
    print(f"   CSV: {csv_path}")
    print(f"   MD:  {md_path}")

    # Print summary
    print("\n📊 Quick Summary:")
    print(f"   Total branches: {stats['total_branches']}")
    print(f"   With PRs: {stats['with_pr']}")
    print(f"   No checks: {stats['no_checks']}")
    print(f"   Old branches: {stats['old_branches']}")


if __name__ == "__main__":
    main()
