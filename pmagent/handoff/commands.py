#!/usr/bin/env python3
"""
PM Agent CLI - Handoff Commands

Handoff service for generating DMS-grounded context reports.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Import handoff generation function from existing script
from scripts.prepare_handoff import generate_handoff_content  # noqa: E402

app = typer.Typer(help="Handoff service commands")


@app.command("generate")
def handoff_generate(
    type: str = typer.Option("role", "--type", help="Handoff type (currently only 'role' supported)"),
    role: str = typer.Option(None, "--role", help="Role for handoff (e.g., 'orchestrator')"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (default: share/handoff_latest.md)"),
) -> None:
    """
    Generate a DMS-grounded handoff report.

    This command produces a structured handoff context report that the PM must use
    before planning new work. The report includes git state, PR information (if applicable),
    and baseline evidence per Rule 051.

    Example:
        pmagent handoff generate --type role --role orchestrator
    """
    # Validate type (for now, only 'role' is supported)
    if type != "role":
        print(
            f"Error: Unsupported handoff type '{type}'. Currently only 'role' is supported.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate handoff content using existing function
    try:
        content = generate_handoff_content()

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = Path("share/handoff_latest.md")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        output_path.write_text(content, encoding="utf-8")

        # Print success message
        print(f"✅ Handoff report generated: {output_path}", file=sys.stderr)
        print(f"   Type: {type}", file=sys.stderr)
        if role:
            print(f"   Role: {role}", file=sys.stderr)
        print(f"   Size: {len(content)} bytes", file=sys.stderr)

        # Also print content to stdout for piping/redirection
        print(content)

        sys.exit(0)
    except Exception as e:
        print(f"Error generating handoff report: {e}", file=sys.stderr)
        sys.exit(1)
