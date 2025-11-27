#!/usr/bin/env python3
"""
Phase 13: Unify Vector Dimensions for BibleScholar

Stabilizes the Vector Search integration by ensuring all code uses the canonical
1024-dimensional embedding format (BGE-M3 compatible) from bible.verse_embeddings.

The bible.verses table has a deprecated vector(768) column that should not be used.
All vector operations must use bible.verse_embeddings with vector(1024).

This script:
1. Validates that vector_adapter.py uses 1024-dim from verse_embeddings
2. Adds dimension validation to prevent dimension mismatches
3. Updates documentation to clarify canonical dimension
4. Ensures BGE-M3 compatibility (1024-dim is BGE-M3's native dimension)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Canonical dimension for Bible Lane (BGE-M3 compatible)
CANONICAL_DIMENSION = 1024
DEPRECATED_DIMENSION = 768


def validate_adapter_dimension() -> tuple[bool, str]:
    """Validate that vector_adapter uses canonical 1024-dim."""
    adapter_file = Path(__file__).parent.parent.parent / "agentpm" / "biblescholar" / "vector_adapter.py"

    if not adapter_file.exists():
        return False, f"Adapter file not found: {adapter_file}"

    content = adapter_file.read_text()

    # Check that it uses verse_embeddings (1024-dim)
    if "verse_embeddings" not in content:
        return False, "Adapter does not use verse_embeddings table"

    # Check that it mentions 1024-dim
    if "1024" not in content and "vector(1024)" not in content:
        return False, "Adapter does not specify 1024-dim"

    # Check that it doesn't use deprecated verses.embedding in actual code
    # Allow references in comments/docstrings about deprecation
    lines = content.split("\n")
    in_docstring = False
    for i, line in enumerate(lines):
        # Track docstring state
        if '"""' in line:
            in_docstring = not in_docstring
        # Check for verses.embedding in actual code (not comments/docstrings)
        if "verses.embedding" in line:
            stripped = line.strip()
            # Allow in comments
            if stripped.startswith("#"):
                continue
            # Allow in docstrings
            if in_docstring or '"""' in line or "'''" in line:
                continue
            # Allow if it's part of a deprecation message
            if "deprecated" in line.lower() or "previously" in line.lower():
                continue
            # This is actual code usage - fail
            return False, f"Adapter references verses.embedding in code (line {i + 1}): {stripped[:60]}"

    return True, "Adapter uses canonical 1024-dim from verse_embeddings"


def add_dimension_validation() -> tuple[bool, str]:
    """Add dimension validation to find_similar_by_embedding method."""
    adapter_file = Path(__file__).parent.parent.parent / "agentpm" / "biblescholar" / "vector_adapter.py"
    content = adapter_file.read_text()

    # Check if validation already exists
    if "len(query_embedding)" in content and "1024" in content:
        # Check if it's in the right place (find_similar_by_embedding)
        if "def find_similar_by_embedding" in content:
            method_start = content.find("def find_similar_by_embedding")
            method_end = content.find("\n    def ", method_start + 1)
            if method_end == -1:
                method_end = len(content)
            method_content = content[method_start:method_end]

            if "len(query_embedding)" in method_content and "1024" in method_content:
                return True, "Dimension validation already present"

    # Add validation after the docstring
    if "def find_similar_by_embedding" not in content:
        return False, "find_similar_by_embedding method not found"

    # Find the method and add validation
    method_start = content.find("def find_similar_by_embedding")
    if method_start == -1:
        return False, "Could not find find_similar_by_embedding method"

    # Find the start of the method body (after docstring)
    docstring_end = content.find('"""', method_start + 30)
    if docstring_end != -1:
        docstring_end = content.find('"""', docstring_end + 3)
        if docstring_end != -1:
            body_start = content.find("\n        ", docstring_end)
            if body_start != -1:
                # Insert validation after the first line of the method body
                validation = f"""        # Validate embedding dimension (BGE-M3 requires 1024-dim)
        if len(query_embedding) != {CANONICAL_DIMENSION}:
            raise ValueError(
                f"Query embedding must be {CANONICAL_DIMENSION}-dimensional (BGE-M3 compatible), "
                f"got {{len(query_embedding)}}-dimensional"
            )
        
"""
                # Check if validation already exists
                if validation.strip() in content:
                    return True, "Dimension validation already present"

                # Insert validation
                new_content = content[: body_start + 1] + validation + content[body_start + 1 :]
                adapter_file.write_text(new_content)
                return (
                    True,
                    f"Added dimension validation to find_similar_by_embedding (requires {CANONICAL_DIMENSION}-dim)",
                )

    return False, "Could not locate insertion point for validation"


