# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

"""
Minimal a11y smoke without Node: validates presence of basic landmarks/attrs.
Checks (best-effort):
 - page <title> present and non-empty
 - images have alt (if any <img> exist)
 - basic HTML structure
NOTE: For React SPAs, semantic landmarks (<main>, <nav>, headings) are injected at runtime
and cannot be detected in static HTML analysis. This is expected behavior.
Target defaults to webui/public/index.html (static).
"""

import argparse, json, pathlib, time

from html.parser import HTMLParser


class _DOM(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.images = []
        self.has_main = False
        self.has_nav = False
        self.title = ""
        self._in_title = False
        self.headings = set()

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        a = dict(attrs)
        if tag == "img":
            self.images.append(a)
        if tag == "main" or a.get("role") == "main":
            self.has_main = True
        if tag == "nav" or a.get("role") == "navigation":
            self.has_nav = True
        if tag in ("h1", "h2", "h3"):
            self.headings.add(tag)
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def audit(html: str):
    dom = _DOM()
    dom.feed(html)
    issues = []
    if not dom.title.strip():
        issues.append("Missing or empty <title>")

    # Detect React SPA (has root div and script tags)
    is_react_spa = '<div id="root"></div>' in html and '<script type="module"' in html

    if is_react_spa:
        # For React SPAs, semantic landmarks are injected at runtime - this is expected
        pass  # No issues for React SPAs regarding landmarks
    else:
        # For static sites, check for landmarks
        if not (dom.has_main and dom.has_nav):
            if not dom.has_main:
                issues.append("Missing main landmark (<main> or role=main)")
            if not dom.has_nav:
                issues.append("Missing navigation landmark (<nav> or role=navigation)")
        if not dom.headings:
            issues.append("No top-level headings (h1..h3) found")

    imgs = dom.images
    if imgs:
        missing_alt = [i for i in imgs if not i.get("alt")]
        if missing_alt:
            issues.append(f"{len(missing_alt)} image(s) missing alt text")
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="webui/public/index.html")
    ap.add_argument("--out", default="var/ui/a11y.json")
    a = ap.parse_args()
    p = pathlib.Path(a.path)
    res = {"ts": time.time(), "target": str(p), "exists": p.exists(), "issues": []}
    if p.exists():
        issues = audit(p.read_text(errors="ignore"))
        res["issues"] = issues
        res["ok"] = len(issues) == 0
    else:
        res["ok"] = False
        res["issues"] = ["index.html not found (build or export UI first)"]
    pathlib.Path("var/ui").mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(res, indent=2))
    print(json.dumps(res))


if __name__ == "__main__":
    main()
