#!/usr/bin/env python3
"""
test_document_management.py — Unit tests for document management utilities

Tests the document management functions and utilities for AI-assisted
document management per Rule-061 AI Learning Tracking.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch


# Load environment variables
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from infra.env_loader import ensure_env_loaded

ensure_env_loaded()

from scripts.populate_document_sections import (
    parse_markdown_sections,
    calculate_content_hash,
    count_words,
    extract_section_content,
)
from scripts.manage_document_sections import (
    get_document_hierarchy,
    find_missing_sections,
    get_section_stats,
    suggest_missing_sections,
)


class TestDocumentParsing:
    """Test markdown document parsing functions."""

    def test_parse_markdown_sections_simple(self):
        """Test parsing simple markdown with headers."""
        content = """# Main Title

Some content here.

## Subsection 1

More content.

## Subsection 2

Even more content.

### Sub-subsection

Deep content.
"""

        sections = parse_markdown_sections(content)

        # Should find 4 sections
        assert len(sections) == 4

        # Check main title
        assert sections[0] == ("Main Title", 1, None)

        # Check subsections
        assert sections[1] == ("Subsection 1", 2, "Main Title")
        assert sections[2] == ("Subsection 2", 2, "Main Title")
        assert sections[3] == ("Sub-subsection", 3, "Subsection 1")

    def test_parse_markdown_sections_with_emojis(self):
        """Test parsing sections with emojis and special characters."""
        content = """# 🚀 Performance Optimization

Some content.

## ⚡ Pipeline Tuning

More content.

## 🔧 Database Optimization

Database content.
"""

        sections = parse_markdown_sections(content)

        assert len(sections) == 3
        assert sections[0][0] == "🚀 Performance Optimization"
        assert sections[1][0] == "⚡ Pipeline Tuning"
        assert sections[2][0] == "🔧 Database Optimization"

    def test_calculate_content_hash(self):
        """Test content hash calculation."""
        content1 = "Hello World"
        content2 = "Hello World"
        content3 = "Hello world"  # Different case

        hash1 = calculate_content_hash(content1)
        hash2 = calculate_content_hash(content2)
        hash3 = calculate_content_hash(content3)

        assert hash1 == hash2  # Same content
        assert hash1 != hash3  # Different content

        # Should be valid SHA-256 hash (64 characters, hex)
        assert len(hash1) == 64
        assert hash1.isalnum()

    def test_count_words(self):
        """Test word counting function."""
        assert count_words("") == 0
        assert count_words("Hello") == 1
        assert count_words("Hello World") == 2
        assert count_words("Hello, World!") == 2  # Punctuation ignored
        assert count_words("Hello\nWorld") == 2  # Newlines handled
        assert count_words("Hello   World") == 2  # Multiple spaces

    def test_extract_section_content(self):
        """Test section content extraction."""
        content = """# Section 1

This is section 1 content.
It has multiple lines.

## Section 2

This is section 2 content.
It also has multiple lines.

# Section 3

This is section 3.
"""

        # Extract section 1
        section1_content = extract_section_content(content, "Section 1")
        assert "This is section 1 content" in section1_content
        assert "It has multiple lines" in section1_content
        assert "Section 2" not in section1_content

        # Extract section 2
        section2_content = extract_section_content(content, "Section 2")
        assert "This is section 2 content" in section2_content
        assert "Section 3" not in section2_content


class TestDocumentAnalysis:
    """Test document analysis functions."""

    @patch("scripts.manage_document_sections.psycopg")
    def test_get_document_hierarchy(self, mock_psycopg):
        """Test getting document hierarchy from database."""
        # Mock database connection and cursor
        mock_cursor = Mock()
        mock_conn = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_psycopg.connect.return_value.__enter__.return_value = mock_conn

        # Mock database response
        mock_cursor.fetchall.return_value = [
            ("Section 1", 1, None, 10, "2024-01-01"),
            ("Section 2", 2, "Section 1", 15, "2024-01-01"),
        ]

        hierarchy = get_document_hierarchy("test.md")

        assert len(hierarchy) == 2
        assert hierarchy[0]["name"] == "Section 1"
        assert hierarchy[0]["level"] == 1
        assert hierarchy[0]["parent"] is None
        assert hierarchy[1]["parent"] == "Section 1"

    def test_find_missing_sections(self):
        """Test finding missing required sections."""
        existing_sections = [
            {"name": "Introduction"},
            {"name": "Setup"},
            {"name": "Usage"},
        ]

        required = ["Introduction", "Setup", "Usage", "Configuration", "Troubleshooting"]

        missing = find_missing_sections("test.md", required)

        assert "Configuration" in missing
        assert "Troubleshooting" in missing
        assert "Introduction" not in missing

    def test_get_section_stats(self):
        """Test calculating section statistics."""
        sections = [
            {"name": "Section 1", "level": 1, "word_count": 10},
            {"name": "Section 2", "level": 2, "word_count": 20},
            {"name": "Section 3", "level": 2, "word_count": 0},  # Empty
            {"name": "Section 4", "level": 3, "word_count": 15},
        ]

        stats = get_section_stats(sections)

        assert stats["total_sections"] == 4
        assert stats["total_words"] == 45
        assert stats["empty_sections"] == 1
        assert stats["sections_by_level"][1] == 1
        assert stats["sections_by_level"][2] == 2
        assert stats["sections_by_level"][3] == 1

    def test_suggest_missing_sections(self):
        """Test suggesting missing sections for different document types."""
        # Test master reference suggestions
        suggestions = suggest_missing_sections("GEMATRIA_MASTER_REFERENCE.md")
        assert "Error Handling & Recovery" in suggestions
        assert "Performance Optimization" in suggestions
        assert len(suggestions) == 10

        # Test agents suggestions
        suggestions = suggest_missing_sections("AGENTS.md")
        assert "Error Recovery Procedures" in suggestions

        # Test unknown document type
        suggestions = suggest_missing_sections("unknown.md")
        assert suggestions == []
