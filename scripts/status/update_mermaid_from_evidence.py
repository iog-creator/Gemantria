#!/usr/bin/env python3

"""

Generate docs/atlas/status.mmd from existing evidence files only.

- No DB, no network. Reads JSON/flat-text verdicts already produced by CI/tag.

- Colors: green (pass), red (fail), grey (missing/unknown).

"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


# repo layout: <repo>/scripts/status/update_mermaid_from_evidence.py
REPO = Path(__file__).resolve().parents[2]
ATLAS_DIR = REPO / "docs" / "atlas"
OUT = ATLAS_DIR / "status.mmd"
EVIDENCE = REPO / "evidence"
BADGES = REPO / "share" / "eval" / "badges"
EVIDENCE_DOCS = REPO / "docs" / "evidence"
CHANGELOG = REPO / "CHANGELOG.md"

# Logical items → (path, label)
ITEMS = {
    "exports_json": (EVIDENCE / "exports_guard.verdict.json", "Exports JSON"),
    "rfc3339": (EVIDENCE / "exports_rfc3339.verdict.json", "RFC3339 timestamps"),
    "extraction_acc": (EVIDENCE / "guard_extraction_accuracy.json", "Extraction accuracy"),
    "xrefs_metrics": (EVIDENCE / "xrefs_metrics.json", "Xrefs metrics"),
    "badges_manifest": (EVIDENCE / "badges_manifest.json", "Badges manifest"),
    "badge_exports": (BADGES / "exports_json.svg", "exports_json.svg"),
}


class Status:
    GREEN = "green"
    RED = "red"
    GREY = "grey"


def get_latest_tag() -> str:
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=REPO,
            text=True,
        ).strip()
        return tag
    except Exception:
        return "UN-TAGGED"


def verdict_status(path: Path) -> str:
    """Infer pass/fail/unknown from a verdict file."""
    if not path.exists():
        return Status.GREY

    # Try JSON first
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Common booleans
        for key in ("ok", "pass", "success", "passed"):
            if isinstance(data, dict) and key in data:
                return Status.GREEN if bool(data[key]) else Status.RED

        # Heuristic: cases/correct
        if isinstance(data, dict) and "cases" in data and "correct" in data:
            try:
                cases = int(data["cases"])
                correct = int(data["correct"])
                return Status.GREEN if correct >= cases else Status.RED
            except Exception:
                return Status.GREY

        # Presence often implies success in our bundle
        return Status.GREEN
    except Exception:
        # Non-JSON fallback: look for pass/fail keywords
        txt = path.read_text(encoding="utf-8", errors="ignore").lower()
        if "false" in txt or "fail" in txt or "error" in txt:
            return Status.RED
        if "true" in txt or "pass" in txt or "ok" in txt or "success" in txt:
            return Status.GREEN
        return Status.GREY


def file_presence_status(path: Path) -> str:
    return Status.GREEN if path.exists() else Status.GREY


def cls(status: str) -> str:
    return {
        Status.GREEN: ":::green",
        Status.RED: ":::red",
        Status.GREY: ":::grey",
    }[status]


def node(id_: str, label: str, summary_md: Path, status: str, base_url: str = "") -> str:
    """Node links to human summary (which itself links to raw evidence)."""
    display = f"{label}<br/>({summary_md.relative_to(REPO)})"
    line = f'    {id_}["{display}"]{cls(status)}\n'
    if summary_md.exists():
        rel_path = summary_md.relative_to(REPO).as_posix()
        # Always use relative paths for GitHub/IDE compatibility
        # base_url is only used for HTML preview in browser
        click_url = rel_path
        line += f'    click {id_} "{click_url}" "Open {label} summary"\n'
    return line


def write_human_summary(title: str, verdict_path: Path, out_md: Path) -> None:
    """Render a minimal non-technical summary from an evidence file (JSON or text)."""
    out_md.parent.mkdir(parents=True, exist_ok=True)
    status = verdict_status(verdict_path) if verdict_path.suffix != ".svg" else file_presence_status(verdict_path)
    emoji = {"green": "✅", "red": "❌", "grey": "⚪"}.get(status, "⚪")
    raw_link = verdict_path.relative_to(REPO).as_posix()

    # One-line hints tailored for the orchestrator
    hints = {
        "Exports JSON": "Checks that our exported JSON files are well-formed and complete.",
        "RFC3339 timestamps": "Checks that all timestamps look like 2025-11-09T10:15:00Z (standard format).",
        "Extraction accuracy": "Quick accuracy check on sample cases to ensure extractors still behave.",
        "Xrefs metrics": "Cross-reference summary for links shown in the UI tiles.",
        "Badges manifest": "Index of which status badges are present for this proof snapshot.",
        "exports_json.svg": "Green/red picture used on the dashboard for the exports JSON check.",
    }
    hint = hints.get(title, "")

    try:
        data = {}
        if verdict_path.exists() and verdict_path.suffix == ".json":
            data = json.loads(verdict_path.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    out_md.write_text(
        f"# {title} {emoji}\n\n"
        f"**What this proves (for the orchestrator):** {hint}\n\n"
        f"**Status:** {status.upper()}\n\n"
        f"**Raw evidence:** `{raw_link}`\n\n"
        f"**Excerpt:**\n\n```json\n{json.dumps(data, indent=2) if data else '{}'}\n```\n\n"
        f"_Definitions:_ **Tag** = frozen proof snapshot · **Badge** = visual pass/fail marker · "
        f"**Verdict** = the JSON file that says pass/fail.\n",
        encoding="utf-8",
    )


def build_mermaid(tag: str, statuses: dict[str, str], base_url: str = "") -> str:
    parts: list[str] = []
    parts.append("```mermaid\nflowchart LR\n  %% Evidence-driven status (auto-generated)\n")

    # Color TAG by aggregate guard state
    guard_keys = ["exports_json", "rfc3339", "extraction_acc", "xrefs_metrics"]
    guard_vals = [statuses.get(k, "grey") for k in guard_keys]
    if any(v == Status.RED for v in guard_vals):
        tag_cls = ":::red"
    elif guard_vals and all(v == Status.GREEN for v in guard_vals):
        tag_cls = ":::green"
    else:
        tag_cls = ":::grey"
    parts.append(f'  TAG["{tag}<br/>(STRICT proof)"]{tag_cls}\n')
    if CHANGELOG.exists():
        rel_changelog = CHANGELOG.relative_to(REPO).as_posix()
        # Always use relative paths for GitHub/IDE compatibility
        parts.append(f'  click TAG "{rel_changelog}" "Open CHANGELOG"\n')

    parts.append('  subgraph GUARDS["Guards & Verdicts"]\n')
    parts.append(
        node(
            "EJSON",
            "Exports JSON",
            EVIDENCE_DOCS / "exports_json.md",
            statuses["exports_json"],
            base_url,
        )
    )
    parts.append(
        node(
            "ERFC",
            "RFC3339 timestamps",
            EVIDENCE_DOCS / "exports_rfc3339.md",
            statuses["rfc3339"],
            base_url,
        )
    )
    parts.append(
        node(
            "EACC",
            "Extraction accuracy",
            EVIDENCE_DOCS / "extraction_accuracy.md",
            statuses["extraction_acc"],
            base_url,
        )
    )
    parts.append(
        node(
            "XREF",
            "Xrefs metrics",
            EVIDENCE_DOCS / "xrefs_metrics.md",
            statuses["xrefs_metrics"],
            base_url,
        )
    )
    parts.append("  end\n\n")

    parts.append('  subgraph BADGES["Badges (visual pass/fail)"]\n')
    parts.append(
        node(
            "BMAN",
            "Badges manifest",
            EVIDENCE_DOCS / "badges_manifest.md",
            statuses["badges_manifest"],
            base_url,
        )
    )
    parts.append(
        node(
            "BEXP",
            "exports_json.svg",
            EVIDENCE_DOCS / "exports_json_badge.md",
            statuses["badge_exports"],
            base_url,
        )
    )
    parts.append("  end\n\n")

    parts.append("  TAG --> EJSON\n  TAG --> ERFC\n  TAG --> EACC\n  TAG --> XREF\n  TAG --> BADGES\n\n")

    parts.append(
        "  %% Color classes\n"
        "  classDef green fill:#a7f3d0,stroke:#065f46,color:#083344,stroke-width:1px;\n"
        "  classDef red   fill:#fecaca,stroke:#7f1d1d,color:#111827,stroke-width:1px;\n"
        "  classDef grey  fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-width:1px;\n"
        "```\n"
    )
    return "".join(parts)


def build_html(mermaid_content: str, tag: str, base_url: str = "") -> str:
    """Generate standalone HTML file that renders the diagram."""
    # Extract just the Mermaid code (remove markdown backticks)
    mermaid_code = mermaid_content
    if mermaid_code.startswith("```mermaid"):
        mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
    elif mermaid_code.startswith("```"):
        mermaid_code = mermaid_code.replace("```", "").strip()

    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>Gemantria Atlas - Tag {tag}</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }},
            securityLevel: 'loose'
        }});
        
        // Handle click events on Mermaid nodes using callback
        const callback = function(id) {{
            // Map node IDs to summary URLs (human-readable pages)
            // Use base_url for browser preview, relative paths for GitHub/IDE
            const base = '{base_url}' || '';
            const urlMap = {{
                'TAG': base ? base + '/CHANGELOG.md' : 'CHANGELOG.md',
                'EJSON': base ? base + '/docs/evidence/exports_json.md' : 'docs/evidence/exports_json.md',
                'ERFC': base ? base + '/docs/evidence/exports_rfc3339.md' : 'docs/evidence/exports_rfc3339.md',
                'EACC': base ? base + '/docs/evidence/extraction_accuracy.md' : 'docs/evidence/extraction_accuracy.md',
                'XREF': base ? base + '/docs/evidence/xrefs_metrics.md' : 'docs/evidence/xrefs_metrics.md',
                'BMAN': base ? base + '/docs/evidence/badges_manifest.md' : 'docs/evidence/badges_manifest.md',
                'BEXP': base ? base + '/docs/evidence/exports_json_badge.md' : 'docs/evidence/exports_json_badge.md'
            }};
            
            const url = urlMap[id];
            if (url) {{
                window.open(url, '_blank');
            }}
        }};
        
        // Set up click handler after Mermaid renders
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(function() {{
                const svg = document.querySelector('.mermaid svg');
                if (svg) {{
                    // Add click handlers to all node groups
                    const nodeGroups = svg.querySelectorAll('g.node');
                    nodeGroups.forEach(function(group) {{
                        const nodeId = group.id;
                        if (nodeId && ['TAG', 'EJSON', 'ERFC', 'EACC', 'XREF', 'BMAN', 'BEXP'].includes(nodeId)) {{
                            group.style.cursor = 'pointer';
                            group.addEventListener('click', function() {{
                                callback(nodeId);
                            }});
                        }}
                    }});
                }}
            }}, 1500);
        }});
    </script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #6c757d;
            margin-bottom: 30px;
        }}
        .diagram {{
            text-align: center;
        }}
        .mermaid {{
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ Gemantria Atlas</h1>
        <div class="subtitle">Evidence-driven status for tag {tag}</div>
        <div class="diagram">
            <pre class="mermaid">{mermaid_code}</pre>
        </div>
    </div>
</body>
</html>"""
    return html_template


