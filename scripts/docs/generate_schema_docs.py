#!/usr/bin/env python3
"""
Generate Markdown documentation from JSON Schema files.

Usage: python3 scripts/docs/generate_schema_docs.py [--schema-dir docs/SSOT] [--output-dir docs/schemas]
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict


def format_schema_property(name: str, prop: Dict[str, Any], required: bool = False) -> str:
    """Format a single schema property as Markdown."""
    prop_type = prop.get("type", "any")
    description = prop.get("description", "")
    default = prop.get("default")
    enum = prop.get("enum")

    lines = [f"### `{name}`"]
    if required:
        lines.append("**Required**")
    lines.append(f"**Type**: `{prop_type}`")
    if description:
        lines.append(f"**Description**: {description}")
    if default is not None:
        lines.append(f"**Default**: `{json.dumps(default)}`")
    if enum:
        lines.append(f"**Allowed values**: {', '.join(str(v) for v in enum)}")

    # Handle nested objects
    if prop_type == "object" and "properties" in prop:
        lines.append("\n**Properties**:")
        for sub_name, sub_prop in prop["properties"].items():
            sub_required = name in prop.get("required", [])
            lines.append(f"\n{format_schema_property(sub_name, sub_prop, sub_required)}")

    # Handle arrays
    if prop_type == "array" and "items" in prop:
        lines.append("\n**Items**:")
        items = prop["items"]
        if isinstance(items, dict):
            if "type" in items:
                lines.append(f"- Type: `{items['type']}`")
            if "properties" in items:
                lines.append("- Properties:")
                for sub_name, sub_prop in items["properties"].items():
                    lines.append(f"  - `{sub_name}`: {sub_prop.get('description', '')}")

    return "\n".join(lines)


def generate_schema_doc(schema_path: pathlib.Path) -> str:
    """Generate Markdown documentation from a JSON Schema file."""
    with schema_path.open(encoding="utf-8") as f:
        schema = json.load(f)

    title = schema.get("title", schema_path.stem)
    description = schema.get("description", "")

    lines = [
        f"# {title}",
        "",
        description,
        "",
        "## Schema Definition",
        "",
        f"**File**: `{schema_path.name}`",
        "",
    ]

    # Schema metadata
    if "$schema" in schema:
        lines.append(f"**JSON Schema Version**: {schema['$schema']}")
    if "version" in schema:
        lines.append(f"**Schema Version**: {schema['version']}")

    lines.append("")

    # Properties
    if "properties" in schema:
        lines.append("## Properties")
        lines.append("")
        required = schema.get("required", [])
        for prop_name, prop_def in schema["properties"].items():
            lines.append(format_schema_property(prop_name, prop_def, prop_name in required))
            lines.append("")

    # Examples
    if "examples" in schema:
        lines.append("## Examples")
        lines.append("")
        for i, example in enumerate(schema["examples"], 1):
            lines.append(f"### Example {i}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(example, indent=2))
            lines.append("```")
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Markdown docs from JSON Schema files")
    parser.add_argument(
        "--schema-dir",
        type=pathlib.Path,
        default=pathlib.Path("docs/SSOT"),
        help="Directory containing JSON Schema files",
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=pathlib.Path("docs/schemas"),
        help="Output directory for generated Markdown files",
    )
    args = parser.parse_args()

    schema_dir = args.schema_dir.resolve()
    output_dir = args.output_dir.resolve()

    if not schema_dir.exists():
        print(f"Error: Schema directory not found: {schema_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all JSON schema files
    schema_files = list(schema_dir.glob("*.schema.json")) + list(schema_dir.glob("SSOT_*.json"))

    if not schema_files:
        print(f"No schema files found in {schema_dir}")
        return 0

    print(f"Generating schema docs from {len(schema_files)} files...")

    for schema_file in schema_files:
        try:
            doc_content = generate_schema_doc(schema_file)
            output_file = output_dir / f"{schema_file.stem}.md"
            output_file.write_text(doc_content, encoding="utf-8")
            print(f"  ✓ {schema_file.name} → {output_file.name}")
        except Exception as e:
            print(f"  ✗ Error processing {schema_file.name}: {e}")
            return 1

    print(f"\n✅ Generated {len(schema_files)} schema documentation files in {output_dir}")
    return 0


if __name__ == "__main__":
    exit(main())
