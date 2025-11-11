# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
manage_document_sections.py — AI-assisted document management utilities

Query, analyze, and manage document sections for AI-assisted maintenance.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Load environment variables via centralized loader
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.config.env import get_rw_dsn
import psycopg


def get_document_hierarchy(document_name: str) -> List[Dict]:
    """Get hierarchical view of document sections."""

    dsn = get_rw_dsn()
    if not dsn:
        raise ValueError("GEMATRIA_DSN not available (via centralized loader)")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT section_name, section_level, parent_section, word_count, last_updated
                FROM document_sections 
                WHERE document_name = %s 
                ORDER BY section_level, section_name
            """,
                (document_name,),
            )

            sections = []
            for row in cur.fetchall():
                sections.append(
                    {
                        "name": row[0],
                        "level": row[1],
                        "parent": row[2],
                        "word_count": row[3],
                        "last_updated": row[4],
                    }
                )

    return sections


def find_missing_sections(document_name: str, required_sections: List[str]) -> List[str]:
    """Find sections that are required but missing from document."""

    sections = get_document_hierarchy(document_name)
    existing_names = {s["name"] for s in sections}

    missing = []
    for required in required_sections:
        if required not in existing_names:
            missing.append(required)

    return missing


def get_section_stats(document_name: str) -> Dict:
    """Get statistics about document sections."""

    sections = get_document_hierarchy(document_name)

    stats = {
        "total_sections": len(sections),
        "sections_by_level": {},
        "total_words": 0,
        "empty_sections": 0,
    }

    for section in sections:
        level = section["level"]
        stats["sections_by_level"][level] = stats["sections_by_level"].get(level, 0) + 1
        stats["total_words"] += section["word_count"]
        if section["word_count"] == 0:
            stats["empty_sections"] += 1

    return stats


def suggest_missing_sections(document_name: str) -> List[str]:
    """Suggest sections that might be missing based on document type."""

    suggestions = {
        "GEMATRIA_MASTER_REFERENCE.md": [
            "Error Handling & Recovery",
            "Performance Optimization",
            "Security Considerations",
            "Testing Strategy",
            "Deployment Guide",
            "Troubleshooting Guide",
            "API Reference",
            "Configuration Examples",
            "Integration Examples",
            "Migration Guide",
        ],
        "AGENTS.md": [
            "Error Recovery Procedures",
            "Performance Benchmarks",
            "Security Protocols",
            "Testing Frameworks",
            "Integration Testing",
            "Performance Monitoring",
        ],
    }

    return suggestions.get(document_name, [])


def print_document_analysis(document_name: str):
    """Print comprehensive analysis of document sections."""

    print(f"📄 Document Analysis: {document_name}")
    print("=" * 50)

    # Get stats
    stats = get_section_stats(document_name)
    print("📊 Statistics:")
    print(f"  Total sections: {stats['total_sections']}")
    print(f"  Total words: {stats['total_words']}")
    print(f"  Empty sections: {stats['empty_sections']}")
    print(f"  Sections by level: {stats['sections_by_level']}")

    # Get hierarchy
    sections = get_document_hierarchy(document_name)

    print("\n📑 Section Hierarchy:")
    for section in sections[:20]:  # Show first 20
        indent = "  " * (section["level"] - 1)
        parent = f" (parent: {section['parent']})" if section["parent"] else ""
        words = f" [{section['word_count']} words]" if section["word_count"] > 0 else " [empty]"
        print(f"{indent}• {section['name']}{words}{parent}")

    if len(sections) > 20:
        print(f"... and {len(sections) - 20} more sections")

    # Suggest missing sections
    suggestions = suggest_missing_sections(document_name)
    if suggestions:
        print("\n💡 Suggested missing sections:")
        for suggestion in suggestions[:10]:
            print(f"  - {suggestion}")


def main():
    """Main function for document management."""

    if len(sys.argv) < 2:
        print("Usage: python scripts/manage_document_sections.py <command> [args...]")
        print("Commands:")
        print("  analyze <document>    - Analyze document sections")
        print("  hierarchy <document>  - Show section hierarchy")
        print("  missing <document>    - Find missing sections")
        print("  stats <document>      - Show section statistics")
        return

    command = sys.argv[1]

    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: python scripts/manage_document_sections.py analyze <document>")
            return
        document = sys.argv[2]
        print_document_analysis(document)

    elif command == "hierarchy":
        if len(sys.argv) < 3:
            print("Usage: python scripts/manage_document_sections.py hierarchy <document>")
            return
        document = sys.argv[2]
        sections = get_document_hierarchy(document)
        for section in sections:
            indent = "  " * (section["level"] - 1)
            print(f"{indent}{section['name']}")

    elif command == "stats":
        if len(sys.argv) < 3:
            print("Usage: python scripts/manage_document_sections.py stats <document>")
            return
        document = sys.argv[2]
        stats = get_section_stats(document)
        print(f"Stats for {document}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    elif command == "missing":
        if len(sys.argv) < 3:
            print("Usage: python scripts/manage_document_sections.py missing <document>")
            return
        document = sys.argv[2]
        suggestions = suggest_missing_sections(document)
        print(f"Suggested missing sections for {document}:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
