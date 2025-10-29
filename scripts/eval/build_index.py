#!/usr/bin/env python3
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
import os
DEFAULT_EVAL = ROOT / "share" / "eval"
ENV_EVAL = os.environ.get("EVAL_DIR")
EVAL = (ROOT / ENV_EVAL) if ENV_EVAL else DEFAULT_EVAL
OUT = EVAL / "index.md"


def main():
    print("[eval.index] starting")

    # Ensure output directory exists
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # Gather eval artifacts
    eval_files = []
    if EVAL.exists():
        for pattern in ["*.json", "*.md", "*.html"]:
            eval_files.extend(EVAL.glob(pattern))

    # Create index content
    lines = ["# Eval Index", "", f"Generated from {len(eval_files)} eval artifacts:", ""]

    for file_path in sorted(eval_files):
        rel_path = file_path.relative_to(ROOT)
        size = file_path.stat().st_size
        lines.append(f"* `{rel_path}` ({size} bytes)")

    # Add summary
    lines.extend(["", "## Summary", "", f"Total artifacts: {len(eval_files)}"])

    # Write index
    content = "\n".join(lines)
    OUT.write_text(content, encoding="utf-8")
    print(f"[eval.index] wrote {OUT}")
    print("[eval.index] OK")


if __name__ == "__main__":
    main()
