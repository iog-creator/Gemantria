#!/usr/bin/env python3
"""
generate_handoff.py — Update project handoff document for continuity.

Updates NEXT_STEPS.md with current timestamp and status indicators
to ensure smooth handoffs between development sessions.
"""

import datetime
from pathlib import Path


def update_handoff_status():
    """Update handoff document with current timestamp."""
    next_steps_path = Path(__file__).resolve().parent.parent / "NEXT_STEPS.md"

    if not next_steps_path.exists():
        print("⚠️  NEXT_STEPS.md not found, creating basic handoff marker")
        next_steps_path.write_text(
            f"# NEXT_STEPS - Auto-generated {datetime.datetime.now().isoformat()}\n\nHandoff completed.\n"
        )
        return True

    # Read current content
    content = next_steps_path.read_text()

    # Add/update timestamp marker
    timestamp = datetime.datetime.now().isoformat()
    marker = f"<!-- Handoff updated: {timestamp} -->"

    if "<!-- Handoff updated:" in content:
        # Replace existing marker
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("<!-- Handoff updated:"):
                lines[i] = marker
                break
        content = "\n".join(lines)
    else:
        # Add marker at top
        content = marker + "\n" + content

    # Write back
    next_steps_path.write_text(content)
    print(f"✅ Handoff document updated at {timestamp}")
    return True


if __name__ == "__main__":
    update_handoff_status()
