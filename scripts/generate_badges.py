#!/usr/bin/env python3

import argparse
from pathlib import Path


def generate_monitoring_badge(output_dir: str) -> None:
    """Generate a simple monitoring badge SVG."""
    badge_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
  <rect width="40" height="20" fill="#555"/>
  <rect x="40" width="80" height="20" fill="#4c1"/>
  <text x="20" y="14" fill="#fff" font-family="Arial,sans-serif" font-size="11" text-anchor="middle">monitoring</text>
  <text x="80" y="14" fill="#fff" font-family="Arial,sans-serif" font-size="11" text-anchor="middle">active</text>
</svg>"""

    output_path = Path(output_dir) / "monitoring.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(badge_svg)

    print(f"Generated monitoring badge at {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate monitoring badges")
    parser.add_argument("--type", required=True, choices=["monitoring"])
    parser.add_argument("--out", required=True, help="Output directory")

    args = parser.parse_args()

    if args.type == "monitoring":
        generate_monitoring_badge(args.out)
    else:
        print(f"Unknown badge type: {args.type}")


if __name__ == "__main__":
    main()
