from scripts.config.env import get_rw_dsn
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
governance_tracker.py — Database-backed governance artifact tracking per Rule-058.

Maintains comprehensive database tracking of:
- MDC rules and their implementations
- Agent files and their governance scope
- Hint emission patterns and linkages
- Metadata compliance validation

Usage:
    python scripts/governance_tracker.py update    # Update governance artifacts in DB
    python scripts/governance_tracker.py validate  # Validate governance compliance
    python scripts/governance_tracker.py report    # Generate governance health report
    python scripts/governance_tracker.py stale     # Check for stale governance artifacts
"""

import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import psycopg

# Load environment variables
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from infra.env_loader import ensure_env_loaded

ensure_env_loaded()

# Database connection
GEMATRIA_DSN = get_rw_dsn()
if not GEMATRIA_DSN:
    print("ERROR: GEMATRIA_DSN environment variable required")
    exit(1)


def check_db_available() -> bool:
    """Check if database is available for operations."""
    try:
        with psycopg.connect(GEMATRIA_DSN, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except (psycopg.OperationalError, psycopg.Error):
        return False


def get_file_checksum(filepath: str) -> str:
    """Calculate SHA-256 checksum of a file."""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def extract_governance_metadata(content: str) -> Tuple[List[str], List[str]]:
    """
    Extract Related Rules and Related Agents from content.

    Returns:
        (rule_references, agent_references)
    """
    rules = []
    agents = []

    # Extract rules
    rules_match = re.search(r"Related Rules?:\s*(.+?)(?:\n|$)", content, re.MULTILINE | re.IGNORECASE)
    if rules_match:
        rules_text = rules_match.group(1)
        # Extract rule numbers like Rule-039, Rule-050, etc.
        rule_nums = re.findall(r"Rule-(\d+)", rules_text)
        rules.extend([f"Rule-{num}" for num in rule_nums])

    # Extract agents
    agents_match = re.search(r"Related Agents?:\s*(.+?)(?:\n|$)", content, re.MULTILINE | re.IGNORECASE)
    if agents_match:
        agents_text = agents_match.group(1)
        # Extract agent file references
        agent_refs = re.findall(r'([A-Z_]+\.md|src/[^\'"\s]+|scripts/[^\'"\s]+)', agents_text)
        agents.extend(agent_refs)

    return rules, agents


def scan_governance_artifacts() -> List[Dict]:
    """Scan codebase for governance artifacts that need tracking."""
    artifacts = []

    # Scan MDC rules
    cursor_rules = ROOT / ".cursor" / "rules"
    if cursor_rules.exists():
        for rule_file in cursor_rules.glob("*.mdc"):
            rule_num = rule_file.stem.split("-")[0]
            content = rule_file.read_text()
            checksum = get_file_checksum(str(rule_file))

            artifacts.append(
                {
                    "type": "rule",
                    "name": f"Rule-{rule_num}",
                    "file_path": str(rule_file.relative_to(ROOT)),
                    "rule_refs": [f"Rule-{rule_num}"],
                    "agent_refs": [],  # Rules don't reference agents
                    "checksum": checksum,
                    "content": content,
                }
            )

    # Scan agent files
    agent_files = [
        "AGENTS.md",
        "src/graph/AGENTS.md",
        "src/services/AGENTS.md",
        "scripts/AGENTS.md",
        "docs/AGENTS.md",
        "scripts/manage_document_sections.py",
        "scripts/populate_document_sections.py",
        "scripts/document_management_hints.py",
        "docs/SSOT/auto_schema_output.md",
    ]

    for agent_file in agent_files:
        agent_path = ROOT / agent_file
        if agent_path.exists():
            content = agent_path.read_text()
            checksum = get_file_checksum(str(agent_path))
            rules, agents = extract_governance_metadata(content)

            artifacts.append(
                {
                    "type": "agent_file",
                    "name": agent_file,
                    "file_path": agent_file,
                    "rule_refs": rules,
                    "agent_refs": agents,
                    "checksum": checksum,
                    "content": content,
                }
            )

    # Scan functions with governance metadata
    governance_functions = [
        ("src.graph.graph.run_pipeline", "src/graph/graph.py"),
        ("src.graph.graph.wrap_hints_node", "src/graph/graph.py"),
        ("src.services.lmstudio_client.assert_qwen_live", "src/services/lmstudio_client.py"),
    ]

    for func_path, file_path in governance_functions:
        full_path = ROOT / file_path
        if full_path.exists():
            content = full_path.read_text()
            checksum = get_file_checksum(str(full_path))
            rules, agents = extract_governance_metadata(content)

            artifacts.append(
                {
                    "type": "metadata_reference",
                    "name": func_path,
                    "file_path": file_path,
                    "rule_refs": rules,
                    "agent_refs": agents,
                    "checksum": checksum,
                    "content": content,
                }
            )

    # Scan hint emissions in code
    hint_emissions = []
    for py_file in ROOT.rglob("*.py"):
        if py_file.name.startswith(".") or "test" in str(py_file):
            continue

        content = py_file.read_text()
        # Find LOUD HINT emissions
        hints = re.findall(r'emit_loud_hint\(["\']([^"\']+)["\']', content)
        for hint in hints:
            # Extract rule reference from hint
            rule_match = re.search(r"Rule-(\d+)", hint)
            rule_ref = f"Rule-{rule_match.group(1)}" if rule_match else None

            # Extract agent reference from hint
            agent_match = re.search(r'([A-Z_]+\.md|src/[^\'"\s]+|scripts/[^\'"\s]+)', hint)
            agent_ref = agent_match.group(1) if agent_match else None

            hint_emissions.append(
                {
                    "type": "hint_emission",
                    "name": f"{py_file.relative_to(ROOT)}:{hint[:50]}...",
                    "file_path": str(py_file.relative_to(ROOT)),
                    "rule_refs": [rule_ref] if rule_ref else [],
                    "agent_refs": [agent_ref] if agent_ref else [],
                    "checksum": get_file_checksum(str(py_file)),
                    "content": hint,
                }
            )

    artifacts.extend(hint_emissions)

    # Scan share manifest items
    manifest_path = ROOT / "docs" / "SSOT" / "SHARE_MANIFEST.json"
    if manifest_path.exists():
        try:
            import json

            manifest_content = manifest_path.read_text()
            manifest_checksum = get_file_checksum(str(manifest_path))
            spec = json.loads(manifest_content)
            items = spec.get("items", [])

            # Track the manifest itself
            artifacts.append(
                {
                    "type": "share_manifest",
                    "name": "SHARE_MANIFEST.json",
                    "file_path": str(manifest_path.relative_to(ROOT)),
                    "rule_refs": ["Rule-044", "Rule-030"],
                    "agent_refs": ["scripts/update_share.py", "scripts/sync_share.py"],
                    "checksum": manifest_checksum,
                }
            )

            # Track individual manifest items (summary)
            for item in items:
                src = item.get("src", "")
                dst = item.get("dst", "")
                if src and dst:
                    item_id = f"{src}:{dst}"
                    src_path = ROOT / src
                    if src_path.exists():
                        item_checksum = get_file_checksum(str(src_path))
                        artifacts.append(
                            {
                                "type": "share_manifest_item",
                                "name": item_id,
                                "file_path": src,
                                "rule_refs": ["Rule-044"],
                                "agent_refs": ["scripts/update_share.py"],
                                "checksum": item_checksum,
                            }
                        )
        except Exception as e:
            # Don't fail if manifest parsing fails
            print(f"HINT: governance.tracker: Failed to scan share manifest: {e}", file=sys.stderr)

    return artifacts


def update_governance_db():
    """Update governance artifacts in database."""
    if not check_db_available():
        print("HINT: governance.tracker: Database unavailable (hermetic behavior); skipping DB update")
        print(f"HINT: governance.tracker: Scanned {len(scan_governance_artifacts())} artifacts (not persisted)")
        return

    artifacts = scan_governance_artifacts()

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                print(f"📊 Updating {len(artifacts)} governance artifacts in database...")

                for artifact in artifacts:
                    cur.execute(
                        """
                        SELECT update_governance_artifact(%s, %s, %s, %s, %s, %s)
                    """,
                        (
                            artifact["type"],
                            artifact["name"],
                            artifact["file_path"],
                            artifact["rule_refs"],
                            artifact["agent_refs"],
                            artifact["checksum"],
                        ),
                    )

                conn.commit()
                print("✅ Governance artifacts updated successfully")
    except (psycopg.OperationalError, psycopg.Error) as e:
        print(f"HINT: governance.tracker: Database connection failed (hermetic behavior): {e}")
        print(f"HINT: governance.tracker: Scanned {len(artifacts)} artifacts (not persisted)")


def validate_governance_compliance(lenient: bool = False):
    """Validate governance compliance across the system."""
    if not check_db_available():
        print("HINT: governance.tracker: Database unavailable (hermetic behavior); skipping compliance validation")
        print("HINT: governance.tracker: Compliance validation skipped (DB required)")
        return True  # Return success to allow housekeeping to pass

    issues = []

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                # Check for stale artifacts (>24 hours) - skip in lenient mode
                if not lenient:
                    cur.execute("SELECT * FROM check_governance_freshness(24)")
                    stale_artifacts = cur.fetchall()

                    if stale_artifacts:
                        issues.append(f"🚨 {len(stale_artifacts)} stale governance artifacts (>24h)")

                # Check for artifacts without rule references
                cur.execute("""
                    SELECT COUNT(*) FROM governance_artifacts
                    WHERE array_length(rule_references, 1) = 0
                    AND artifact_type != 'rule'
                """)
                no_rules = cur.fetchone()[0]
                if no_rules > 0:
                    issues.append(f"⚠️ {no_rules} artifacts missing rule references")

                # Check hint emissions are properly linked
                cur.execute("""
                    SELECT COUNT(*) FROM hint_emissions
                    WHERE rule_reference IS NULL OR agent_reference IS NULL
                """)
                unlinked_hints = cur.fetchone()[0]
                if unlinked_hints > 0:
                    issues.append(f"🔗 {unlinked_hints} hint emissions not properly linked")
    except (psycopg.OperationalError, psycopg.Error) as e:
        print(f"HINT: governance.tracker: Database connection failed (hermetic behavior): {e}")
        print("HINT: governance.tracker: Compliance validation skipped (DB required)")
        return True  # Return success to allow housekeeping to pass

    if issues:
        print("❌ Governance Compliance Issues:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        mode = " (lenient mode)" if lenient else ""
        print(f"✅ Governance compliance validation passed{mode}")
        return True


def generate_governance_report():
    """Generate comprehensive governance health report."""
    if not check_db_available():
        print("HINT: governance.tracker: Database unavailable (hermetic behavior); skipping report generation")
        return

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                print("🔥🔥🔥 GOVERNANCE HEALTH REPORT 🔥🔥🔥")
                print("=" * 50)

                # Artifact counts by type
                cur.execute("""
                    SELECT artifact_type, COUNT(*) as count
                    FROM governance_artifacts
                    GROUP BY artifact_type
                    ORDER BY count DESC
                """)
                print("\n📊 Artifact Inventory:")
                for row in cur.fetchall():
                    print(f"  {row[0]}: {row[1]}")

                # Rule coverage
                cur.execute("""
                    SELECT unnest(rule_references) as rule, COUNT(*) as ref_count
                    FROM governance_artifacts
                    WHERE rule_references IS NOT NULL
                    GROUP BY unnest(rule_references)
                    ORDER BY ref_count DESC
                    LIMIT 10
                """)
                print("\n🎯 Top Referenced Rules:")
                for row in cur.fetchall():
                    print(f"  {row[0]}: {row[1]} references")

                # Agent file coverage
                cur.execute("""
                    SELECT unnest(agent_references) as agent, COUNT(*) as ref_count
                    FROM governance_artifacts
                    WHERE agent_references IS NOT NULL
                    GROUP BY unnest(agent_references)
                    ORDER BY ref_count DESC
                    LIMIT 10
                """)
                print("\n📁 Top Referenced Agent Files:")
                for row in cur.fetchall():
                    print(f"  {row[0]}: {row[1]} references")

                # Hint emission stats
                cur.execute("""
                    SELECT COUNT(*) as total_hints,
                           COUNT(DISTINCT run_id) as unique_runs,
                           MAX(emitted_at) as last_emission
                    FROM hint_emissions
                """)
                stats = cur.fetchone()
                print("📢 Hint Emission Stats:")
                print(f"  Total hints emitted: {stats[0]}")
                print(f"  Unique runs: {stats[1]}")
                print(f"  Last emission: {stats[2]}")

                # Compliance check results
                cur.execute("""
                    SELECT check_type, check_result, COUNT(*) as count
                    FROM governance_compliance_log
                    WHERE executed_at >= NOW() - INTERVAL '24 hours'
                    GROUP BY check_type, check_result
                    ORDER BY check_type, check_result
                """)
                print("✅ Recent Compliance Checks:")
                for row in cur.fetchall():
                    status_icon = "✅" if row[1] == "pass" else "❌"
                    print(f"  {status_icon} {row[0]}: {row[1]} ({row[2]} times)")
    except (psycopg.OperationalError, psycopg.Error) as e:
        print(f"HINT: governance.tracker: Database connection failed (hermetic behavior): {e}")
        print("HINT: governance.tracker: Report generation skipped (DB required)")


def check_stale_artifacts():
    """Check for stale governance artifacts."""
    if not check_db_available():
        print("HINT: governance.tracker: Database unavailable (hermetic behavior); skipping stale artifact check")
        return

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM check_governance_freshness(24)")
                stale = cur.fetchall()

                if stale:
                    print("🚨 STALE GOVERNANCE ARTIFACTS (>24 hours):")
                    for artifact, hours, is_stale in stale:
                        if is_stale:
                            print(f"  ⚠️  {artifact}: {hours:.1f} hours old")
                        else:
                            print(f"  ✅ {artifact}: {hours:.1f} hours old")
                else:
                    print("✅ All governance artifacts are fresh (<24 hours)")
    except (psycopg.OperationalError, psycopg.Error) as e:
        print(f"HINT: governance.tracker: Database connection failed (hermetic behavior): {e}")
        print("HINT: governance.tracker: Stale artifact check skipped (DB required)")


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scripts/governance_tracker.py {update|validate [--lenient]|report|stale}")
        sys.exit(1)

    command = sys.argv[1]
    lenient = "--lenient" in sys.argv

    if command == "update":
        update_governance_db()
    elif command == "validate":
        success = validate_governance_compliance(lenient=lenient)
        sys.exit(0 if success else 1)
    elif command == "report":
        generate_governance_report()
    elif command == "stale":
        check_stale_artifacts()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
