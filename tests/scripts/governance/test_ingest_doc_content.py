"""Tests for scripts/governance/ingest_doc_content.py"""

from __future__ import annotations

from scripts.governance import ingest_doc_content as mod


def test_chunk_markdown_headings() -> None:
    """Test that headings are correctly identified as fragments."""
    content = """# Title
## Section
### Subsection
"""
    fragments = mod.chunk_markdown(content)
    assert len(fragments) == 3
    assert all(f.fragment_type == "heading" for f in fragments)
    assert fragments[0].content == "# Title"
    assert fragments[1].content == "## Section"
    assert fragments[2].content == "### Subsection"


def test_chunk_markdown_code_blocks() -> None:
    """Test that code blocks are correctly identified."""
    content = """```python
def hello():
    print("world")
```
"""
    fragments = mod.chunk_markdown(content)
    assert len(fragments) == 1
    assert fragments[0].fragment_type == "code"
    assert "```python" in fragments[0].content
    assert "def hello()" in fragments[0].content


def test_chunk_markdown_paragraphs() -> None:
    """Test that paragraphs are correctly identified."""
    content = """This is a paragraph.

This is another paragraph.
"""
    fragments = mod.chunk_markdown(content)
    assert len(fragments) == 2
    assert all(f.fragment_type == "paragraph" for f in fragments)
    assert "This is a paragraph" in fragments[0].content
    assert "This is another paragraph" in fragments[1].content


def test_chunk_markdown_mixed() -> None:
    """Test mixed content (headings, paragraphs, code)."""
    content = """# Title

This is a paragraph.

```python
code here
```

## Section 2

More text.
"""
    fragments = mod.chunk_markdown(content)
    assert len(fragments) >= 4
    assert fragments[0].fragment_type == "heading"
    assert fragments[1].fragment_type == "paragraph"
    assert any(f.fragment_type == "code" for f in fragments)
    # Verify fragment_index is sequential
    indices = [f.fragment_index for f in fragments]
    assert indices == list(range(len(fragments)))


def test_normalize_content_strips_bom() -> None:
    """Test that BOM is stripped."""
    content = "\ufeff# Title"
    normalized = mod.normalize_content(content)
    assert not normalized.startswith("\ufeff")
    assert normalized.startswith("#")


def test_normalize_content_normalizes_newlines() -> None:
    """Test that newlines are normalized to \\n."""
    content = "Line 1\r\nLine 2\rLine 3\nLine 4"
    normalized = mod.normalize_content(content)
    assert "\r" not in normalized
    assert "\r\n" not in normalized
    assert "\n" in normalized
