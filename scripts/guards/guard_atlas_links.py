#!/usr/bin/env python3
"""
PLAN-079 E95 — Atlas Links Integrity Sweep

Per MASTER_PLAN E95:

- Scan for broken links across all Atlas pages.
- Verify internal links resolve.
- External links should be "accessible (or marked as external)."

Hermetic interpretation (no network, DB-off tolerant):

- Internal links:
  - hrefs that are relative paths (no scheme, no mailto:, no javascript:, not just '#').
  - We resolve them against the source HTML file and require the target file to exist under docs/atlas/.
- External links:
  - hrefs starting with http:// or https://
  - We cannot hit the network, so we enforce that external links are explicitly marked as external:
    - class contains "external", OR
    - rel contains "external", OR
    - data-external="true"

Output JSON verdict:

{
  "ok": bool,
  "checks": {
    "html_scanned": bool,
    "no_broken_internal_links": bool,
    "external_links_marked": bool,
  },
  "counts": {
    "html_files": int,
    "internal_links": int,
    "broken_internal_links": int,
    "external_links": int,
    "unmarked_external_links": int,
  },
  "details": {
    "broken_internal_links": [
      {"source": str, "href": str, "resolved": str},
      ...
    ],
    "unmarked_external_links": [
      {"source": str, "href": str},
      ...
    ],
  },
}
"""

import html
import json
import pathlib
import re
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS_ROOT = ROOT / "docs" / "atlas"

# Whitelist patterns for allowed out-of-scope links (diagnostic/evidence/share links)
# These are reported in details but don't fail the guard
# Atlas pages legitimately link to JSON exports in share/ and evidence/ directories
EVIDENCE_WHITELIST_PATTERNS = [
    r"\.\./\.\./evidence",
    r"\.\./\.\./\.\./evidence",
    r"\.\./\.\./\.\./share/",
    r"\.\./\.\./share/",
]

# Very simple <a> tag matcher; good enough for guard purposes.
A_TAG_RE = re.compile(
    r"<a\b([^>]*?)>",
    re.IGNORECASE | re.DOTALL,
)

HREF_RE = re.compile(
    r'href\s*=\s*("([^"]*)"|\'([^\']*)\')',
    re.IGNORECASE,
)

CLASS_RE = re.compile(
    r'class\s*=\s*("([^"]*)"|\'([^\']*)\')',
    re.IGNORECASE,
)

REL_RE = re.compile(
    r'rel\s*=\s*("([^"]*)"|\'([^\']*)\')',
    re.IGNORECASE,
)

DATA_EXTERNAL_RE = re.compile(
    r'data-external\s*=\s*("([^"]*)"|\'([^\']*)\')',
    re.IGNORECASE,
)


def _iter_html_files():
    if not ATLAS_ROOT.exists():
        return []
    return sorted(ATLAS_ROOT.rglob("*.html"))


def _extract_attr(pattern: re.Pattern, attrs: str) -> str | None:
    m = pattern.search(attrs)
    if not m:
        return None
    return m.group(2) or m.group(3)


def _parse_links(text: str):
    """Yield (attrs_str, href_value) for each <a> tag with an href."""
    for m in A_TAG_RE.finditer(text):
        attrs = m.group(1) or ""
        href_match = HREF_RE.search(attrs)
        if not href_match:
            continue
        href = href_match.group(2) or href_match.group(3) or ""
        yield attrs, html.unescape(href)


def _is_external(href: str) -> bool:
    lower = href.lower().strip()
    return lower.startswith("http://") or lower.startswith("https://")


def _is_absolute_path(href: str) -> bool:
    """Check if href is an absolute path starting with '/'."""
    return href.strip().startswith("/")


def _is_whitelisted(href: str) -> bool:
    """Check if href matches whitelist patterns for evidence/diagnostic links."""
    import re

    for pattern in EVIDENCE_WHITELIST_PATTERNS:
        if re.search(pattern, href):
            return True
    return False


