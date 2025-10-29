#!/usr/bin/env python3
import json
import os
import pathlib
import time
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_EVAL = ROOT / "share" / "eval"
EVAL_OUTDIR = os.environ.get("EVAL_OUTDIR")
EVAL = (ROOT / EVAL_OUTDIR) if EVAL_OUTDIR else DEFAULT_EVAL
OUT = EVAL / "release_notes.md"


def main():
    print("[eval.release_notes] starting")

    EVAL.mkdir(parents=True, exist_ok=True)

    # Load various report files
    reports = {}

    # Load main report
    report_json = EVAL / "report.json"
    if report_json.exists():
        try:
            reports["main"] = json.loads(report_json.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[eval.release_notes] WARN could not load report.json: {e}")

    # Load history if available
    history_json = EVAL / "history.json"
    if history_json.exists():
        try:
            reports["history"] = json.loads(history_json.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[eval.release_notes] WARN could not load history.json: {e}")

    # Generate release notes
    now = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    content = f"""# Release Notes

Generated: {now}

## Summary

"""

    # Add summary from main report
    if "main" in reports:
        summary = reports["main"].get("summary", {})
        ok_count = summary.get("ok_count", 0)
        fail_count = summary.get("fail_count", 0)
        total = ok_count + fail_count

        content += f"- **Total Tasks**: {total}\n"
        content += f"- **Passed**: {ok_count}\n"
        content += f"- **Failed**: {fail_count}\n"

        if total > 0:
            pass_rate = (ok_count / total) * 100
            content += f"- **Pass Rate**: {pass_rate:.1f}%\n"

    content += "\n## Recent Changes\n\n"

    # Add recent task history
    if "history" in reports:
        history = reports["history"]
        task_history = history.get("task_history", [])

        if task_history:
            content += "### Task Execution Summary\n\n"
            content += "| Task | Status | Duration | Time |\n"
            content += "|------|--------|----------|------|\n"

            # Show last 10 tasks
            for task in task_history[-10:]:
                key = task.get("key", "unknown")
                status = task.get("status", "unknown")
                duration = f"{task.get('duration_ms', 0)}ms"
                timestamp = task.get("timestamp", "unknown")
                content += f"| {key} | {status} | {duration} | {timestamp} |\n"

    content += "\n## Notes\n\n"
    content += "- This release includes automated quality checks and validation.\n"
    content += "- All metrics are based on current evaluation results.\n"

    OUT.write_text(content, encoding="utf-8")
    print(f"[eval.release_notes] wrote {OUT.relative_to(ROOT)}")
    print("[eval.release_notes] done")


if __name__ == "__main__":
    exit(main() or 0)
