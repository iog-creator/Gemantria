# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

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


def update_next_steps_from_envelope(envelope: dict) -> bool:
    """
    Update NEXT_STEPS.md with completion status and next steps from envelope.

    Args:
        envelope: Completion envelope dict from generate_completion_envelope

    Returns:
        True if successful
    """
    next_steps_path = Path(__file__).resolve().parent.parent / "NEXT_STEPS.md"

    # Read or create NEXT_STEPS.md
    if not next_steps_path.exists():
        content = "# NEXT_STEPS\n\n"
    else:
        content = next_steps_path.read_text()

    # Extract information from envelope
    work_type = envelope.get("work", {}).get("type", "unknown")
    timestamp = envelope.get("timestamp", datetime.datetime.now().isoformat())
    next_steps = envelope.get("next_steps", [])
    handoff_status = envelope.get("handoff", {}).get("status", "unknown")
    handoff_instructions = envelope.get("handoff", {}).get("instructions", "")

    # Add completion section
    completion_section = f"""
## Latest Completion ({timestamp})

**Work Type**: {work_type}
**Status**: {handoff_status}
**Instructions**: {handoff_instructions}

### Next Steps

"""
    for step in next_steps:
        step_id = step.get("id", "NEXT_STEPS:?")
        step_title = step.get("title", "Unknown step")
        step_source = step.get("source", "unknown")
        completion_section += f"- [{step_id}] {step_title} (source: {step_source})\n"

    # Append to content (after timestamp marker if present)
    if "<!-- Handoff updated:" in content:
        # Insert after the marker
        lines = content.split("\n")
        marker_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("<!-- Handoff updated:"):
                marker_idx = i
                break
        if marker_idx >= 0:
            lines.insert(marker_idx + 1, completion_section)
            content = "\n".join(lines)
        else:
            content = content + "\n" + completion_section
    else:
        content = content + "\n" + completion_section

    # Write back
    next_steps_path.write_text(content)
    print("✅ NEXT_STEPS.md updated with completion envelope")
    return True


if __name__ == "__main__":
    update_handoff_status()