def update_documentation() -> tuple[bool, str]:
    """Update documentation to clarify canonical dimension."""
    adapter_file = Path(__file__).parent.parent.parent / "agentpm" / "biblescholar" / "vector_adapter.py"
    content = adapter_file.read_text()

    # Check if documentation already mentions canonical dimension
    if f"{CANONICAL_DIMENSION}-dimensional" in content and "canonical" in content.lower():
        return True, "Documentation already mentions canonical dimension"

    # Update module docstring if needed
    if '"""BibleScholar Vector similarity adapter' in content:
        # Find module docstring
        docstring_start = content.find('"""')
        docstring_end = content.find('"""', docstring_start + 3)
        if docstring_end != -1:
            docstring = content[docstring_start + 3 : docstring_end]

            # Add canonical dimension note if not present
            if "canonical" not in docstring.lower() or f"{CANONICAL_DIMENSION}" not in docstring:
                updated_docstring = docstring.rstrip()
                if not updated_docstring.endswith("."):
                    updated_docstring += "."
                updated_docstring += f"\n\nCanonical embedding dimension: {CANONICAL_DIMENSION} (BGE-M3 compatible).\nThe deprecated bible.verses.embedding column (vector({DEPRECATED_DIMENSION})) should not be used."

                new_content = content[: docstring_start + 3] + updated_docstring + content[docstring_end:]
                adapter_file.write_text(new_content)
                return True, "Updated module docstring with canonical dimension"

    return True, "Documentation check complete"


def main() -> int:
    """Main execution."""
    print("=" * 70)
    print("Phase 13: Unify Vector Dimensions for BibleScholar")
    print("=" * 70)
    print()
    print(f"Canonical dimension: {CANONICAL_DIMENSION} (BGE-M3 compatible)")
    print(f"Deprecated dimension: {DEPRECATED_DIMENSION} (bible.verses.embedding)")
    print()

    # Step 1: Validate adapter uses correct dimension
    print("Step 1: Validating adapter uses canonical 1024-dim...")
    valid, msg = validate_adapter_dimension()
    if not valid:
        print(f"  ❌ FAILED: {msg}")
        return 1
    print(f"  ✓ {msg}")
    print()

    # Step 2: Add dimension validation
    print("Step 2: Adding dimension validation...")
    success, msg = add_dimension_validation()
    if not success:
        print(f"  ⚠ WARNING: {msg}")
    else:
        print(f"  ✓ {msg}")
    print()

    # Step 3: Update documentation
    print("Step 3: Updating documentation...")
    success, msg = update_documentation()
    if not success:
        print(f"  ⚠ WARNING: {msg}")
    else:
        print(f"  ✓ {msg}")
    print()

    print("=" * 70)
    print("Summary:")
    print(f"  • Canonical dimension: {CANONICAL_DIMENSION} (BGE-M3)")
    print("  • Source table: bible.verse_embeddings")
    print(f"  • Deprecated: bible.verses.embedding (vector({DEPRECATED_DIMENSION}))")
    print("=" * 70)
    print()
    print("✓ Vector dimension unification complete")
    print()
    print("Next steps:")
    print("  1. Run tests: pytest agentpm/biblescholar/tests/test_vector_flow.py -v")
    print("  2. Verify BGE-M3 embeddings are 1024-dimensional")
    print("  3. Ensure all code paths use verse_embeddings, not verses.embedding")

    return 0


if __name__ == "__main__":
    sys.exit(main())
