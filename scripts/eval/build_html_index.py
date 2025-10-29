#!/usr/bin/env python3
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
import os
DEFAULT_OUTDIR = ROOT / "share" / "eval"
ENV_OUTDIR = os.environ.get("EVAL_HTML_OUTDIR")
OUTDIR = (ROOT / ENV_OUTDIR) if ENV_OUTDIR else DEFAULT_OUTDIR
HTML_OUT = OUTDIR / "index.html"
REPORT_JSON = OUTDIR / "report.json"


def main():
    print("[eval.html] starting")

    # Create output directory
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Try to read the eval report
    report_data = {}
    if REPORT_JSON.exists():
        try:
            report_data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[eval.html] WARN could not read report: {e}")

    # Generate basic HTML index
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Gemantria Eval Results</title>
    <style>
        body {{ font-family: monospace; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .task {{ margin: 10px 0; padding: 5px; border-left: 3px solid #ccc; }}
        .ok {{ border-left-color: #4CAF50; }}
        .fail {{ border-left-color: #f44336; }}
    </style>
</head>
<body>
    <h1>Gemantria Eval Results</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p>Timestamp: {report_data.get('ts_unix', 'N/A')}</p>
        <p>Tasks: {report_data.get('summary', {}).get('task_count', 0)}</p>
        <p>OK: {report_data.get('summary', {}).get('ok_count', 0)}</p>
        <p>Fail: {report_data.get('summary', {}).get('fail_count', 0)}</p>
    </div>

    <h2>Task Results</h2>
"""

    for result in report_data.get('results', []):
        status_class = "ok" if result.get('status') == 'OK' else "fail"
        html_content += f"""
    <div class="task {status_class}">
        <strong>{result.get('key', 'unknown')} ({result.get('kind', 'unknown')})</strong>
        <br>Status: {result.get('status', 'unknown')}
    </div>
"""

    html_content += """
</body>
</html>
"""

    # Write HTML file
    HTML_OUT.write_text(html_content, encoding="utf-8")
    print(f"[eval.html] wrote {HTML_OUT}")
    print("[eval.html] OK")


if __name__ == "__main__":
    main()
