# AGENTS.md - docs/atlas Directory

## Directory Purpose

The `docs/atlas/` directory contains documentation for the atlas aspects of the Gematria analysis system, including compliance dashboards, guard receipts, browser interfaces, and webproof pages.

## Key Documents

- `index.html` - Main Atlas landing page
- `browser/guard_receipts.html` - Guard receipts index (E91)
- `browser/violations.html` - Violations browser (E89, stub for now)
- `dashboard/compliance_summary.html` - Compliance summary dashboard (E86)
- `dashboard/compliance_timeseries.html` - Compliance time-series dashboard (E87)
- `dashboard/compliance_heatmap.html` - Compliance heatmap dashboard (E87)
- `webproof/` - Webproof pages for various compliance checks
- `mcp_catalog_view.html` - MCP catalog viewer

## PLAN-079 E95: Atlas Links Integrity

**Guard:** `scripts/guards/guard_atlas_links.py`

**Purpose:** Validates link integrity across all Atlas HTML pages to ensure no broken internal links and proper external link marking.

**Link Classification:**

1. **Internal Links** (relative paths within `docs/atlas/`):
   - Must resolve to existing files within `docs/atlas/`
   - Broken internal links cause guard to fail

2. **External Links** (http:// or https://):
   - Must be explicitly marked as external via:
     - `class` containing "external", OR
     - `rel` containing "external", OR
     - `data-external="true"`
   - Unmarked external links cause guard to fail

3. **Absolute Paths** (`/...`):
   - Treated as app-level routes (not file paths)
   - Tracked separately in `details.absolute_paths`
   - Should be marked as external if they point outside the docs tree

4. **Whitelisted Links** (evidence/ and share/):
   - Links to `../../evidence/` or `../../../share/` are whitelisted
   - These are diagnostic/export links, reported in `details.whitelisted_links` but don't fail the guard
   - Allows Atlas pages to link to JSON exports and evidence files

**Guard Output:**

- `evidence/guard_atlas_links.json` - JSON verdict with:
  - `ok`: Overall pass/fail status
  - `checks`: Boolean checks (html_scanned, no_broken_internal_links, external_links_marked)
  - `counts`: Counts of links by type
  - `details`: Lists of broken/unmarked/whitelisted/absolute links

**Make Target:** `make guard.atlas.links`

**Integration:** E95 is integrated into the E99 browser screenshot integrated guard.

## Documentation Standards

- All HTML pages should use relative links within `docs/atlas/` for internal navigation
- External links must be marked with `rel="external"` or `data-external="true"`
- Links to evidence/share directories are allowed but tracked separately

## Development Guidelines

- When adding new Atlas pages, ensure all links are valid and properly classified
- Run `make guard.atlas.links` before committing changes to Atlas HTML
- If adding links to evidence/share, they will be whitelisted automatically
- Absolute paths (`/...`) should be marked as external if they're app routes

## Related ADRs

| Document | Related ADRs |
|----------|--------------|
| Atlas Links Integrity (E95) | PLAN-079 |