def build_ascii_diagram(tag: str, statuses: dict[str, str]) -> str:
    """Generate simple ASCII diagram for Cursor IDE."""
    status_symbols = {Status.GREEN: "✅", Status.RED: "❌", Status.GREY: "⚪"}

    lines = []
    lines.append(f"🗺️  GEMATRIA ATLAS - Tag {tag}")
    lines.append("=" * 50)
    lines.append("")

    lines.append("GUARDS & VERDICTS:")
    lines.append(
        f"  {status_symbols[statuses['exports_json']]} Exports JSON        → evidence/exports_guard.verdict.json"
    )
    lines.append(
        f"  {status_symbols[statuses['rfc3339']]} RFC3339 timestamps   → evidence/exports_rfc3339.verdict.json"
    )
    lines.append(
        f"  {status_symbols[statuses['extraction_acc']]} Extraction accuracy → evidence/guard_extraction_accuracy.json"
    )
    lines.append(f"  {status_symbols[statuses['xrefs_metrics']]} Xrefs metrics        → evidence/xrefs_metrics.json")
    lines.append("")

    lines.append("BADGES:")
    lines.append(f"  {status_symbols[statuses['badges_manifest']]} Badges manifest     → evidence/badges_manifest.json")
    lines.append(
        f"  {status_symbols[statuses['badge_exports']]} exports_json.svg    → share/eval/badges/exports_json.svg"
    )
    lines.append("")

    lines.append("LEGEND:")
    lines.append("  ✅ PASS  ❌ FAIL  ⚪ MISSING")
    lines.append("")
    lines.append("Click file paths above or use 'make atlas.update' to refresh.")

    return "\n".join(lines)


