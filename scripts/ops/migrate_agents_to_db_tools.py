#!/usr/bin/env python3
"""
Migration Script: Migrate Agents to DB Tools (M3)
=================================================
Verifies that BibleScholar flows use registered MCP tools instead of direct DB adapters.

Migration Status:
- search_flow.py: Uses search_bible_verses tool ✓
- lexicon_flow.py: fetch_lexicon_entry uses lookup_lexicon_entry tool ✓
- lexicon_flow.py: fetch_word_study uses adapter (infrastructure, exempted) ✓
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def check_file_uses_tool(file_path: Path, tool_name: str) -> bool:
    """Check if file imports and uses the specified tool."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Check for tool import
        has_import = False
        has_usage = False

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.ImportFrom):
                if node.module and "tools" in node.module:
                    for alias in node.names:
                        if alias.name == tool_name:
                            has_import = True

            # Check function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == tool_name:
                        has_usage = True
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr == tool_name:
                        has_usage = True

        return has_import and has_usage
    except Exception as e:
        print(f"ERROR: Failed to parse {file_path}: {e}")
        return False


def verify_migration():
    """Verify migration status."""
    print("🔍 Verifying M3 Migration Status...")
    print()

    all_ok = True

    # Check search_flow.py
    search_flow = REPO_ROOT / "agentpm" / "biblescholar" / "search_flow.py"
    if search_flow.exists():
        uses_tool = check_file_uses_tool(search_flow, "search_bible_verses")
        if uses_tool:
            print("✅ agentpm/biblescholar/search_flow.py: Uses search_bible_verses tool")
        else:
            print("❌ agentpm/biblescholar/search_flow.py: Does NOT use search_bible_verses tool")
            all_ok = False
    else:
        print("⚠️  agentpm/biblescholar/search_flow.py: File not found")
        all_ok = False

    # Check lexicon_flow.py
    lexicon_flow = REPO_ROOT / "agentpm" / "biblescholar" / "lexicon_flow.py"
    if lexicon_flow.exists():
        uses_tool = check_file_uses_tool(lexicon_flow, "lookup_lexicon_entry")
        if uses_tool:
            print("✅ agentpm/biblescholar/lexicon_flow.py: Uses lookup_lexicon_entry tool")
        else:
            print("❌ agentpm/biblescholar/lexicon_flow.py: Does NOT use lookup_lexicon_entry tool")
            all_ok = False
    else:
        print("⚠️  agentpm/biblescholar/lexicon_flow.py: File not found")
        all_ok = False

    # Check tools/bible.py exists
    bible_tools = REPO_ROOT / "agentpm" / "tools" / "bible.py"
    if bible_tools.exists():
        print("✅ agentpm/tools/bible.py: Tool implementations present")
    else:
        print("❌ agentpm/tools/bible.py: File not found")
        all_ok = False

    print()
    if all_ok:
        print("✅ Migration verified successfully.")
        print("   All flows use registered MCP tools where applicable.")
        print("   Note: fetch_word_study() uses adapter (infrastructure, exempted from guard).")
        return 0
    else:
        print("❌ Migration verification failed.")
        print("   Some flows still use direct adapters instead of tools.")
        return 1


if __name__ == "__main__":
    sys.exit(verify_migration())
