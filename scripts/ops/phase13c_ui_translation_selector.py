#!/usr/bin/env python3
"""
OPS Script: Phase 13C - Add Translation Selector to UI
======================================================
Adds translation selector component to BiblePage and updates API calls.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIBLE_PAGE = REPO_ROOT / "webui/graph/src/pages/BiblePage.tsx"
API_ROUTER = REPO_ROOT / "src/services/routers/biblescholar.py"
PASSAGE_MODULE = REPO_ROOT / "agentpm/biblescholar/passage.py"

# Available translations
TRANSLATIONS = ["KJV", "ESV", "ASV", "YLT", "TAHOT"]


def update_bible_page():
    """Add translation selector to BiblePage component."""
    print(f"Updating {BIBLE_PAGE}...")
    content = BIBLE_PAGE.read_text()

    # Add translation state
    if "const [translation, setTranslation]" not in content:
        # Find the state declarations
        old_state = "  const [useLm, setUseLm] = useState(true);"
        new_state = """  const [useLm, setUseLm] = useState(true);
  const [translation, setTranslation] = useState('KJV');"""
        if old_state in content:
            content = content.replace(old_state, new_state)
            print("  ✓ Added translation state")

    # Add translation selector UI
    translation_selector = """            <div>
              <label htmlFor="translation" className="block text-sm font-medium text-gray-700 mb-2">
                Translation
              </label>
              <select
                id="translation"
                value={translation}
                onChange={(e) => setTranslation(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="KJV">King James Version (KJV)</option>
                <option value="ESV">English Standard Version (ESV)</option>
                <option value="ASV">American Standard Version (ASV)</option>
                <option value="YLT">Young's Literal Translation (YLT)</option>
                <option value="TAHOT">The Ancient Hebrew of the Torah (TAHOT)</option>
              </select>
            </div>"""

    # Insert after reference input, before useLm checkbox
    old_checkbox = """            <div className="flex items-center">
              <input
                type="checkbox"
                id="use-lm"
                checked={useLm}
                onChange={(e) => setUseLm(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="use-lm" className="ml-2 block text-sm text-gray-700">
                Use AI commentary
              </label>
            </div>"""

    new_form_section = translation_selector + "\n" + old_checkbox

    if old_checkbox in content and translation_selector not in content:
        content = content.replace(old_checkbox, new_form_section)
        print("  ✓ Added translation selector UI")

    # Update API call to include translation parameter
    old_url = "const url = `/api/biblescholar/passage?reference=${encodeURIComponent(reference)}&use_lm=${useLm}`;"
    new_url = "const url = `/api/biblescholar/passage?reference=${encodeURIComponent(reference)}&translation=${encodeURIComponent(translation)}&use_lm=${useLm}`;"

    if old_url in content:
        content = content.replace(old_url, new_url)
        print("  ✓ Updated API call to include translation parameter")
    elif "const url = `/api/biblescholar/passage?" in content:
        # Try to find and replace more flexibly
        import re

        pattern = r"const url = `/api/biblescholar/passage\?reference=\$\{encodeURIComponent\(reference\)\}&use_lm=\$\{useLm\}`;"
        replacement = "const url = `/api/biblescholar/passage?reference=${encodeURIComponent(reference)}&translation=${encodeURIComponent(translation)}&use_lm=${useLm}`;"
        content = re.sub(pattern, replacement, content)
        print("  ✓ Updated API call to include translation parameter (regex)")

    BIBLE_PAGE.write_text(content)
    print(f"✅ Updated {BIBLE_PAGE}")


def update_api_endpoint():
    """Update API endpoint to accept translation parameter."""
    print(f"\nUpdating {API_ROUTER}...")
    content = API_ROUTER.read_text()

    # Update endpoint signature
    old_sig = """@biblescholar_router.get("/passage", response_model=PassageResponse)
async def api_get_passage_with_gematria(
    reference: str = Query(..., description="Bible reference (e.g., 'John 3:16-18')"),
    use_lm: bool = Query(True, description="Use AI commentary (default: True)"),
):"""

    new_sig = """@biblescholar_router.get("/passage", response_model=PassageResponse)
async def api_get_passage_with_gematria(
    reference: str = Query(..., description="Bible reference (e.g., 'John 3:16-18')"),
    translation: str = Query(..., description="Translation identifier (required, e.g., KJV, ESV, ASV, YLT)"),
    use_lm: bool = Query(True, description="Use AI commentary (default: True)"),
):"""

    if old_sig in content:
        content = content.replace(old_sig, new_sig)
        print("  ✓ Updated API endpoint signature")

    # Update function call to pass translation
    old_call = "        passage_data = get_passage_and_commentary(reference, use_lm=use_lm)"
    new_call = (
        "        passage_data = get_passage_and_commentary(reference, translation_source=translation, use_lm=use_lm)"
    )

    if old_call in content:
        content = content.replace(old_call, new_call)
        print("  ✓ Updated function call to pass translation")

    API_ROUTER.write_text(content)
    print(f"✅ Updated {API_ROUTER}")


def update_passage_module():
    """Update get_passage_and_commentary to accept translation_source."""
    print(f"\nUpdating {PASSAGE_MODULE}...")
    content = PASSAGE_MODULE.read_text()

    # Update function signature
    old_sig = 'def get_passage_and_commentary(passage_ref: str, use_lm: bool = True) -> Dict:\n    """\n    Get both passage text (from DB) and commentary (from LM).\n\n    Args:\n        passage_ref: Bible reference (e.g., "Genesis 1:1").\n        use_lm: If True, attempt to use theology LM; if False, raise ValueError.\n\n    Returns:\n        Dict with "reference", "text" (from DB), and "commentary" (from LM).\n    """'

    new_sig = 'def get_passage_and_commentary(passage_ref: str, translation_source: str = "KJV", use_lm: bool = True) -> Dict:\n    """\n    Get both passage text (from DB) and commentary (from LM).\n\n    Args:\n        passage_ref: Bible reference (e.g., "Genesis 1:1").\n        translation_source: Translation identifier (required, e.g., "KJV", "ESV", "ASV", "YLT").\n        use_lm: If True, attempt to use theology LM; if False, raise ValueError.\n\n    Returns:\n        Dict with "reference", "text" (from DB), and "commentary" (from LM).\n    """'

    if old_sig in content:
        content = content.replace(old_sig, new_sig)
        print("  ✓ Updated function signature")

    # Update to use fetch_passage with translation
    # First, check if we need to import fetch_passage
    if "from agentpm.biblescholar.bible_passage_flow import fetch_passage" not in content:
        # Add import after existing imports
        old_imports = "from agentpm.adapters.theology import chat as theology_chat"
        new_imports = """from agentpm.adapters.theology import chat as theology_chat
from agentpm.biblescholar.bible_passage_flow import fetch_passage"""
        if old_imports in content:
            content = content.replace(old_imports, new_imports)
            print("  ✓ Added fetch_passage import")

    # Update the passage fetching logic
    old_fetch = """    # 1. Get Passage Text (DB)
    # Note: Using insights_flow.db directly for now as we don't have a separate passage_flow imported yet.
    # In a full implementation, we'd use BiblePassageFlow.
    verse_id = passage_ref if passage_ref.isdigit() else "1"  # Placeholder resolution
    verse = insights_flow.db.get_verse_by_id(int(verse_id))

    passage_text = verse.text if verse else "Text not found"
"""

    new_fetch = """    # 1. Get Passage Text (DB) using fetch_passage with translation
    verses = fetch_passage(passage_ref, translation_source=translation_source)
    passage_text = "\\n".join([f"{v.verse_num}. {v.text}" for v in verses]) if verses else "Text not found"
"""

    if old_fetch in content:
        content = content.replace(old_fetch, new_fetch)
        print("  ✓ Updated passage fetching to use fetch_passage with translation")

    PASSAGE_MODULE.write_text(content)
    print(f"✅ Updated {PASSAGE_MODULE}")


def main() -> int:
    """Main execution."""
    print("=" * 70)
    print("Phase 13C: Add Translation Selector to UI")
    print("=" * 70)
    print()

    try:
        update_bible_page()
        update_api_endpoint()
        update_passage_module()

        print()
        print("=" * 70)
        print("✅ Phase 13C: Translation selector UI integration complete")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run browser verification (make atlas.webproof)")
        print("  2. Run AWCG to generate completion envelope")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