def _is_internal(href: str) -> bool:
    """Check if href is a relative internal link (not external, not absolute, not special)."""
    lower = href.lower().strip()
    if not lower:
        return False
    if lower.startswith("#"):
        return False
    if lower.startswith("mailto:"):
        return False
    if lower.startswith("javascript:"):
        return False
    if lower.startswith("/"):
        return False  # Absolute paths are handled separately
    if "://" in lower:
        return False
    return True


def _is_marked_external(attrs: str) -> bool:
    cls = _extract_attr(CLASS_RE, attrs) or ""
    rel = _extract_attr(REL_RE, attrs) or ""
    data_ext = _extract_attr(DATA_EXTERNAL_RE, attrs) or ""
    cls_l = cls.lower()
    rel_l = rel.lower()
    data_l = data_ext.lower()
    return "external" in cls_l or "external" in rel_l or data_l in ("true", "1", "yes")


def main() -> int:
    checks: dict[str, bool] = {}
    counts: dict[str, int] = {}
    details: dict[str, Any] = {}

    html_files = list(_iter_html_files())
    counts["html_files"] = len(html_files)
    checks["html_scanned"] = len(html_files) > 0

    internal_links = 0
    broken_internal = []
    external_links = 0
    unmarked_external = []
    absolute_paths = []  # Absolute paths starting with /
    whitelisted_links = []  # Evidence/diagnostic links that are whitelisted

    for html_path in html_files:
        rel_source = html_path.relative_to(ROOT).as_posix()
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        for attrs, href in _parse_links(text):
            if _is_external(href):
                external_links += 1
                if not _is_marked_external(attrs):
                    unmarked_external.append(
                        {
                            "source": rel_source,
                            "href": href,
                        }
                    )
            elif _is_absolute_path(href):
                # Absolute paths are app-level routes, not file paths
                # They should be marked as external or handled specially
                absolute_paths.append(
                    {
                        "source": rel_source,
                        "href": href,
                        "marked_external": _is_marked_external(attrs),
                    }
                )
            elif _is_internal(href):
                # Check if whitelisted (evidence links)
                if _is_whitelisted(href):
                    whitelisted_links.append(
                        {
                            "source": rel_source,
                            "href": href,
                        }
                    )
                    # Whitelisted links don't count as broken, but are tracked
                    continue

                internal_links += 1
                resolved = (html_path.parent / href).resolve()
                try:
                    # Map back to ROOT-relative path if under ROOT
                    resolved_rel = resolved.relative_to(ROOT).as_posix()
                except ValueError:
                    resolved_rel = resolved.as_posix()

                # Only check if file exists and is within docs/atlas/ for true internal links
                if not resolved.exists():
                    broken_internal.append(
                        {
                            "source": rel_source,
                            "href": href,
                            "resolved": resolved_rel,
                        }
                    )
                elif not str(resolved).startswith(str(ATLAS_ROOT)):
                    # Link resolves outside docs/atlas/ - treat as broken internal
                    broken_internal.append(
                        {
                            "source": rel_source,
                            "href": href,
                            "resolved": resolved_rel,
                            "note": "resolves outside docs/atlas/",
                        }
                    )

    counts["internal_links"] = internal_links
    counts["broken_internal_links"] = len(broken_internal)
    counts["external_links"] = external_links
    counts["unmarked_external_links"] = len(unmarked_external)
    counts["absolute_paths"] = len(absolute_paths)
    counts["whitelisted_links"] = len(whitelisted_links)

    checks["no_broken_internal_links"] = len(broken_internal) == 0
    # External links must be explicitly marked as external.
    checks["external_links_marked"] = len(unmarked_external) == 0

    details["broken_internal_links"] = broken_internal[:64]
    details["unmarked_external_links"] = unmarked_external[:64]
    details["absolute_paths"] = absolute_paths[:64]
    details["whitelisted_links"] = whitelisted_links[:64]

    ok = all(checks.values())
    verdict = {
        "ok": ok,
        "checks": checks,
        "counts": counts,
        "details": details,
    }
    print(json.dumps(verdict, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
