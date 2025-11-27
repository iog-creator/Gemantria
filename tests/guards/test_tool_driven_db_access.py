import ast
import os
from pathlib import Path
import pytest

# Directories/Files to scan
SCAN_ROOTS = ["agentpm"]

# Files/Directories to exempt from the guard
EXEMPTIONS = [
    "agentpm/db",
    "agentpm/control_plane",
    "agentpm/tools",
    "agentpm/biblescholar/bible_db_adapter.py",
    "agentpm/biblescholar/lexicon_adapter.py",
    "agentpm/biblescholar/vector_adapter.py",
    "agentpm/biblescholar/reference_parser.py",
    "agentpm/biblescholar/bible_passage_flow.py",  # Uses sqlalchemy for book mapping cache
    "agentpm/adapters",
    "agentpm/scripts",  # Ops scripts are infrastructure
    "agentpm/knowledge",  # Core knowledge retrieval infra
    "agentpm/dms",  # DMS infrastructure
    "agentpm/guarded",  # Gatekeeper infra
    "agentpm/status",  # Status reporting infra
    "agentpm/docs",  # Docs search infra
    "agentpm/runtime",  # Runtime infra (logging, budget)
]

# Forbidden patterns
FORBIDDEN_IMPORTS = ["psycopg", "sqlalchemy"]
FORBIDDEN_CALLS = ["connect", "execute"]  # Heuristic, checked with context


def is_exempt(path: str) -> bool:
    for exemption in EXEMPTIONS:
        if exemption in path:
            return True
    return False


def check_file_for_violations(file_path: str) -> list[str]:
    violations = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = getattr(node, "module", None)
                if module_name:
                    for forbidden in FORBIDDEN_IMPORTS:
                        if module_name.startswith(forbidden):
                            violations.append(f"Forbidden import '{module_name}' on line {node.lineno}")

                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in FORBIDDEN_IMPORTS:
                            if alias.name.startswith(forbidden):
                                violations.append(f"Forbidden import '{alias.name}' on line {node.lineno}")

            # Check calls (psycopg.connect, cursor.execute)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    # Check for .execute() calls that look like SQL execution
                    if attr_name == "execute":
                        # This is a weak heuristic, but catches cur.execute()
                        # We can try to see if the first arg is a string starting with SELECT/INSERT
                        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                            sql_keywords = ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "WITH "]
                            if any(node.args[0].value.strip().upper().startswith(k) for k in sql_keywords):
                                violations.append(f"Potential SQL execution detected on line {node.lineno}")

                    # Check for psycopg.connect
                    if attr_name == "connect":
                        # Hard to be sure without type inference, but we can check if 'psycopg' is in the name
                        if isinstance(node.func.value, ast.Name) and "psycopg" in node.func.value.id:
                            violations.append(f"Direct DB connection detected on line {node.lineno}")

    except Exception as e:
        violations.append(f"Error parsing file: {e}")

    return violations


def test_tool_driven_db_access_enforcement():
    """
    Guard: Enforce Tool-Driven Database Access (M3).
    Agents must not use raw SQL or direct DB connections.
    """
    repo_root = Path(os.getcwd())
    violations = {}

    for root_dir in SCAN_ROOTS:
        start_path = repo_root / root_dir
        if not start_path.exists():
            continue

        for path in start_path.rglob("*.py"):
            rel_path = str(path.relative_to(repo_root))

            if is_exempt(rel_path):
                continue

            if "tests" in rel_path.split(os.sep):
                continue

            file_violations = check_file_for_violations(str(path))
            if file_violations:
                violations[rel_path] = file_violations

    if violations:
        error_msg = "Tool-Driven DB Access Violations Detected:\n"
        for fpath, vlist in violations.items():
            error_msg += f"\nFile: {fpath}\n"
            for v in vlist:
                error_msg += f"  - {v}\n"

        pytest.fail(error_msg)


if __name__ == "__main__":
    # Allow running directly
    pytest.main([__file__])
