#!/usr/bin/env bash
set -euo pipefail

# --- Rule-062 ENV VALIDATION (MANDATORY — do not alter) ---
python_path="$(command -v python3 || true)"
expected_path="/home/mccoy/Projects/Gemantria.v2/.venv/bin/python3"

if [ "$python_path" != "$expected_path" ]; then
  cat <<'EOF'
🚨 ENVIRONMENT FAILURE (Rule-062) 🚨
Expected venv Python: /home/mccoy/Projects/Gemantria.v2/.venv/bin/python3
Current python: '"$python_path"'
ACTION REQUIRED: source /home/mccoy/Projects/Gemantria.v2/.venv/bin/activate && re-run.
EOF
  exit 62
fi

repo_root="$(git rev-parse --show-toplevel)"; cd "$repo_root"
mkdir -p evidence

# --- Snapshot BEFORE ---
echo "=== HEAD.before (short) ===" && git rev-parse --short HEAD | tee evidence/e38gate.head.before.txt
echo "=== BRANCH.before ==="      && git rev-parse --abbrev-ref HEAD | tee evidence/e38gate.branch.before.txt
echo "=== STATUS.before ==="      && git status -sb | tee evidence/e38gate.status.before.txt

# --- Re-gate and merge PR #441 (Rule-051 posture: only REQUIRED checks block) ---
gh pr view 441 --json number,title,state,url,headRefName,baseRefName,mergeStateStatus,author \
  | tee evidence/pr_441.view.json >/dev/null || true

# Robust required-checks handling (gh returns nothing if none are configured)
req_json="$(gh pr checks 441 --required --json name,state 2>/dev/null || true)"
[ -z "${req_json}" ] && req_json="[]"
printf '%s\n' "$req_json" | tee evidence/pr_441.required.json >/dev/null
gate="$(printf '%s' "$req_json" | jq -r 'if length==0 then "NO_REQUIRED_CHECKS" else (all(.state=="SUCCESS")|tostring) end' 2>/dev/null || echo ERR)"
printf '%s\n' "$gate" | tee evidence/pr_441.required_gate.txt

# Merge if eligible per Rule-051
if [ "$gate" = "true" ] || [ "$gate" = "NO_REQUIRED_CHECKS" ]; then
  echo "GATE: OK → merging PR #441 (squash)." | tee evidence/pr_441.merge.out.txt
  gh pr merge 441 --squash | tee -a evidence/pr_441.merge.out.txt
else
  echo "GATE: NOT READY — required checks not green" | tee evidence/pr_441.merge.out.txt
fi

# --- Sync to main & Hermetic Bundle (Ruff + TVs E06–E37 + guards) ---
git fetch --quiet origin
git checkout main
git pull --ff-only

ruff format --check . && ruff check . | tail -n 30 | sed 's/^/RUFF: /' | tee evidence/e38gate.ruff.tail.txt

pytest -q agentpm/tests/extractors/test_extraction_provenance_e06_e10.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E06-10: /' | tee evidence/e38gate.pytest.e06e10.tail.txt || true
pytest -q agentpm/tests/extractors/test_extraction_determinism_e11_e13.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E11-13: /' | tee evidence/e38gate.pytest.e11e13.tail.txt || true
pytest -q agentpm/tests/extractors/test_extraction_graph_propagation_e14_e16.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E14-16: /' | tee evidence/e38gate.pytest.e14e16.tail.txt || true
pytest -q agentpm/tests/extractors/test_graph_rollups_e17_e19.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E17-19: /' | tee evidence/e38gate.pytest.e17e19.tail.txt || true
pytest -q agentpm/tests/exports/test_graph_export_e20_e22.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E20-22: /' | tee evidence/e38gate.pytest.e20e22.tail.txt || true
pytest -q agentpm/tests/atlas/test_atlas_smoke_e23_e25.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E23-25: /' | tee evidence/e38gate.pytest.e23e25.tail.txt || true
pytest -q agentpm/tests/atlas/test_atlas_links_e26_e28.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E26-28: /' | tee evidence/e38gate.pytest.e26e28.tail.txt || true
pytest -q agentpm/tests/atlas/test_atlas_auditjump_e29_e31.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E29-31: /' | tee evidence/e38gate.pytest.e29e31.tail.txt || true
pytest -q agentpm/tests/atlas/test_atlas_download_backlinks_e32_e34.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E32-34: /' | tee evidence/e38gate.pytest.e32e34.tail.txt || true
pytest -q agentpm/tests/atlas/test_atlas_rawproof_e35_e37.py 2>&1 \
  | tail -n 25 | sed 's/^/PYTEST E35-37: /' | tee evidence/e38gate.pytest.e35e37.tail.txt || true

