#!/usr/bin/env python3
import glob
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "share" / "eval" / "exports_catalog.md"
ENV_OUT = os.environ.get("EXPORTS_CATALOG_OUT")
OUT = (ROOT / ENV_OUT) if ENV_OUT else DEFAULT_OUT


def main() -> int:
    print("[eval.catalog] starting")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    exports_dir = ROOT / "exports"
    if not exports_dir.exists():
        print(f"[eval.catalog] FAIL no exports dir at {exports_dir}")
        return 1

    # Find all JSON files in exports/
    pattern = str(exports_dir / "*.json")
    json_files = sorted(glob.glob(pattern))

    if not json_files:
        print("[eval.catalog] WARN no JSON files found in exports/")
        catalog = "# Exports Catalog\n\nNo exports found.\n"
    else:
        catalog_lines = [
            "# Exports Catalog",
            "",
            f"Found {len(json_files)} export files:",
            "",
        ]

        for json_file in json_files:
            path = pathlib.Path(json_file)
            rel_path = path.relative_to(ROOT)

            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Extract basic stats
                if "nodes" in data and "edges" in data:
                    try:
                        nodes = (
                            len(data["nodes"])
                            if hasattr(data["nodes"], "__len__")
                            else data["nodes"]
                        )
                        edges = (
                            len(data["edges"])
                            if hasattr(data["edges"], "__len__")
                            else data["edges"]
                        )
                        stats = f" ({nodes} nodes, {edges} edges)"
                    except (TypeError, AttributeError):
                        stats = f" (stats: nodes={data.get('nodes', '?')}, edges={data.get('edges', '?')})"
                elif isinstance(data, list):
                    stats = f" ({len(data)} items)"
                elif isinstance(data, dict):
                    stats = f" ({len(data)} keys)"
                else:
                    stats = ""

                catalog_lines.append(f"* `{rel_path}`{stats}")

            except Exception as e:
                catalog_lines.append(f"* `{rel_path}` (ERROR: {e})")

        catalog = "\n".join(catalog_lines)

    OUT.write_text(catalog, encoding="utf-8")
    print(f"[eval.catalog] wrote {OUT.relative_to(ROOT)}")
    print("[eval.catalog] OK")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
