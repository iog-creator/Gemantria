#!/usr/bin/env python3
import json
import pathlib
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "share" / "eval" / "report.json"
REMEDIATION_PLAN = ROOT / "share" / "eval" / "remediation_plan.json"
REMEDIATION_MD = ROOT / "share" / "eval" / "remediation_plan.md"


def _load_report() -> dict[str, Any]:
    if not REPORT_JSON.exists():
        return {}
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _analyze_failures(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Analyze failed tasks and generate remediation suggestions."""
    results = report.get("results", [])
    failed_tasks = [r for r in results if r.get("status") != "OK"]

    remediations = []

    for task in failed_tasks:
        key = task["key"]
        kind = task["kind"]

        # Generate specific remediation based on task type and failure
        if kind == "file_glob":
            missing = task.get("missing", [])
            if missing:
                remediations.append(
                    {
                        "task_key": key,
                        "issue": f"Missing files matching globs: {missing}",
                        "severity": "high",
                        "category": "data_integrity",
                        "suggested_actions": [
                            "Check if pipeline has completed successfully",
                            "Verify export generation completed",
                            f"Run `make go` to regenerate missing files: {missing}",
                            "Check logs for export generation errors",
                        ],
                        "automated_fix_available": True,
                        "fix_command": "make go",
                        "estimated_effort": "medium",
                    }
                )

        elif kind == "json_assert":
            checks = task.get("checks", [])
            failed_checks = [c for c in checks if c.get("status") != "OK"]
            for check in failed_checks:
                check_name = check.get("name", "unnamed check")
                op = check.get("op", "unknown")

                if op == "not_null_all":
                    null_indices = check.get("null_indices", [])
                    remediations.append(
                        {
                            "task_key": key,
                            "issue": f"Null values found in {check_name}: {len(null_indices)} null entries",
                            "severity": "high",
                            "category": "data_quality",
                            "suggested_actions": [
                                (
                                    f"Investigate null values at indices: {null_indices[:10]}..."
                                    if len(null_indices) > 10
                                    else f"Investigate null values at indices: {null_indices}"
                                ),
                                "Check pipeline data enrichment steps",
                                "Verify LLM confidence thresholds",
                                "Consider ALLOW_PARTIAL=1 for development",
                            ],
                            "automated_fix_available": False,
                            "estimated_effort": "high",
                        }
                    )

                elif op == "frac_in_range":
                    observed_frac = check.get("observed_frac", 0)
                    min_frac = check.get("min_frac", 0)
                    range_spec = check.get("range", [0, 1])
                    remediations.append(
                        {
                            "task_key": key,
                            "issue": f"Value distribution out of range in {check_name}: {observed_frac:.2%} in "
                            f"[{range_spec[0]}, {range_spec[1]}], minimum required: {min_frac:.2%}",
                            "severity": "medium",
                            "category": "data_distribution",
                            "suggested_actions": [
                                "Review edge strength calculation algorithm",
                                "Check embedding normalization",
                                "Adjust EDGE_ALPHA/EDGE_STRONG/EDGE_WEAK parameters",
                                "Consider algorithmic changes for better distribution",
                            ],
                            "automated_fix_available": False,
                            "estimated_effort": "high",
                        }
                    )

                elif op == "if_present_eq_all":
                    bad_indices = check.get("bad_indices", [])
                    expected = check.get("expected")
                    remediations.append(
                        {
                            "task_key": key,
                            "issue": f"Inconsistent values in {check_name}: {len(bad_indices)} entries "
                            f"don't match expected value {expected}",
                            "severity": "medium",
                            "category": "data_consistency",
                            "suggested_actions": [
                                (
                                    f"Review data generation for consistency at indices: {bad_indices[:10]}..."
                                    if len(bad_indices) > 10
                                    else f"Review data generation for consistency at indices: {bad_indices}"
                                ),
                                "Check embedding dimension configuration",
                                "Verify vector storage and retrieval",
                            ],
                            "automated_fix_available": False,
                            "estimated_effort": "medium",
                        }
                    )

        elif kind == "grep":
            misses = task.get("misses", [])
            if misses:
                remediations.append(
                    {
                        "task_key": key,
                        "issue": f"Required patterns not found: {misses}",
                        "severity": "low",
                        "category": "documentation",
                        "suggested_actions": [
                            f"Add missing patterns to documentation: {misses}",
                            "Update RULES_INDEX.md with new rule entries",
                            "Ensure ADR coverage for any new rules",
                        ],
                        "automated_fix_available": False,
                        "estimated_effort": "low",
                    }
                )

        elif kind == "ref_integrity":
            counts = task.get("counts", {})
            limits = task.get("limits", {})
            missing_endpoints = counts.get("missing_endpoints", 0)
            allow_missing = limits.get("allow_missing_endpoints", 0)

            if missing_endpoints > allow_missing:
                remediations.append(
                    {
                        "task_key": key,
                        "issue": f"Referential integrity violation: {missing_endpoints} missing endpoints "
                        f"(limit: {allow_missing})",
                        "severity": "high" if missing_endpoints > 10 else "medium",
                        "category": "data_integrity",
                        "suggested_actions": [
                            f"Found {missing_endpoints} missing node endpoints in graph",
                            "Run `make eval.repairplan` to generate stub node proposals",
                            "Apply repair plan with `make repair.apply` to add stub nodes",
                            "Re-run evaluation to verify referential integrity",
                            f"Consider ALLOW_PARTIAL=1 if {missing_endpoints} missing endpoints is acceptable",
                        ],
                        "automated_fix_available": True,
                        "fix_command": "make eval.repairplan && make repair.apply",
                        "estimated_effort": "medium",
                    }
                )

        else:
            # Generic remediation for unknown task types
            error = task.get("error", "Unknown failure")
            remediations.append(
                {
                    "task_key": key,
                    "issue": f"Task failed: {error}",
                    "severity": "medium",
                    "category": "unknown",
                    "suggested_actions": [
                        "Review task configuration and parameters",
                        "Check logs for detailed error information",
                        "Verify dependencies and prerequisites",
                    ],
                    "automated_fix_available": False,
                    "estimated_effort": "medium",
                }
            )

    return remediations


def _generate_summary(remediations: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate summary statistics for the remediation plan."""
    categories: dict[str, int] = {}
    severities = {"low": 0, "medium": 0, "high": 0}
    automated_available = 0

    for rem in remediations:
        cat = rem["category"]
        sev = rem["severity"]
        categories[cat] = categories.get(cat, 0) + 1
        severities[sev] = severities.get(sev, 0) + 1
        if rem["automated_fix_available"]:
            automated_available += 1

    return {
        "total_issues": len(remediations),
        "by_category": categories,
        "by_severity": severities,
        "automated_fixes_available": automated_available,
        "estimated_total_effort": (
            "high" if severities["high"] > 0 else "medium" if severities["medium"] > 2 else "low"
        ),
    }


def _write_markdown_plan(remediations: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    """Write remediation plan in human-readable Markdown format."""
    lines = []
    lines.append("# Gemantria Remediation Plan")
    lines.append("")
    lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    lines.append("")
    lines.append(f"**Total Issues:** {summary['total_issues']}")
    lines.append(f"**Automated Fixes Available:** {summary['automated_fixes_available']}")
    lines.append(f"**Estimated Effort:** {summary['estimated_total_effort'].upper()}")
    lines.append("")

    # Summary by severity
    lines.append("## Summary by Severity")
    for sev, count in summary["by_severity"].items():
        if count > 0:
            lines.append(f"- **{sev.upper()}:** {count}")
    lines.append("")

    # Summary by category
    lines.append("## Summary by Category")
    for cat, count in summary["by_category"].items():
        lines.append(f"- **{cat.replace('_', ' ').title()}:** {count}")
    lines.append("")

    # Detailed remediations
    lines.append("## Detailed Remediation Actions")
    lines.append("")

    for i, rem in enumerate(remediations, 1):
        lines.append(f"### {i}. {rem['task_key']} - {rem['severity'].upper()}")
        lines.append("")
        lines.append(f"**Issue:** {rem['issue']}")
        lines.append("")
        lines.append("**Suggested Actions:**")
        for action in rem["suggested_actions"]:
            lines.append(f"- {action}")
        lines.append("")

        if rem["automated_fix_available"]:
            lines.append(f"**Automated Fix:** `{rem['fix_command']}`")
            lines.append("")

        lines.append(f"**Estimated Effort:** {rem['estimated_effort'].upper()}")
        lines.append("")

    REMEDIATION_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("[eval.remediation] starting")

    if not REPORT_JSON.exists():
        print("[eval.remediation] FAIL no report.json found (run make eval.report first)")
        return 2

    report = _load_report()
    if not report:
        print("[eval.remediation] FAIL could not load report")
        return 2

    # Analyze failures and generate remediations
    remediations = _analyze_failures(report)
    summary = _generate_summary(remediations)

    # Create remediation plan
    plan = {
        "version": "1.0",
        "generated_at": int(time.time()),
        "based_on_report": {
            "run_id": report.get("run_id", "unknown"),
            "ok_count": report.get("summary", {}).get("ok_count", 0),
            "fail_count": report.get("summary", {}).get("fail_count", 0),
        },
        "summary": summary,
        "remediations": remediations,
    }

    # Write outputs
    REMEDIATION_PLAN.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")

    _write_markdown_plan(remediations, summary)

    print(f"[eval.remediation] analyzed {summary['total_issues']} issues")
    print(f"[eval.remediation] {summary['automated_fixes_available']} automated fixes available")
    print(f"[eval.remediation] wrote {REMEDIATION_PLAN.relative_to(ROOT)}")
    print(f"[eval.remediation] wrote {REMEDIATION_MD.relative_to(ROOT)}")
    print("[eval.remediation] OK")

    return 0


if __name__ == "__main__":
    import sys  # noqa: E402

    sys.exit(main())
