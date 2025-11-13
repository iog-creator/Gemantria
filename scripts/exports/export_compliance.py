# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""CLI wrapper for compliance exporter."""

import argparse
import pathlib
import sys

from agentpm.control_plane.exports import write_compliance_exports


def main() -> int:
    parser = argparse.ArgumentParser(description="Export compliance data to Atlas")
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=pathlib.Path("share/atlas/control_plane"),
        help="Output directory for compliance JSONs",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="STRICT mode (fail on errors)",
    )

    args = parser.parse_args()

    strict_mode = "STRICT" if args.strict else "HINT"

    try:
        results = write_compliance_exports(args.output_dir, strict_mode=strict_mode)

        # Print results
        for filename, status in results.items():
            if status == "ok":
                print(f"✓ {filename}")
            else:
                print(f"✗ {filename}: {status}", file=sys.stderr)
                if strict_mode == "STRICT":
                    return 1

        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
