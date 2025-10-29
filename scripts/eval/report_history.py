#!/usr/bin/env python3
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
import os
DEFAULT_OUTDIR = ROOT / "share" / "eval"
ENV_OUTDIR = os.environ.get("EVAL_OUTDIR")
OUTDIR = (ROOT / ENV_OUTDIR) if ENV_OUTDIR else DEFAULT_OUTDIR
JSON_OUT = OUTDIR / "history.json"
MD_OUT = OUTDIR / "history.md"


def main():
    print("[eval.history] starting")

    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Load eval report to get history
    report_json = OUTDIR / "report.json"
    if not report_json.exists():
        print(f"[eval.history] FAIL no report.json at {report_json}")
        return 1

    try:
        report = json.loads(report_json.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[eval.history] FAIL could not parse report: {e}")
        return 1

    # Generate history data
    tasks = report.get("tasks", [])
    history_data = {
        "generated_at": report.get("timestamp", "unknown"),
        "total_tasks": len(tasks),
        "passed": sum(1 for t in tasks if t.get("status") == "OK"),
        "failed": sum(1 for t in tasks if t.get("status") == "FAIL"),
        "task_history": [
            {
                "key": t.get("key"),
                "status": t.get("status"),
                "duration_ms": t.get("duration_ms", 0),
                "timestamp": t.get("timestamp", "unknown")
            }
            for t in tasks
        ]
    }

    # Write JSON
    JSON_OUT.write_text(json.dumps(history_data, indent=2), encoding="utf-8")
    print(f"[eval.history] wrote {JSON_OUT.relative_to(ROOT)}")

    # Write Markdown
    md_content = f"""# Eval History Report

Generated: {history_data['generated_at']}

## Summary
- **Total Tasks**: {history_data['total_tasks']}
- **Passed**: {history_data['passed']}
- **Failed**: {history_data['failed']}

## Task History

| Task Key | Status | Duration (ms) | Timestamp |
|----------|--------|---------------|-----------|
"""

    for task in history_data['task_history']:
        md_content += f"| {task['key']} | {task['status']} | {task['duration_ms']} | {task['timestamp']} |\n"

    MD_OUT.write_text(md_content, encoding="utf-8")
    print(f"[eval.history] wrote {MD_OUT.relative_to(ROOT)}")
    print("[eval.history] done")


if __name__ == "__main__":
    exit(main() or 0)
