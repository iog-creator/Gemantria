#!/usr/bin/env python3
"""
PLAN-079 E94 — Screenshot ↔ Tagproof Integration Guard

Per MASTER_PLAN E94:

- Ensure tagproof bundle references all screenshots.
- Ensure screenshots are included in tagproof artifacts.
- Validate screenshot manifest consistency within tagproof.

This guard is hermetic and DB-off tolerant:
- Reads only local tagproof artifacts and screenshot manifests.
- Does NOT run tar, network calls, or DB queries.

Heuristic inputs (kept flexible for evolving tagproof layout):

1. Tagproof directories:
   - ./tagproof/
   - ./share/releases/*/tagproof/

2. Screenshot files (PNG) within tagproof dirs.

3. Screenshot manifest JSON candidates within tagproof dirs:
   - *screenshot*manifest*.json
   - *screenshots*.json

Core checks:

- tagproof_dir_exists: at least one tagproof directory found.
- has_tagproof_screenshots: at least one *.png in tagproof dirs.
- has_tagproof_manifest: at least one manifest JSON found and parsed.
- manifest_nonempty: manifest has >=1 entries.
- all_screenshots_listed: every discovered screenshot filename is referenced in manifest.
- no_manifest_orphans: every manifest entry references an existing screenshot path.

Emits JSON verdict:

{
  "ok": bool,
  "checks": {...},
  "counts": {...},
  "details": {
    "tagproof_dirs": [...],
    "manifest_paths": [...],
    "unlisted_screenshots": [...],
    "orphan_manifest_entries": [...]
  }
}
"""

import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
TAGPROOF_ROOT = ROOT / "tagproof"
RELEASES_ROOT = ROOT / "share" / "releases"


def _discover_tagproof_dirs() -> list[pathlib.Path]:
    dirs: list[pathlib.Path] = []
    if TAGPROOF_ROOT.exists():
        dirs.append(TAGPROOF_ROOT)

    if RELEASES_ROOT.exists():
        for rel in RELEASES_ROOT.iterdir():
            if not rel.is_dir():
                continue
            tp = rel / "tagproof"
            if tp.exists():
                dirs.append(tp)

    # Deduplicate
    seen = set()
    uniq: list[pathlib.Path] = []
    for d in dirs:
        p = d.resolve()
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _discover_screenshots(tag_dirs: list[pathlib.Path]) -> list[pathlib.Path]:
    shots: list[pathlib.Path] = []
    for d in tag_dirs:
        for p in d.rglob("*.png"):
            shots.append(p)
    return shots


def _discover_manifests(tag_dirs: list[pathlib.Path]) -> list[pathlib.Path]:
    manifests: list[pathlib.Path] = []
    for d in tag_dirs:
        for p in d.rglob("*.json"):
            name = p.name.lower()
            if "screenshot" in name or "screenshots" in name:
                manifests.append(p)
    return manifests


def _load_manifest_entries(path: pathlib.Path) -> list[dict]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(doc, list):
        return [x for x in doc if isinstance(x, dict)]
    if isinstance(doc, dict):
        for key in ("items", "screenshots", "pages"):
            v = doc.get(key)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    return []


def _extract_paths_from_entry(entry: dict) -> list[str]:
    paths: list[str] = []
    for key in ("path", "screenshot", "screenshot_path"):
        val = entry.get(key)
        if isinstance(val, str):
            paths.append(val)
    return paths


def main() -> int:
    checks: dict[str, bool] = {}
    counts: dict[str, int] = {}
    details: dict[str, Any] = {}

    tag_dirs = _discover_tagproof_dirs()
    checks["tagproof_dir_exists"] = len(tag_dirs) > 0
    counts["tagproof_dirs"] = len(tag_dirs)
    details["tagproof_dirs"] = [str(d) for d in tag_dirs]

    screenshots = _discover_screenshots(tag_dirs) if tag_dirs else []
    counts["tagproof_screenshots"] = len(screenshots)
    checks["has_tagproof_screenshots"] = len(screenshots) > 0

    manifests = _discover_manifests(tag_dirs) if tag_dirs else []
    counts["tagproof_manifests"] = len(manifests)
    details["manifest_paths"] = [str(p) for p in manifests]

    all_entries: list[dict] = []
    for mp in manifests:
        all_entries.extend(_load_manifest_entries(mp))
    counts["manifest_entries"] = len(all_entries)
    checks["manifest_nonempty"] = len(all_entries) > 0 if manifests else False

    # Build maps for matching
    screenshot_names = {p.name for p in screenshots}
    manifest_paths: list[str] = []
    for e in all_entries:
        manifest_paths.extend(_extract_paths_from_entry(e))
    manifest_paths_set = set(manifest_paths)

    # Unlisted screenshots = in tagproof PNGs but not mentioned in manifest
    unlisted_screenshots = sorted([s for s in screenshot_names if not any(s in m for m in manifest_paths_set)])
    counts["unlisted_screenshots"] = len(unlisted_screenshots)
    checks["all_screenshots_listed"] = counts["unlisted_screenshots"] == 0 if screenshots else False

    # Orphan manifest entries = manifest paths that don't correspond to existing PNGs
    orphan_manifest_entries = sorted(
        [m for m in manifest_paths_set if not any(m.endswith("/" + s) or s in m for s in screenshot_names)]
    )
    counts["orphan_manifest_entries"] = len(orphan_manifest_entries)
    checks["no_manifest_orphans"] = counts["orphan_manifest_entries"] == 0 if manifest_paths else False

    details["unlisted_screenshots"] = unlisted_screenshots[:64]
    details["orphan_manifest_entries"] = orphan_manifest_entries[:64]

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
