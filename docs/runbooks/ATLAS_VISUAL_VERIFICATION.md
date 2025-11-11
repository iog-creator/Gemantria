# Atlas Visual Verification — Browser Workflow

## Purpose

Use Cursor's **Browser** tool to visually verify Atlas Mermaid diagrams, HTML pages, and generated artifacts. This workflow ensures visual content is correctly rendered and accessible.

## Preconditions

- Branch: Current working branch (or main after merge)
- Artifacts: `docs/atlas/*.mmd` and `docs/atlas/index.html` present
- Local server: Python HTTP server for serving static files

## Steps (Cursor)

**Option 1: Use the standardized script (RECOMMENDED):**
```bash
cd /home/mccoy/Projects/Gemantria.v2
make browser.verify
# OR
bash scripts/ops/browser_verify.sh --strict --port 8778
```
The script will start the server and generate instructions in `evidence/webproof/browser_verify_instructions.txt`. Cursor must then execute the browser tool calls listed in that file.

**Option 2: Manual setup:**
1) **Start local HTTP server:**
   ```bash
   cd /home/mccoy/Projects/Gemantria.v2
   source .venv/bin/activate
   python3 -m http.server 8000 >/dev/null 2>&1 & echo $! > .server.pid
   sleep 2
   ```

2) **Navigate to Atlas index page:**
   - Use `browser_navigate` to: `http://localhost:8000/docs/atlas/index.html?nocache=$(date +%s)`
   - **Note:** Use cache-busting query parameter to avoid stale content

3) **Verify page structure:**
   - Use `browser_snapshot` to capture accessibility tree
   - Verify all sections are present:
     - DSN Proofs section
     - Mermaid Views section
     - KPIs panel (if SSI processed)
     - Legend section with error-rate categories

4) **Verify visual content:**
   - Use `browser_take_screenshot` to capture full-page screenshot
   - Verify Legend section is visible with:
     - "err-high: ≥ 20% errors on child node" (red border)
     - "err-med: ≥ 5% errors on child node" (amber border)
     - "err-low: < 5% errors on child node" (grey border)
   - Verify window control description is present

5) **Verify KPIs JSON:**
   - Navigate to: `http://localhost:8000/docs/atlas/_kpis.json`
   - Verify JSON structure:
     - `mode`: "HINT" or "STRICT"
     - `window`: "24h", "7d", or "30d"
     - `success`: integer count
     - `error`: integer count
     - `generated`: RFC3339 timestamp

6) **Verify Mermaid files (if accessible):**
   - Navigate to: `http://localhost:8000/docs/atlas/dependencies.mmd`
   - Verify file downloads or displays correctly
   - Check for class definitions (err-high, err-med, err-low)

7) **Capture evidence:**
   - Save screenshots to `evidence/atlas_*.screenshot.png`
   - Document any issues or missing content
   - Include verification results in PR evidence

8) **Cleanup:**
   ```bash
   kill "$(cat .server.pid)" 2>/dev/null && rm -f .server.pid
   ```

## Verification Checklist

- [ ] Index page loads without errors
- [ ] All sections visible in browser snapshot
- [ ] Legend section present with all three error-rate categories
- [ ] KPIs JSON accessible and valid
- [ ] Screenshots captured and saved to evidence/
- [ ] No console errors in browser
- [ ] HTML structure valid (proper `<html>`, `<head>`, `<body>` tags)

## Common Issues

**Issue:** Legend section not visible in browser snapshot
- **Cause:** Browser caching or missing HTML structure
- **Fix:** Use cache-busting query parameter, verify `<html>`, `<head>`, `<body>` tags present

**Issue:** Body content truncated
- **Cause:** Missing closing tags or malformed HTML
- **Fix:** Verify all tags are properly closed, check HTML structure

**Issue:** KPIs panel not visible
- **Cause:** SSI (Server-Side Includes) not processed by simple HTTP server
- **Fix:** Expected behavior for local verification; SSI processed by GitHub Pages

## Integration with Rule 051

This workflow satisfies Rule 051's browser verification requirement:
- **Required when:** Modifying HTML, CSS, or visual documentation
- **Evidence:** Screenshots and browser snapshots included in PR evidence
- **Mandatory:** Not optional for visual/web outputs per Rule 051

## Related Documentation

- Rule 051: Cursor Insight & Handoff (browser verification requirements)
- `docs/atlas/README.md`: Atlas Mermaid generator documentation
- `docs/runbooks/CURSOR_BROWSER_QA.md`: General browser QA workflow

