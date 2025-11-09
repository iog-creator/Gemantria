#!/usr/bin/env python3

"""
Quick preview utility for Atlas files.
Usage: python3 scripts/status/preview_atlas.py [html|txt|mmd]
"""

import sys
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ATLAS_DIR = REPO / "docs" / "atlas"


def preview_html():
    """Open HTML file in browser."""
    html_file = ATLAS_DIR / "status.html"
    if html_file.exists():
        subprocess.run(["xdg-open", str(html_file)])
        print("📺 Opened HTML preview in browser")
    else:
        print("❌ HTML file not found. Run 'make atlas.update' first.")


def preview_txt():
    """Display ASCII diagram in terminal."""
    txt_file = ATLAS_DIR / "status.txt"
    if txt_file.exists():
        print("\n" + "=" * 60)
        print(txt_file.read_text())
        print("=" * 60 + "\n")
    else:
        print("❌ Text file not found. Run 'make atlas.update' first.")


def preview_mmd():
    """Show Mermaid code (for copy-paste to online renderers)."""
    mmd_file = ATLAS_DIR / "status.mmd"
    if mmd_file.exists():
        content = mmd_file.read_text()
        print("📋 Mermaid code (copy to https://mermaid.live/ or similar):")
        print("\n" + content + "\n")
    else:
        print("❌ Mermaid file not found. Run 'make atlas.update' first.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/status/preview_atlas.py [html|txt|mmd]")
        print("  html - Open in browser")
        print("  txt  - Show ASCII diagram")
        print("  mmd  - Show Mermaid code")
        return

    command = sys.argv[1].lower()

    if command == "html":
        preview_html()
    elif command == "txt":
        preview_txt()
    elif command == "mmd":
        preview_mmd()
    else:
        print(f"❌ Unknown command: {command}")
        main()


if __name__ == "__main__":
    main()
