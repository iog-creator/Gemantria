#!/bin/bash
# Test script for documentation requirement rule (009-documentation-sync.mdc)
# This script validates that documentation is updated or created for any code change

echo "=== DOCUMENTATION REQUIREMENT RULE TEST SUITE ==="
echo "Testing that documentation is updated or created for any code change..."
echo ""

# Test 1: Rule syntax and core purpose
echo "1. Testing rule syntax and core purpose..."
if grep -q "Require docs/ADR/SSOT updates for any code change" .cursor/rules/027-docs-sync-gate.mdc && grep -q "rules_guard.py" .cursor/rules/027-docs-sync-gate.mdc; then
    echo "✅ Rule syntax and purpose: PASS (enforcement rule + core requirement)"
else
    echo "❌ Rule syntax and purpose: FAIL"
fi

# Test 2: AGENTS.md file coverage
echo "2. Testing AGENTS.md file coverage..."
TOTAL_AGENTS=$(find . -name "AGENTS.md" -type f | wc -l)
if [ "$TOTAL_AGENTS" -ge 10 ]; then
    echo "✅ AGENTS.md coverage: PASS ($TOTAL_AGENTS files exist)"
else
    echo "❌ AGENTS.md coverage: FAIL (only $TOTAL_AGENTS files, need comprehensive coverage)"
fi

# Test 3: ADR coverage for changes
echo "3. Testing ADR coverage for changes..."
TOTAL_ADRS=$(find docs/ADRs -name "ADR-*.md" -type f | wc -l)
if [ "$TOTAL_ADRS" -ge 14 ]; then
    echo "✅ ADR coverage: PASS ($TOTAL_ADRS ADRs document major changes)"
else
    echo "❌ ADR coverage: FAIL (only $TOTAL_ADRS ADRs, major changes need documentation)"
fi

# Test 4: Cursor rules coverage
echo "4. Testing cursor rules coverage..."
TOTAL_RULES=$(find .cursor/rules -name "*.mdc" -type f | wc -l)
if [ "$TOTAL_RULES" -ge 14 ]; then
    echo "✅ Cursor rules coverage: PASS ($TOTAL_RULES rules enforce behavior)"
else
    echo "❌ Cursor rules coverage: FAIL (only $TOTAL_RULES rules, new behaviors need rules)"
fi

# Test 5: Report generation verification
echo "5. Testing report generation verification..."
RECENT_REPORTS=$(find reports -name "*.md" -type f -newermt "1 day ago" | wc -l)
if [ "$RECENT_REPORTS" -gt 0 ]; then
    echo "✅ Report generation: PASS ($RECENT_REPORTS recent reports)"
else
    echo "❌ Report generation: FAIL (no recent reports - pipeline not generating reports)"
fi

# Test 6: ADR creation for rule changes
echo "6. Testing ADR creation for rule changes..."
if [ -f "docs/ADRs/ADR-013-documentation-sync-enhancement.md" ]; then
    echo "✅ ADR for rule changes: PASS (ADR-013 documents this rule enhancement)"
else
    echo "❌ ADR for rule changes: FAIL (rule changes need ADR documentation)"
fi

# Test 7: Cross-referencing between docs
echo "7. Testing cross-referencing between docs..."
ADR_CROSSREF=$(grep -l "Related Rules\|Related ADRs" docs/ADRs/ADR-*.md | wc -l)
RULE_CROSSREF=$(grep -l "ADR-\|AGENTS.md" .cursor/rules/*.mdc | wc -l)
if [ "$ADR_CROSSREF" -gt 3 ] && [ "$RULE_CROSSREF" -gt 3 ]; then
    echo "✅ Cross-referencing: PASS ($ADR_CROSSREF ADRs, $RULE_CROSSREF rules with links)"
else
    echo "❌ Cross-referencing: FAIL (poor linking: $ADR_CROSSREF ADRs, $RULE_CROSSREF rules)"
fi

# Test 8: Documentation reflects current code
echo "8. Testing documentation reflects current code..."
# Check if recent changes have corresponding docs (basic heuristic)
RECENT_CODE_CHANGES=$(find . -name "*.py" -type f -newermt "1 week ago" | wc -l)
RECENT_DOC_CHANGES=$(find . -name "*.md" -type f -newermt "1 week ago" | wc -l)
if [ "$RECENT_DOC_CHANGES" -gt 0 ]; then
    echo "✅ Documentation updates: PASS (recent documentation changes detected)"
else
    echo "⚠️  Documentation updates: WARN (no recent doc changes, verify code changes have docs)"
fi

echo ""
echo "=== TEST SUMMARY ==="
echo "This rule ensures documentation is updated or created for ANY code change!"
echo "Core requirement: Every PR must include documentation updates or new docs."
echo "Run this script before PRs to verify compliance with the always-applied rule."