make guard.extractors || true
tail -n 12 evidence/guard_extractors_provenance.txt 2>/dev/null | sed 's/^/GUARD P: /' | tee evidence/e38gate.guard.provenance.tail.txt || true
tail -n 12 evidence/guard_extractors_determinism.txt 2>/dev/null | sed 's/^/GUARD D: /' | tee evidence/e38gate.guard.determinism.tail.txt || true
tail -n 12 evidence/guard_extractors_graph.txt 2>/dev/null | sed 's/^/GUARD G: /' | tee evidence/e38gate.guard.graph.tail.txt || true
tail -n 12 evidence/guard_extractors_rollups.txt 2>/dev/null | sed 's/^/GUARD R: /' | tee evidence/e38gate.guard.rollups.tail.txt || true

make guard.exports || true
tail -n 20 evidence/guard_exports.txt 2>/dev/null | sed 's/^/GUARD EXPORTS: /' | tee evidence/e38gate.guard.exports.tail.txt || true

make guard.atlas || true
tail -n 20 evidence/guard_atlas_smoke.txt 2>/dev/null | sed 's/^/GUARD ATLAS (smoke): /' | tee evidence/e38gate.guard.atlas_smoke.tail.txt || true
tail -n 20 evidence/guard_atlas_links.txt 2>/dev/null | sed 's/^/GUARD ATLAS (links): /' | tee evidence/e38gate.guard.atlas_links.tail.txt || true
tail -n 20 evidence/guard_atlas_download.txt 2>/dev/null | sed 's/^/GUARD ATLAS (download): /' | tee evidence/e38gate.guard.atlas_download.tail.txt || true
tail -n 20 evidence/guard_atlas_auditjump.txt 2>/dev/null | sed 's/^/GUARD ATLAS (auditjump): /' | tee evidence/e38gate.guard.atlas_auditjump.tail.txt || true
tail -n 20 evidence/guard_atlas_rawproof.txt 2>/dev/null | sed 's/^/GUARD ATLAS (rawproof): /' | tee evidence/e38gate.guard.atlas_rawproof.tail.txt || true

# --- Stage TVs E38–E40 (xfail) ---
git checkout -B "tvs/072-e38plus.accessibility-sitemap.staged.$(date +%Y%m%d-%H%M)"

mkdir -p agentpm/tests/atlas

cat > agentpm/tests/atlas/test_atlas_accessibility_e38_e40.py <<'PYTEST_E3840'
import os, json, pytest, re

xfail_reason = "Staged TVs for E38–E40 (accessibility + sitemap.html + counts banner)"
pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)

def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_e38_breadcrumb_has_aria_label_on_back_to_atlas():
    p = "share/atlas/nodes/0.html"
    assert os.path.exists(p), "node page missing (staged)"
    html = _read(p)
    assert re.search(r'<a[^>]+aria-label="Back to Atlas"[^>]*>\s*←\s*Back to Atlas', html), "breadcrumb lacks aria-label (staged)"

def test_e39_index_links_to_sitemap_html_and_json():
    idx = "share/atlas/index.html"
    assert os.path.exists(idx), "index missing (staged)"
    html = _read(idx)
    # Expect links surfaced in implementation slice
    assert ("sitemap.html" in html) or ("sitemap.json" in html), "no sitemap link visible (staged)"

def test_e40_counts_banner_present_on_index():
    idx = "share/atlas/index.html"
    assert os.path.exists(idx), "index missing (staged)"
    html = _read(idx)
    # Expect a visible counts banner like: <div id="counts">Nodes: N • Jumpers: M</div>
    assert ("id=\"counts\"" in html) or ("Nodes:" in html), "counts banner missing (staged)"
PYTEST_E3840

