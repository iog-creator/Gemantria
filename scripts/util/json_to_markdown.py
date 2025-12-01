#!/usr/bin/env python3
"""
JSON to Markdown Converter

Converts JSON files to human-readable markdown format for PM consumption.
Preserves JSON structure while making it more readable.

Usage:
    python scripts/util/json_to_markdown.py <input.json> [--output <output.md>]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, UTC


def json_to_markdown(data: dict | list, indent: int = 0, max_depth: int = 10) -> str:
    """Convert JSON data to markdown format.

    Args:
        data: JSON data (dict or list)
        indent: Current indentation level
        max_depth: Maximum nesting depth

    Returns:
        Markdown-formatted string
    """
    if indent > max_depth:
        return "  " * indent + "... (max depth reached)\n"

    lines = []
    indent_str = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{indent_str}- **{key}**:\n")
                lines.append(json_to_markdown(value, indent + 1, max_depth))
            elif value is None:
                lines.append(f"{indent_str}- **{key}**: `null`\n")
            elif isinstance(value, bool):
                lines.append(f"{indent_str}- **{key}**: `{str(value).lower()}`\n")
            elif isinstance(value, (int, float)):
                lines.append(f"{indent_str}- **{key}**: `{value}`\n")
            else:
                # String value - escape markdown special chars
                value_str = str(value).replace("|", "\\|").replace("*", "\\*")
                if "\n" in value_str:
                    # Multi-line string - use code block
                    lines.append(f"{indent_str}- **{key}**:\n\n```\n{value_str}\n```\n\n")
                elif len(value_str) > 100:
                    # Long string - use code block
                    lines.append(f"{indent_str}- **{key}**:\n\n```\n{value_str}\n```\n\n")
                else:
                    lines.append(f"{indent_str}- **{key}**: `{value_str}`\n")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                lines.append(f"{indent_str}{i + 1}. Item:\n")
                lines.append(json_to_markdown(item, indent + 1, max_depth))
            else:
                item_str = str(item).replace("|", "\\|").replace("*", "\\*")
                if len(item_str) > 100:
                    lines.append(f"{indent_str}{i + 1}. ```\n{item_str}\n```\n\n")
                else:
                    lines.append(f"{indent_str}{i + 1}. `{item_str}`\n")

    return "".join(lines)


def convert_file(input_path: Path, output_path: Path | None = None) -> int:
    """Convert a JSON file to markdown.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output markdown file (default: input_path with .md extension)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    if not input_path.exists():
        print(f"ERROR: Input file does not exist: {input_path}", file=sys.stderr)
        return 1

    # Skip embedding files (too large, not useful as markdown)
    filename_lower = input_path.name.lower()
    if "embedding" in filename_lower or "embedded" in filename_lower:
        print(f"⏭️  Skipping embedding file: {input_path.name} (too large for markdown conversion)")
        return 0

    # Skip files larger than 1MB (likely binary or too large for markdown)
    file_size = input_path.stat().st_size
    if file_size > 1024 * 1024:  # 1MB
        print(f"⏭️  Skipping large file: {input_path.name} ({file_size / 1024 / 1024:.1f}MB, too large for markdown conversion)")
        return 0

    try:
        # Read JSON
        json_data = json.loads(input_path.read_text(encoding="utf-8"))

        # Generate markdown
        md_content = f"# {input_path.stem}\n\n"
        md_content += f"**Generated**: {datetime.now(UTC).isoformat()}\n"
        md_content += f"**Source**: `{input_path.name}`\n\n"
        md_content += "---\n\n"
        md_content += json_to_markdown(json_data)

        # Determine output path
        if output_path is None:
            output_path = input_path.with_suffix(".md")

        # Write markdown
        output_path.write_text(md_content, encoding="utf-8")
        print(f"✅ Converted {input_path.name} → {output_path.name}")
        return 0

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {input_path}: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Failed to convert {input_path}: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description="Convert JSON files to markdown")
    parser.add_argument("input", type=Path, help="Input JSON file path")
    parser.add_argument("--output", type=Path, help="Output markdown file path (default: input with .md extension)")

    args = parser.parse_args()

    return convert_file(args.input, args.output)


if __name__ == "__main__":
    sys.exit(main())
