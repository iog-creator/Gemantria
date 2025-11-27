#!/usr/bin/env python3
"""
OPS Script: Phase 13C - Parallel Text Viewer Component
======================================================
Implements parallel translation viewer that displays multiple translations side-by-side.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIBLE_PAGE = REPO_ROOT / "webui/graph/src/pages/BiblePage.tsx"

# Available translations
TRANSLATIONS = ["KJV", "ESV", "ASV", "YLT", "TAHOT"]


def update_bible_page():
    """Update BiblePage to support parallel translation viewing."""
    print(f"Updating {BIBLE_PAGE}...")
    content = BIBLE_PAGE.read_text()

    # Replace single translation state with multi-select
    old_state = "  const [translation, setTranslation] = useState('KJV');"
    new_state = """  const [selectedTranslations, setSelectedTranslations] = useState<string[]>(['KJV']);"""

    if old_state in content:
        content = content.replace(old_state, new_state)
        print("  ✓ Updated state to support multiple translations")

    # Update data state to hold multiple passages
    old_data_state = "  const [data, setData] = useState<PassageResponse | null>(null);"
    new_data_state = "  const [data, setData] = useState<Record<string, PassageResponse>>({});"

    if old_data_state in content:
        content = content.replace(old_data_state, new_data_state)
        print("  ✓ Updated data state to hold multiple passages")

    # Replace single select with multi-select checkboxes
    old_translation_selector = """            <div>
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
                <option value="YLT">Young&apos;s Literal Translation (YLT)</option>
                <option value="TAHOT">The Ancient Hebrew of the Torah (TAHOT)</option>
              </select>
            </div>"""

    new_translation_selector = """            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Translations (select multiple for parallel view)
              </label>
              <div className="grid grid-cols-2 gap-3">
                {['KJV', 'ESV', 'ASV', 'YLT', 'TAHOT'].map((trans) => (
                  <div key={trans} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`trans-${trans}`}
                      checked={selectedTranslations.includes(trans)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedTranslations([...selectedTranslations, trans]);
                        } else {
                          setSelectedTranslations(selectedTranslations.filter(t => t !== trans));
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor={`trans-${trans}`} className="ml-2 block text-sm text-gray-700">
                      {trans === 'KJV' ? 'King James Version' :
                       trans === 'ESV' ? 'English Standard Version' :
                       trans === 'ASV' ? 'American Standard Version' :
                       trans === 'YLT' ? 'Young\'s Literal Translation' :
                       'The Ancient Hebrew of the Torah'}
                    </label>
                  </div>
                ))}
              </div>
            </div>"""

    if old_translation_selector in content:
        content = content.replace(old_translation_selector, new_translation_selector)
        print("  ✓ Replaced single select with multi-select checkboxes")

    # Update handleSubmit to fetch multiple translations in parallel
    old_handle_submit = """  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reference.trim()) {
      setError('Please enter a Bible reference');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const url = `/api/biblescholar/passage?reference=${encodeURIComponent(reference)}&translation=${encodeURIComponent(translation)}&use_lm=${useLm}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result: PassageResponse = await response.json();

      if (result.errors && result.errors.length > 0) {
        setError(result.errors.join('; '));
        return;
      }

      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch passage');
    } finally {
      setLoading(false);
    }
  };"""

    new_handle_submit = """  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reference.trim()) {
      setError('Please enter a Bible reference');
      return;
    }

    if (selectedTranslations.length === 0) {
      setError('Please select at least one translation');
      return;
    }

    setLoading(true);
    setError(null);
    setData({});

    try {
      // Fetch all selected translations in parallel
      const promises = selectedTranslations.map(async (trans) => {
        const url = `/api/biblescholar/passage?reference=${encodeURIComponent(reference)}&translation=${encodeURIComponent(trans)}&use_lm=${useLm}`;
        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText} for ${trans}`);
        }

        const result: PassageResponse = await response.json();
        return { translation: trans, data: result };
      });

      const results = await Promise.all(promises);
      const dataMap: Record<string, PassageResponse> = {};

      // Check for errors in any result
      const allErrors: string[] = [];
      for (const { translation, data: result } of results) {
        if (result.errors && result.errors.length > 0) {
          allErrors.push(`${translation}: ${result.errors.join('; ')}`);
        } else {
          dataMap[translation] = result;
        }
      }

      if (allErrors.length > 0) {
        setError(allErrors.join(' | '));
      }

      setData(dataMap);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch passages');
    } finally {
      setLoading(false);
    }
  };"""

    if old_handle_submit in content:
        content = content.replace(old_handle_submit, new_handle_submit)
        print("  ✓ Updated handleSubmit to fetch multiple translations in parallel")

    # Update results display to show parallel columns
    old_results_display = """        {data && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-4">{data.reference}</h2>
              <div className="space-y-3 text-gray-800">
                {data.verses.map((verse, idx) => (
                  <div key={idx} className="mb-4 pb-4 border-b border-gray-200 last:border-0">
                    <div className="mb-2">
                      <span className="font-semibold text-blue-600">
                        {verse.verse}.
                      </span>{' '}
                      {verse.text}
                    </div>
                    {verse.gematria && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-md">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Gematria Values</h4>
                        <div className="space-y-2">
                          {Object.entries(verse.gematria).map(([system, result]) => (
                            <div key={system} className="text-sm">
                              <span className="font-medium text-gray-700">{system}:</span>{' '}
                              <span className="text-blue-600 font-semibold">{result.value}</span>
                              {result.normalized && (
                                <span className="text-gray-500 ml-2">
                                  ({result.normalized})
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {data.commentary && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold mb-4">Commentary</h3>
                <div className="text-gray-700 whitespace-pre-wrap mb-2">
                  {data.commentary.text}
                </div>
                <p className="text-sm text-gray-700">
                  Source: {data.commentary.source === 'lm_theology'
                    ? 'AI Commentary (Theology Model)'
                    : 'Fallback (LM Unavailable)'}
                </p>
              </div>
            )}
          </div>
        )}"""

    new_results_display = """        {Object.keys(data).length > 0 && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-4">
                {Object.values(data)[0]?.reference || reference}
              </h2>
              
              {/* Parallel Translation View */}
              <div className={`grid gap-4 ${Object.keys(data).length === 1 ? 'grid-cols-1' : Object.keys(data).length === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
                {Object.entries(data).map(([trans, passageData]) => (
                  <div key={trans} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <h3 className="text-lg font-semibold mb-3 text-blue-600 border-b border-gray-300 pb-2">
                      {trans === 'KJV' ? 'King James Version' :
                       trans === 'ESV' ? 'English Standard Version' :
                       trans === 'ASV' ? 'American Standard Version' :
                       trans === 'YLT' ? 'Young\'s Literal Translation' :
                       'The Ancient Hebrew of the Torah'}
                    </h3>
                    <div className="space-y-3 text-gray-800 text-sm">
                      {passageData.verses.map((verse, idx) => (
                        <div key={idx} className="mb-3 pb-2 border-b border-gray-200 last:border-0">
                          <div className="mb-1">
                            <span className="font-semibold text-blue-600 text-xs">
                              {verse.verse}.
                            </span>{' '}
                            <span className="text-gray-800">{verse.text}</span>
                          </div>
                          {verse.gematria && (
                            <div className="mt-2 p-2 bg-white rounded text-xs">
                              <h4 className="text-xs font-semibold text-gray-700 mb-1">Gematria</h4>
                              <div className="space-y-1">
                                {Object.entries(verse.gematria).map(([system, result]) => (
                                  <div key={system} className="text-xs">
                                    <span className="font-medium text-gray-600">{system}:</span>{' '}
                                    <span className="text-blue-600 font-semibold">{result.value}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Commentary (from first translation) */}
            {Object.values(data)[0]?.commentary && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold mb-4">Commentary</h3>
                <div className="text-gray-700 whitespace-pre-wrap mb-2">
                  {Object.values(data)[0]?.commentary?.text}
                </div>
                <p className="text-sm text-gray-700">
                  Source: {Object.values(data)[0]?.commentary?.source === 'lm_theology'
                    ? 'AI Commentary (Theology Model)'
                    : 'Fallback (LM Unavailable)'}
                </p>
              </div>
            )}
          </div>
        )}"""

    if old_results_display in content:
        content = content.replace(old_results_display, new_results_display)
        print("  ✓ Updated results display to show parallel columns")

    BIBLE_PAGE.write_text(content)
    print(f"✅ Updated {BIBLE_PAGE}")


def main() -> int:
    """Main execution."""
    print("=" * 70)
    print("Phase 13C: Parallel Text Viewer Component")
    print("=" * 70)
    print()

    try:
        update_bible_page()

        print()
        print("=" * 70)
        print("✅ Phase 13C: Parallel viewer UI integration complete")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run browser verification (make atlas.webproof UI_PAGE=/bible)")
        print("  2. Run AWCG to generate completion envelope")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
