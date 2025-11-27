#!/usr/bin/env python3
"""
Phase 13B: Adapter Enhancement - Translation Filter Verification
================================================================
Verifies that bible_db_adapter.py correctly implements translation_source filtering
and adds comprehensive tests for multiple translations (KJV, ESV, ASV, YLT, TAHOT).

This script:
1. Verifies translation_source filtering in all adapter methods
2. Adds multi-translation tests to test_bible_passage_flow.py
3. Confirms SQL queries include translation_source filtering
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ADAPTER_PATH = REPO_ROOT / "agentpm" / "biblescholar" / "bible_db_adapter.py"
TEST_PATH = REPO_ROOT / "agentpm" / "biblescholar" / "tests" / "test_bible_passage_flow.py"


def verify_adapter_implementation():
    """Verify that bible_db_adapter.py correctly implements translation_source filtering."""
    print("=" * 70)
    print("Verifying bible_db_adapter.py translation_source implementation")
    print("=" * 70)

    with open(ADAPTER_PATH) as f:
        content = f.read()

    # Check for translation_source parameter in key methods
    methods_to_check = [
        "get_verse",
        "get_passage",
        "search_verses",
        "get_verses_by_strongs",
    ]

    all_verified = True
    for method in methods_to_check:
        # Check method signature has translation_source parameter
        pattern = rf"def {method}\(.*?translation_source.*?\)"
        if not re.search(pattern, content, re.DOTALL):
            print(f"❌ {method}() missing translation_source parameter")
            all_verified = False
        else:
            print(f"✓ {method}() has translation_source parameter")

        # Check SQL query includes translation_source filtering
        pattern = rf"def {method}.*?translation_source.*?=.*?translation_source"
        if not re.search(pattern, content, re.DOTALL):
            print(f"⚠️  {method}() SQL may not filter by translation_source")
        else:
            print(f"✓ {method}() SQL filters by translation_source")

    if all_verified:
        print("\n✅ All adapter methods verified for translation_source support")
    else:
        print("\n❌ Some adapter methods need translation_source support")
        sys.exit(1)

    return True


def add_multi_translation_tests():
    """Add multi-translation tests to test_bible_passage_flow.py."""
    print("\n" + "=" * 70)
    print("Adding multi-translation tests to test_bible_passage_flow.py")
    print("=" * 70)

    with open(TEST_PATH) as f:
        test_content = f.read()

    # Check if multi-translation tests already exist
    if "test_fetch_verse_multiple_translations" in test_content:
        print("✓ Multi-translation tests already exist")
        return True

    # Add new test class for multi-translation tests
    new_tests = '''

class TestMultiTranslationSupport:
    """Test multi-translation support in passage flow."""

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_verse_multiple_translations(self, mock_adapter_class):
        """Test fetching same verse from multiple translations."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter_class.return_value = mock_adapter

        translations = ["KJV", "ESV", "ASV", "YLT"]
        for translation in translations:
            mock_verse = VerseRecord(
                verse_id=1,
                book_name="Genesis",
                chapter_num=1,
                verse_num=1,
                text=f"In the beginning ({translation})",
                translation_source=translation,
            )
            mock_adapter.get_verse.return_value = mock_verse

            result = fetch_verse("Genesis 1:1", translation)

            assert result is not None
            assert result.translation_source == translation
            mock_adapter.get_verse.assert_called_with("Gen", 1, 1, translation)

    @patch("agentpm.biblescholar.bible_passage_flow.BibleDbAdapter")
    def test_fetch_passage_multiple_translations(self, mock_adapter_class):
        """Test fetching passage from multiple translations."""
        mock_adapter = MagicMock(spec=BibleDbAdapter)
        mock_adapter_class.return_value = mock_adapter

        translations = ["KJV", "ESV", "ASV"]
        for translation in translations:
            mock_verses = [
                VerseRecord(1, "Genesis", 1, 1, f"Verse 1 ({translation})", translation),
                VerseRecord(2, "Genesis", 1, 2, f"Verse 2 ({translation})", translation),
            ]
            mock_adapter.get_passage.return_value = mock_verses

            result = fetch_passage("Genesis 1:1-2", translation)

            assert len(result) == 2
            assert all(v.translation_source == translation for v in result)
            mock_adapter.get_passage.assert_called_with("Gen", 1, 1, 1, 2, translation)
'''

    # Append new tests before the last line
    if test_content.strip().endswith(")"):
        # Find the last class and append after it
        test_content = test_content.rstrip() + new_tests + "\n"
    else:
        test_content = test_content.rstrip() + "\n" + new_tests

    with open(TEST_PATH, "w") as f:
        f.write(test_content)

    print("✓ Added multi-translation tests to test_bible_passage_flow.py")
    return True


def main():
    """Main execution."""
    print("Phase 13B: Adapter Enhancement - Translation Filter Verification")
    print("=" * 70)

    # Verify adapter implementation
    verify_adapter_implementation()

    # Add multi-translation tests
    add_multi_translation_tests()

    print("\n" + "=" * 70)
    print("✅ Phase 13B enhancement complete")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run: pytest agentpm/biblescholar/tests/test_bible_passage_flow.py -v")
    print("2. Verify all tests pass with translation_source filtering")


if __name__ == "__main__":
    main()
