#!/usr/bin/env python3
import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "share" / "eval"
HTML_OUT = OUTDIR / "index.html"
REPORT_JSON = OUTDIR / "report.json"


def _status_badge(status: str) -> str:
    if status == "OK":
        return '<span style="background-color: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">PASS</span>'  # noqa: E501
    elif status == "FAIL":
        return '<span style="background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">FAIL</span>'  # noqa: E501
    else:
        return '<span style="background-color: #ffc107; color: black; padding: 2px 8px; border-radius: 4px; font-size: 12px;">WARN</span>'  # noqa: E501


def _load_report() -> dict[str, Any] | dict[str, dict[str, int] | list]:
    if REPORT_JSON.exists():
        return json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    return {"summary": {"ok_count": 0, "fail_count": 0}, "results": []}


def main() -> int:
    print("[eval.html] starting")

    report = _load_report()
    summary = report.get("summary", {})

    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("    <meta charset='UTF-8'>")
    html.append(
        "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    )
    html.append("    <title>Gemantria Phase-8 Eval Dashboard</title>")
    html.append("    <style>")
    html.append(
        "        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }"  # noqa: E501
    )
    html.append(
        "        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }"  # noqa: E501
    )
    html.append(
        "        h1 { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }"
    )
    html.append(
        "        .summary { background: #f1f8ff; padding: 15px; border-radius: 6px; margin: 20px 0; }"  # noqa: E501
    )
    html.append("        .summary strong { color: #007acc; }")
    html.append(
        "        .artifacts { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin: 20px 0; }"  # noqa: E501
    )
    html.append(
        "        .artifact { border: 1px solid #e1e4e8; border-radius: 6px; padding: 15px; background: #fafbfc; }"  # noqa: E501
    )
    html.append("        .artifact h3 { margin: 0 0 10px 0; color: #333; }")
    html.append("        .artifact a { color: #0366d6; text-decoration: none; }")
    html.append("        .artifact a:hover { text-decoration: underline; }")
    html.append("        .badge { margin-left: 10px; }")
    html.append(
        "        .manifest-section { margin: 20px 0; border: 1px solid #e1e4e8; border-radius: 6px; padding: 15px; background: #fafbfc; }"  # noqa: E501
    )
    html.append("        .manifest-section summary { cursor: pointer; font-weight: bold; }")
    html.append("        #manifest-table { width: 100%; border-collapse: collapse; margin-top: 10px; }")
    html.append("        #manifest-table th, #manifest-table td { border: 1px solid #e1e4e8; padding: 8px; text-align: left; }")
    html.append("        #manifest-table th { background: #f1f8ff; font-weight: bold; }")
    html.append("        #manifest-summary { margin-bottom: 10px; font-weight: bold; }")
    html.append(
        "        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e4e8; color: #586069; font-size: 14px; }"  # noqa: E501
    )
    html.append("    </style>")
    html.append("</head>")
    html.append("<body>")
    html.append("    <div class='container'>")
    html.append("        <h1>🔍 Gemantria Phase-8 Evaluation Dashboard</h1>")
    # badges (optional)
    badges_dir = OUTDIR / "badges"
    report_badge = badges_dir / "report_status.svg"
    strict_badge = badges_dir / "strict_gate.svg"
    badges_html = ""
    if report_badge.exists():
        badges_html += '<img alt="report" src="badges/report_status.svg" style="vertical-align:middle;margin-right:8px;">'  # noqa: E501
    if strict_badge.exists():
        badges_html += '<img alt="strict" src="badges/strict_gate.svg" style="vertical-align:middle;">'  # noqa: E501
    if badges_html:
        html.append(f"<div>{badges_html}</div>")
    html.append("")
    html.append("        <div class='summary'>")
    html.append(
        f"            <strong>Overall Status:</strong> {summary.get('ok_count', 0)} PASS, {summary.get('fail_count', 0)} FAIL"  # noqa: E501
    )
    html.append("        </div>")
    html.append("")
    html.append("        <details class='manifest-section'>")
    html.append("            <summary>📦 Release Manifest</summary>")
    html.append("            <div id='manifest-summary'></div>")
    html.append("            <table id='manifest-table'>")
    html.append("                <thead>")
    html.append("                    <tr>")
    html.append("                        <th>Path</th>")
    html.append("                        <th>Size</th>")
    html.append("                        <th>SHA256</th>")
    html.append("                    </tr>")
    html.append("                </thead>")
    html.append("                <tbody id='manifest-tbody'>")
    html.append("                </tbody>")
    html.append("            </table>")
    html.append("        </details>")
    html.append("")
    html.append("        <div class='artifacts'>")

    # Core reports
    artifacts = [
        (
            "report.md",
            "Core Evaluation Report",
            "Primary evaluation results with pass/fail status for all tasks",
        ),
        ("report.json", "Report JSON", "Machine-readable evaluation results"),
        ("history.md", "Temporal History", "Historical trends across export versions"),
        ("history.json", "History JSON", "Machine-readable historical data"),
        ("delta.md", "Per-Run Delta", "Changes between consecutive evaluations"),
        ("delta.json", "Delta JSON", "Machine-readable delta analysis"),
        ("anomalies.md", "Anomalies Summary", "Consolidated red flags and issues"),
        (
            "policy_diff.md",
            "Policy Delta",
            "Comparison of strict vs dev profile outcomes",
        ),
        ("provenance.md", "Provenance", "Git SHA, versions, and metadata"),
        ("provenance.json", "Provenance JSON", "Machine-readable provenance data"),
        ("checksums.csv", "File Checksums", "SHA256 hashes for all artifacts"),
        ("run_log.jsonl", "Run Log", "Append-only execution history"),
    ]

    # Add artifacts with status badges where available
    for filename, title, description in artifacts:
        status = ""
        if filename == "report.md":
            status = "OK" if summary.get("fail_count", 0) == 0 else "FAIL"

        badge = _status_badge(status) if status else ""
        html.append("            <div class='artifact'>")
        html.append(f"                <h3><a href='{filename}'>{title}</a>{badge}</h3>")
        html.append(f"                <p>{description}</p>")
        html.append("            </div>")

    html.append("        </div>")
    html.append("")
    html.append("        <div class='footer'>")
    html.append(
        "            <p>Generated by Phase-8 evaluation system. Use <code>make eval.html</code> to regenerate.</p>"  # noqa: E501
    )
    html.append("        </div>")
    html.append("    </div>")
    html.append("    <script>")
    html.append("        async function loadManifest() {")
    html.append("            try {")
    html.append("                const response = await fetch('release_manifest.json');")
    html.append("                if (!response.ok) throw new Error('Not found');")
    html.append("                const data = await response.json();")
    html.append("                const summary = document.getElementById('manifest-summary');")
    html.append("                const tbody = document.getElementById('manifest-tbody');")
    html.append("                summary.textContent = `Artifacts: ${data.artifact_count} | Generated: ${new Date(data.generated_at * 1000).toISOString()}`;")
    html.append("                const artifacts = data.artifacts.slice(0, 200);")
    html.append("                tbody.innerHTML = '';")
    html.append("                artifacts.forEach(a => {")
    html.append("                    const tr = document.createElement('tr');")
    html.append("                    tr.innerHTML = `<td>${a.path || ''}</td><td>${a.size !== null ? a.size : ''}</td><td>${a.sha256 || ''}</td>`;")
    html.append("                    tbody.appendChild(tr);")
    html.append("                });")
    html.append("            } catch (e) {")
    html.append("                document.getElementById('manifest-summary').textContent = 'Manifest not found';")
    html.append("            }")
    html.append("        }")
    html.append("        if (document.readyState === 'loading') {")
    html.append("            document.addEventListener('DOMContentLoaded', loadManifest);")
    html.append("        } else {")
    html.append("            loadManifest();")
    html.append("        }")
    html.append("    </script>")
    html.append("</body>")
    html.append("</html>")

    HTML_OUT.write_text("\n".join(html), encoding="utf-8")

    print(f"[eval.html] wrote {HTML_OUT.relative_to(ROOT)}")
    print("[eval.html] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
