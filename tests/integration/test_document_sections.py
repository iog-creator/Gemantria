#!/usr/bin/env python3
"""
test_document_sections.py — Integration tests for document sections tracking system

Tests the document_sections table and related functionality for AI-assisted
document management per Rule-061 AI Learning Tracking.
"""

import os
import hashlib
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

import psycopg


class TestDocumentSections:
    """Test document sections tracking functionality."""

    def test_document_sections_table_exists(self):
        """Test that document_sections table exists and has correct schema."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Check table exists
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = 'document_sections'
                """)
                assert cur.fetchone()[0] == 1

                # Check required columns exist
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'document_sections' 
                    ORDER BY column_name
                """)
                columns = [row[0] for row in cur.fetchall()]
                required_columns = [
                    "id",
                    "document_name",
                    "section_name",
                    "section_path",
                    "section_level",
                    "parent_section",
                    "content_hash",
                    "word_count",
                    "last_updated",
                    "created_at",
                ]
                for col in required_columns:
                    assert col in columns, f"Missing column: {col}"

    def test_update_document_section_function(self):
        """Test the update_document_section function works correctly."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Test inserting new section
                test_doc = "test_document.md"
                test_section = "Test Section"
                test_path = "/tmp/test.md"
                test_hash = hashlib.sha256(b"test content").hexdigest()

                cur.execute(
                    """
                    SELECT update_document_section(%s, %s, %s, %s, %s, %s, %s)
                """,
                    (test_doc, test_section, test_path, 2, None, test_hash, 25),
                )

                # Verify it was inserted
                cur.execute(
                    """
                    SELECT section_name, section_level, word_count 
                    FROM document_sections 
                    WHERE document_name = %s AND section_name = %s
                """,
                    (test_doc, test_section),
                )

                row = cur.fetchone()
                assert row is not None
                assert row[0] == test_section
                assert row[1] == 2
                assert row[2] == 25

                # Test updating existing section
                cur.execute(
                    """
                    SELECT update_document_section(%s, %s, %s, %s, %s, %s, %s)
                """,
                    (test_doc, test_section, test_path, 2, None, test_hash, 30),
                )

                # Verify word count was updated
                cur.execute(
                    """
                    SELECT word_count FROM document_sections 
                    WHERE document_name = %s AND section_name = %s
                """,
                    (test_doc, test_section),
                )

                assert cur.fetchone()[0] == 30

                # Cleanup
                cur.execute("DELETE FROM document_sections WHERE document_name = %s", (test_doc,))
                conn.commit()

    def test_get_document_hierarchy_function(self):
        """Test the get_document_hierarchy function returns correct structure."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Insert test data
                test_doc = "hierarchy_test.md"
                sections_data = [
                    ("Root Section", 1, None, 10),
                    ("Subsection 1", 2, "Root Section", 15),
                    ("Subsection 2", 2, "Root Section", 20),
                    ("Sub-subsection", 3, "Subsection 1", 5),
                ]

                for section_name, level, parent, words in sections_data:
                    test_hash = hashlib.sha256(f"{section_name} content".encode()).hexdigest()
                    cur.execute(
                        """
                        SELECT update_document_section(%s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            test_doc,
                            section_name,
                            f"/tmp/{test_doc}",
                            level,
                            parent,
                            test_hash,
                            words,
                        ),
                    )

                # Test hierarchy function
                cur.execute("SELECT * FROM get_document_hierarchy(%s)", (test_doc,))
                hierarchy = cur.fetchall()

                # Should return all sections with correct hierarchy
                assert len(hierarchy) == 4

                # Find root section
                root = next(row for row in hierarchy if row[0] == "Root Section")
                assert root[1] == 1  # level
                assert root[2] is None  # parent

                # Find subsections
                sub1 = next(row for row in hierarchy if row[0] == "Subsection 1")
                assert sub1[1] == 2
                assert sub1[2] == "Root Section"

                # Cleanup
                cur.execute("DELETE FROM document_sections WHERE document_name = %s", (test_doc,))
                conn.commit()

    def test_master_reference_tracking(self):
        """Test that master reference document is properly tracked."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Check that master reference has sections tracked
                cur.execute("""
                    SELECT COUNT(*) FROM document_sections 
                    WHERE document_name = 'GEMATRIA_MASTER_REFERENCE.md'
                """)
                count = cur.fetchone()[0]
                assert count > 100, f"Expected >100 sections, got {count}"

                # Check that it has proper hierarchy (different levels)
                cur.execute("""
                    SELECT DISTINCT section_level FROM document_sections 
                    WHERE document_name = 'GEMATRIA_MASTER_REFERENCE.md'
                    ORDER BY section_level
                """)
                levels = [row[0] for row in cur.fetchall()]
                assert 1 in levels, "Should have level 1 sections"
                assert 2 in levels, "Should have level 2 sections"
                assert len(levels) >= 3, f"Should have multiple levels, got {levels}"

    def test_document_sections_uniqueness(self):
        """Test that document sections maintain uniqueness constraints."""
        with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
            with conn.cursor() as cur:
                # Test unique constraint on (document_name, section_name)
                test_doc = "uniqueness_test.md"

                # Insert first section
                cur.execute(
                    """
                    SELECT update_document_section(%s, %s, %s, %s, %s, %s, %s)
                """,
                    (test_doc, "Test Section", "/tmp/test.md", 1, None, "hash1", 10),
                )

                # Try to insert duplicate - should not error (ON CONFLICT DO UPDATE)
                cur.execute(
                    """
                    SELECT update_document_section(%s, %s, %s, %s, %s, %s, %s)
                """,
                    (test_doc, "Test Section", "/tmp/test.md", 1, None, "hash2", 15),
                )

                # Should still have only one record
                cur.execute(
                    """
                    SELECT COUNT(*) FROM document_sections 
                    WHERE document_name = %s AND section_name = %s
                """,
                    (test_doc, "Test Section"),
                )

                assert cur.fetchone()[0] == 1

                # Cleanup
                cur.execute("DELETE FROM document_sections WHERE document_name = %s", (test_doc,))
                conn.commit()
