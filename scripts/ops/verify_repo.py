# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"
MANIFEST = ROOT / "eval" / "manifest.yml"
DOC_EVAL = ROOT / "docs" / "PHASE8_EVAL.md"
SHARE_EVAL_DIR = ROOT / "share" / "eval"


def _print(msg: str) -> None:  # deterministic prefix
    print(f"[ops.verify] {msg}")


def check_make_targets() -> tuple[bool, str]:
    if not MAKEFILE.exists():
        return False, "Makefile missing"
    text = MAKEFILE.read_text(encoding="utf-8", errors="ignore")
    # required local-only eval targets
    need = [
        r"(^|\n)\.PHONY:\s+eval\.report",
        r"(^|\n)eval\.report:\n",
        r"(^|\n)ci\.eval\.report:\n",
    ]
    missing = [pat for pat in need if not re.search(pat, text)]
    if missing:
        return False, f"Makefile targets missing: {missing}"
    return True, "Makefile targets present: eval.report, ci.eval.report"


def read_manifest_version() -> tuple[str | None, str]:
    if not MANIFEST.exists():
        return None, "eval/manifest.yml not found"
    # minimal 'version:' line parser (no pyYAML dependency)
    for line in MANIFEST.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"\s*version:\s*(.+)\s*$", line)
        if m:
            return m.group(1).strip(), "manifest version parsed"
    return "(unknown)", "manifest version not found (line 'version: ...' missing)"


def check_eval_doc() -> tuple[bool, str]:
    if not DOC_EVAL.exists():
        return False, "docs/PHASE8_EVAL.md missing"
    head = DOC_EVAL.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
    ok = bool(head and head[0].strip().startswith("# Phase-8 Eval"))
    return ok, f"PHASE8_EVAL header={'OK' if ok else 'MISSING'}"


def check_share_dir() -> tuple[bool, str]:
    exists = SHARE_EVAL_DIR.exists()
    return exists, f"share/eval/ {'exists' if exists else 'missing'}"


def main() -> int:
    _print("starting")
    results = []

    ok_mk, msg_mk = check_make_targets()
    _print(msg_mk)
    results.append(("make_targets", ok_mk))

    ver, msg_ver = read_manifest_version()
    if ver is None:
        _print(msg_ver)
        results.append(("manifest_present", False))
    else:
        _print(f"manifest.version={ver}")
        results.append(("manifest_present", True))

    ok_doc, msg_doc = check_eval_doc()
    _print(msg_doc)
    results.append(("eval_doc", ok_doc))

    ok_share, msg_share = check_share_dir()
    _print(msg_share)
    results.append(("share_eval_dir", ok_share))

    all_ok = all(ok for _, ok in results)
    _print("OK" if all_ok else "DONE_WITH_FAILS")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
