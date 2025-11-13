from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from html.parser import HTMLParser


VERDICT_PATH = Path("evidence/guard_m14_webproof_backlinks.verdict.json")

# Expected backlinks per artifact
EXPECTED_BACKLINKS = {
    "e66_graph_rollup": [
        ("backlink-e66_graph_rollup-json", "share/atlas/graph/rollup.json"),
        (
            "backlink-e66_graph_rollup-guard",
            "evidence/guard_m14_graph_rollup_versioned.verdict.json",
        ),
    ],
    "e67_drilldown": [
        ("backlink-e67_drilldown-json", "share/atlas/nodes/drilldown.sample.json"),
        ("backlink-e67_drilldown-guard", "evidence/guard_m14_node_drilldowns_links.verdict.json"),
    ],
    "e68_screenshots": [
        ("backlink-e68_screenshots-json", "share/atlas/screenshots/manifest.json"),
        (
            "backlink-e68_screenshots-guard",
            "evidence/guard_m14_screenshot_manifest_canonicalized.verdict.json",
        ),
    ],
    "e69_reranker": [
        ("backlink-e69_reranker-json", "share/atlas/badges/reranker.json"),
        ("backlink-e69_reranker-guard", "evidence/guard_m14_reranker_badges.verdict.json"),
    ],
}


class BacklinkParser(HTMLParser):
    """Parse HTML to extract backlinks with data-testid attributes."""

    def __init__(self):
        super().__init__()
        self.backlinks: Dict[str, str] = {}  # testid -> href

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "a":
            testid = None
            href = None
            for attr, value in attrs:
                if attr == "data-testid":
                    testid = value
                elif attr == "href":
                    href = value
            if testid and href:
                self.backlinks[testid] = href


def verdict(ok: bool, **extra: Any) -> int:
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {"ok": ok, **extra}
    VERDICT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


def check_backlinks(html_file: Path, artifact_name: str) -> tuple[bool, List[str]]:
    """Check if HTML file contains expected backlinks."""
    if not html_file.exists():
        return False, [f"HTML file missing: {html_file}"]

    try:
        content = html_file.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"Failed to read HTML: {e}"]

    parser = BacklinkParser()
    parser.feed(content)

    expected = EXPECTED_BACKLINKS.get(artifact_name, [])
    missing = []
    found = []

    for testid, expected_path in expected:
        if testid not in parser.backlinks:
            missing.append(f"Missing backlink: {testid}")
        else:
            href = parser.backlinks[testid]
            # Check if href points to expected path (relative path resolution)
            # href might be like "../../../share/atlas/graph/rollup.json"
            if expected_path in href or href.endswith(expected_path.split("/")[-1]):
                found.append(testid)
            else:
                missing.append(f"Backlink {testid} points to wrong path: {href} (expected: {expected_path})")

    if missing:
        return False, missing
    return True, found


def main() -> int:
    webproof_dir = Path("docs/atlas/webproof")

    if not webproof_dir.exists():
        return verdict(False, error="webproof_dir_missing", path=str(webproof_dir))

    all_ok = True
    all_errors: List[str] = []
    all_found: Dict[str, List[str]] = {}

    for artifact_name in EXPECTED_BACKLINKS.keys():
        html_file = webproof_dir / f"{artifact_name}.html"
        ok, issues = check_backlinks(html_file, artifact_name)
        if not ok:
            all_ok = False
            all_errors.extend([f"{artifact_name}: {issue}" for issue in issues])
        else:
            all_found[artifact_name] = issues

    if not all_ok:
        return verdict(False, error="missing_backlinks", details=all_errors, found=all_found)

    return verdict(True, found=all_found, artifacts=list(EXPECTED_BACKLINKS.keys()))


if __name__ == "__main__":
    raise SystemExit(main())
