#!/usr/bin/env python3
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "eval" / "manifest.yml"
REPORT = ROOT / "scripts" / "eval" / "report.py"
OUTDIR = ROOT / "share" / "eval"


# replace any task args 'file' of exports/graph_latest.json with the provided path (string-substitution)
def _rewrite_manifest_text(txt: str, repl_path: str) -> str:
    # naive but effective: replace the literal path in YAML
    return re.sub(r'file:\s*"exports/graph_latest\.json"', f'file: "{repl_path}"', txt)


def main() -> int:
    if len(sys.argv) != 2:
        print("[eval.report_for] usage: report_for_file.py <path-to-export.json>")
        return 2
    target = pathlib.Path(sys.argv[1]).resolve()
    print(f"[eval.report_for] starting target={target}")
    if not target.exists():
        print("[eval.report_for] FAIL no such file")
        return 2
    OUTDIR.mkdir(parents=True, exist_ok=True)
    txt = MANIFEST.read_text(encoding="utf-8")
    patched = _rewrite_manifest_text(txt, str(target.relative_to(ROOT)))
    tmp_manifest = MANIFEST.parent / "_manifest.tmp.yml"
    tmp_manifest.write_text(patched, encoding="utf-8")

    # run the canonical report.py with the temp manifest by shadowing MANIFEST env var via file swap
    backup = MANIFEST.read_text(encoding="utf-8")
    try:
        MANIFEST.write_text(patched, encoding="utf-8")
        # import and run report.py as a module
        import runpy

        runpy.run_path(str(REPORT))
    finally:
        MANIFEST.write_text(backup, encoding="utf-8")
        if tmp_manifest.exists():
            tmp_manifest.unlink(missing_ok=True)

    # Rename artifacts to include basename
    base = target.stem
    (OUTDIR / "report.json").rename(OUTDIR / f"report_for_{base}.json")
    (OUTDIR / "report.md").rename(OUTDIR / f"report_for_{base}.md")
    print(f"[eval.report_for] wrote share/eval/report_for_{base}.json")
    print(f"[eval.report_for] wrote share/eval/report_for_{base}.md")
    print("[eval.report_for] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
