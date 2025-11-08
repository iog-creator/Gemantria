# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
document_management_hints.py — Hint system integration for document management

Provides LOUD HINTS for document management operations per Rule-050 OPS Contract.
Automatically triggers when document operations are needed.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Load environment variables
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from infra.env_loader import ensure_env_loaded

ensure_env_loaded()

import psycopg


class DocumentManagementHints:
    """Manages hints for document management operations."""

    def __init__(self):
        self.run_id = f"doc_hints_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def emit_hint(self, hint_text: str, rule_reference: str = "058", context: str = "document_management"):
        """Emit a LOUD HINT for document management."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT log_hint_emission(%s, %s, %s, %s, %s)
                """,
                    (self.run_id, hint_text, rule_reference, "scripts/document_management_hints.py", context),
                )
                conn.commit()

        print(f"📢 LOUD HINT [{rule_reference}]: {hint_text}")

    def check_document_freshness(self) -> bool:
        """Check if documents need updating per Rule-058."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM check_governance_freshness(24)
                    WHERE is_stale = true AND artifact_name LIKE '%.md'
                """)
                stale_docs = cur.fetchone()[0]

                if stale_docs > 0:
                    self.emit_hint(
                        f"🚨 {stale_docs} documents are stale (>24h old). Run document management update.", "058"
                    )
                    return False

        return True

    def check_document_completeness(self) -> bool:
        """Check if master reference has required sections."""
        required_sections = {
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
        }

        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT section_name FROM document_sections 
                    WHERE document_name = 'GEMATRIA_MASTER_REFERENCE.md'
                """)
                existing_sections = {row[0] for row in cur.fetchall()}

                missing = required_sections - existing_sections
                if missing:
                    self.emit_hint(
                        f"📝 Master reference missing {len(missing)} critical sections: {', '.join(list(missing)[:3])}{'...' if len(missing) > 3 else ''}",
                        "027",
                    )
                    return False

        return True

    def check_ai_learning_coverage(self) -> bool:
        """Check if AI learning system covers document operations."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Check for document-related learning events
                cur.execute("""
                    SELECT COUNT(*) FROM learning_events 
                    WHERE learning_type = 'document_management'
                    AND created_at >= NOW() - INTERVAL '7 days'
                """)
                recent_learning = cur.fetchone()[0]

                if recent_learning == 0:
                    self.emit_hint(
                        "🧠 AI learning system lacks recent document management training. Consider logging document operation patterns.",
                        "061",
                    )
                    return False

        return True

    def check_tool_usage_analytics(self) -> bool:
        """Check if document tools have usage analytics."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM tool_usage_analytics 
                    WHERE tool_name LIKE '%document%' 
                    AND last_used >= NOW() - INTERVAL '7 days'
                """)
                recent_usage = cur.fetchone()[0]

                if recent_usage == 0:
                    self.emit_hint(
                        "📊 Document tools lack recent usage analytics. Run document management operations to populate metrics.",
                        "061",
                    )
                    return False

        return True

    def run_all_checks(self):
        """Run all document management hint checks."""
        print("🔍 Running document management hint checks...")

        checks = [
            ("Document Freshness", self.check_document_freshness),
            ("Document Completeness", self.check_document_completeness),
            ("AI Learning Coverage", self.check_ai_learning_coverage),
            ("Tool Usage Analytics", self.check_tool_usage_analytics),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                passed = check_func()
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}: {'PASS' if passed else 'HINT EMITTED'}")
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ {check_name}: ERROR - {e}")
                all_passed = False

        if all_passed:
            print("✅ All document management checks passed!")
        else:
            print("⚠️  Some document management hints were emitted. Check hint_emissions table.")

        return all_passed


def main():
    """Main function for document management hints."""
    hints = DocumentManagementHints()
    success = hints.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