# Add a Makefile helper to run staged TVs (idempotent)
python3 - <<'ENDPY' | tee evidence/e38gate.make.patch.log
from __future__ import annotations
import pathlib
mf = pathlib.Path("Makefile"); txt = mf.read_text()
target = "\ntvs.atlas.next40:\n\t@pytest -q agentpm/tests/atlas/test_atlas_accessibility_e38_e40.py > evidence/tvs_e38e40.txt || true\n"
if "tvs.atlas.next40:" not in txt:
    mf.write_text(txt + target)
    print("PATCHED: Makefile (tvs.atlas.next40)")
else:
    print("Makefile already has tvs.atlas.next40")
ENDPY

# Run staged TVs to generate evidence tails
make tvs.atlas.next40 || true
tail -n 30 evidence/tvs_e38e40.txt 2>/dev/null | sed 's/^/TVS E38-40: /' | tee evidence/e38gate.tvs_e38e40.tail.txt || true

# Commit and open the staging PR
git add -A
git commit -m "test(TVs): stage E38–E40 (accessibility + sitemap.html + counts banner) as xfail; add tvs.atlas.next40 [hermetic]" || true
git push -u origin HEAD
gh pr create --title "TVs E38+ staged: accessibility + sitemap.html + counts banner (xfail)" \
  --body "Stages E38–E40 TVs (xfail) to require aria-label on breadcrumb, visible sitemap link, and counts banner on Atlas index. Includes helper target \`make tvs.atlas.next40\` for evidence-only runs." \
  --base main --head "$(git rev-parse --abbrev-ref HEAD)" \
  | tee evidence/tvs_e38plus.pr_create.txt || true

# --- Snapshot AFTER ---
echo "=== HEAD.after (short) ===" && git rev-parse --short HEAD | tee evidence/e38gate.head.after.txt
echo "=== BRANCH.after ==="      && git rev-parse --abbrev-ref HEAD | tee evidence/e38gate.branch.after.txt
git status -sb | tee evidence/e38gate.status.after.txt
git diff --name-only origin/main...HEAD | tee evidence/e38gate.diff.names.txt

# Browser Verification note for staging slice
echo "Browser Verification not applicable (TVs staging; screenshots land with implementation)." | tee evidence/e38gate.browser_verification.note.txt

# 3) Evidence to return — what Cursor must paste back into chat
echo "EVIDENCE_LIST:"
printf "%s\n" \
"1) e38gate.head.before.txt" \
"2) e38gate.branch.before.txt" \
"3) e38gate.status.before.txt" \
"4) pr_441.view.json" \
"5) pr_441.required.json" \
"6) pr_441.required_gate.txt" \
"7) pr_441.merge.out.txt" \
"8) e38gate.ruff.tail.txt" \
"9) e38gate.pytest.e06e10.tail.txt" \
"10) e38gate.pytest.e11e13.tail.txt" \
"11) e38gate.pytest.e14e16.tail.txt" \
"12) e38gate.pytest.e17e19.tail.txt" \
"13) e38gate.pytest.e20e22.tail.txt" \
"14) e38gate.pytest.e23e25.tail.txt" \
"15) e38gate.pytest.e26e28.tail.txt" \
"16) e38gate.pytest.e29e31.tail.txt" \
"17) e38gate.pytest.e32e34.tail.txt" \
"18) e38gate.pytest.e35e37.tail.txt" \
"19) e38gate.guard.provenance.tail.txt" \
"20) e38gate.guard.determinism.tail.txt" \
"21) e38gate.guard.graph.tail.txt" \
"22) e38gate.guard.rollups.tail.txt" \
"23) e38gate.guard.exports.tail.txt" \
"24) e38gate.guard.atlas_smoke.tail.txt" \
"25) e38gate.guard.atlas_links.tail.txt" \
"26) e38gate.guard.atlas_download.tail.txt" \
"27) e38gate.guard.atlas_auditjump.tail.txt" \
"28) e38gate.guard.atlas_rawproof.tail.txt" \
"29) e38gate.make.patch.log" \
"30) e38gate.tvs_e38e40.tail.txt" \
"31) tvs_e38plus.pr_create.txt" \
"32) e38gate.head.after.txt" \
"33) e38gate.branch.after.txt" \
"34) e38gate.status.after.txt" \
"35) e38gate.diff.names.txt" \
"36) e38gate.browser_verification.note.txt"

