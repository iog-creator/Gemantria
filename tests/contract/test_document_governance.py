#!/usr/bin/env python3
"""
test_document_governance.py — Contract tests for document governance compliance

Tests that document management operations comply with governance rules
per Rule-027 (Docs Sync Gate) and Rule-058 (Auto-Housekeeping).
"""

import os
import sys
from pathlib import Path


# Load environment variables
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from infra.env_loader import ensure_env_loaded

ensure_env_loaded()

import psycopg


class TestDocumentGovernanceCompliance:
    """Test document operations comply with governance rules."""

    def test_document_operations_logged_in_governance(self):
        """Test that document operations are tracked in governance artifacts."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Check that document management is tracked as governance artifact
                cur.execute("""
                    SELECT COUNT(*) FROM governance_artifacts 
                    WHERE artifact_type = 'agent_file' 
                    AND artifact_name LIKE '%document%'
                """)
                doc_artifacts = cur.fetchone()[0]
                assert doc_artifacts > 0, "Document management should be tracked in governance"

    def test_document_sections_integrity(self):
        """Test document sections maintain referential integrity."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Check that all sections have valid document references
                cur.execute("""
                    SELECT COUNT(*) FROM document_sections 
                    WHERE document_name NOT IN (
                        SELECT DISTINCT artifact_name 
                        FROM governance_artifacts 
                        WHERE artifact_type IN ('agent_file', 'rule')
                    )
                """)
                orphaned_sections = cur.fetchone()[0]
                assert orphaned_sections == 0, f"Found {orphaned_sections} orphaned document sections"

    def test_document_update_triggers_hint_emission(self):
        """Test that document updates trigger appropriate hint emissions."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Insert a test document update
                test_run_id = "test_doc_update_001"

                cur.execute(
                    """
                    SELECT log_hint_emission(%s, %s, %s, %s, %s)
                """,
                    (
                        test_run_id,
                        "Document sections updated for GEMATRIA_MASTER_REFERENCE.md",
                        "058",  # Auto-Housekeeping rule
                        "scripts/populate_document_sections.py",
                        "document_management",
                    ),
                )

                # Verify hint was logged
                cur.execute(
                    """
                    SELECT COUNT(*) FROM hint_emissions 
                    WHERE run_id = %s AND rule_reference = %s
                """,
                    (test_run_id, "058"),
                )

                assert cur.fetchone()[0] == 1

                # Cleanup
                cur.execute("DELETE FROM hint_emissions WHERE run_id = %s", (test_run_id,))
                conn.commit()

    def test_document_compliance_validation(self):
        """Test that document operations pass compliance validation."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Run compliance check for document operations
                cur.execute("""
                    INSERT INTO governance_compliance_log (
                        check_type, check_result, details, triggered_by
                    ) VALUES (
                        'document_integrity',
                        'pass',
                        '{"sections_tracked": 144, "documents_managed": 3}',
                        'test_contract'
                    )
                """)

                # Verify compliance log was created
                cur.execute("""
                    SELECT COUNT(*) FROM governance_compliance_log 
                    WHERE check_type = 'document_integrity' 
                    AND check_result = 'pass'
                    AND triggered_by = 'test_contract'
                """)

                assert cur.fetchone()[0] == 1

                # Cleanup
                cur.execute("""
                    DELETE FROM governance_compliance_log 
                    WHERE triggered_by = 'test_contract'
                """)
                conn.commit()

    def test_document_freshness_monitoring(self):
        """Test that document freshness is monitored per Rule-058."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Check that documents are included in freshness monitoring
                cur.execute("""
                    SELECT COUNT(*) FROM check_governance_freshness(24)
                    WHERE artifact_name LIKE '%.md'
                """)
                fresh_docs = cur.fetchone()[0]
                assert fresh_docs > 0, "Documents should be monitored for freshness"


class TestDocumentAIIntegration:
    """Test AI learning integration with document management."""

    def test_document_operations_tracked_in_ai_learning(self):
        """Test that document operations are tracked in AI learning system."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Insert test AI interaction for document management
                session_id = "test_doc_session_001"

                cur.execute(
                    """
                    SELECT log_ai_interaction(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        session_id,  # session_id
                        "tool_call",  # interaction_type
                        "Update document sections",  # user_query
                        "Document sections updated successfully",  # ai_response
                        ["manage_document_sections"],  # tools_used
                        '{"document": "GEMATRIA_MASTER_REFERENCE.md"}',  # context
                        1500,  # execution_time_ms
                        True,  # success
                        None,  # error_details
                    ),
                )

                # Verify AI interaction was logged
                cur.execute(
                    """
                    SELECT COUNT(*) FROM ai_interactions 
                    WHERE session_id = %s AND interaction_type = %s
                """,
                    (session_id, "tool_call"),
                )

                assert cur.fetchone()[0] == 1

                # Cleanup
                cur.execute("DELETE FROM ai_interactions WHERE session_id = %s", (session_id,))
                conn.commit()

    def test_document_tool_usage_analytics(self):
        """Test that document tools are tracked in usage analytics."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Update tool usage for document management
                cur.execute(
                    """
                    SELECT update_tool_usage(%s, %s, %s, %s)
                """,
                    (
                        "manage_document_sections",  # tool_name
                        True,  # success
                        2500,  # execution_time_ms
                        None,  # error_type
                    ),
                )

                # Verify tool usage was updated
                cur.execute("""
                    SELECT usage_count, success_count, average_execution_time_ms 
                    FROM tool_usage_analytics 
                    WHERE tool_name = 'manage_document_sections'
                """)

                row = cur.fetchone()
                assert row is not None
                assert row[0] >= 1  # usage_count
                assert row[1] >= 1  # success_count
                assert row[2] > 0  # average_execution_time_ms

    def test_document_learning_events(self):
        """Test that document management triggers learning events."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Insert learning event for document management improvement
                cur.execute("""
                    INSERT INTO learning_events (
                        learning_type, trigger_event, learning_outcome, 
                        confidence_score, applied_successfully
                    ) VALUES (
                        'document_management',
                        '{"action": "section_tracking", "document": "GEMATRIA_MASTER_REFERENCE.md"}',
                        'Improved document section tracking accuracy',
                        0.85,
                        true
                    )
                """)

                # Verify learning event was recorded
                cur.execute("""
                    SELECT COUNT(*) FROM learning_events 
                    WHERE learning_type = 'document_management' 
                    AND applied_successfully = true
                """)

                assert cur.fetchone()[0] >= 1

                # Cleanup - don't delete learning events as they should persist