def main() -> None:
    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DOCS.mkdir(parents=True, exist_ok=True)
    tag = get_latest_tag()

    # Get base URL from environment or default to localhost:8888
    base_url = os.environ.get("ATLAS_BASE_URL", "http://localhost:8888")

    statuses: dict[str, str] = {
        "exports_json": verdict_status(ITEMS["exports_json"][0]),
        "rfc3339": verdict_status(ITEMS["rfc3339"][0]),
        "extraction_acc": verdict_status(ITEMS["extraction_acc"][0]),
        "xrefs_metrics": verdict_status(ITEMS["xrefs_metrics"][0]),
        "badges_manifest": file_presence_status(ITEMS["badges_manifest"][0]),
        "badge_exports": file_presence_status(ITEMS["badge_exports"][0]),
    }

    # Write human summaries (orchestrator-friendly)
    write_human_summary("Exports JSON", ITEMS["exports_json"][0], EVIDENCE_DOCS / "exports_json.md")
    write_human_summary("RFC3339 timestamps", ITEMS["rfc3339"][0], EVIDENCE_DOCS / "exports_rfc3339.md")
    write_human_summary("Extraction accuracy", ITEMS["extraction_acc"][0], EVIDENCE_DOCS / "extraction_accuracy.md")
    write_human_summary("Xrefs metrics", ITEMS["xrefs_metrics"][0], EVIDENCE_DOCS / "xrefs_metrics.md")
    write_human_summary("Badges manifest", ITEMS["badges_manifest"][0], EVIDENCE_DOCS / "badges_manifest.md")
    write_human_summary("exports_json.svg", ITEMS["badge_exports"][0], EVIDENCE_DOCS / "exports_json_badge.md")

    # Generate Mermaid diagram (with base_url for clickable links)
    mermaid = build_mermaid(tag, statuses, base_url)
    OUT.write_text(mermaid, encoding="utf-8")

    # Generate HTML version (with base_url for clickable links)
    html_out = ATLAS_DIR / "status.html"
    html_content = build_html(mermaid, tag, base_url)
    html_out.write_text(html_content, encoding="utf-8")

    # Generate ASCII version for Cursor
    ascii_out = ATLAS_DIR / "status.txt"
    ascii_content = build_ascii_diagram(tag, statuses)
    ascii_out.write_text(ascii_content, encoding="utf-8")

    print(f"Wrote {OUT.relative_to(REPO)} with tag={tag} and statuses={statuses}")
    print(f"Wrote {html_out.relative_to(REPO)} - open in browser for rendered diagram (base_url={base_url})")
    print(f"Wrote {ascii_out.relative_to(REPO)} - simple text view for Cursor")


if __name__ == "__main__":
    main()
