# Release Process

## v0.0.2 (2025-11-11)

### Browser Verification Template + STRICT Webproof + DSN Automation

**Highlights:**
- Mandatory Browser Verification template in `GPT_SYSTEM_PROMPT.md` (Rule-051/067)
- STRICT webproof enforcement on release tags (Rule-067)
- Automated DSN secrets/variables sync to GitHub
- Atlas UI enhancements with MCP catalog integration

**Key Changes:**
- **docs**: Browser Verification template (RFC-077) — mandatory OPS OUTPUT section for visual/web artifacts
- **ci**: Aligned tagproof workflow with STRICT webproof + DSN posture requirements
- **ops**: Created `scripts/ops/sync_github_dsns.sh` for automatic GitHub secrets/variables sync
- **ops**: Rule-067 webproof hardening — fails on Mermaid syntax errors
- **mcp**: Atlas UI enhancements — live fetch, catalog view, read-only endpoints

**CI Verification:**
- Tag `v0.0.2` tagproof workflow: ✅ **SUCCESS** (run 19280575725)
- All STRICT checks passed: webproof, DSN posture, guards
- All required secrets/variables verified: `ATLAS_DSN`, `BIBLE_DB_DSN`, `GEMATRIA_DSN`

**Related PRs:**
- PR #406: Browser Verification template (Rule-051/067); RFC-077
- PR #405: CI alignment with STRICT webproof + DSN posture

## v2.0 (2025-11-10)
- Overhauled master reference (GEMANTRIA_MASTER_REFERENCE.md v2)
- Added orchestrator layering (LangGraph + Prefect)
- Added MCP-style agent interface guidance
- Implemented Playwright UI tests (tests/ui/test_atlas_node_click.py)
- Schema-to-doc automation via `make schema.docs` (generates Markdown from JSON Schema files)
- Added `ui.test` Makefile target for Playwright test execution
- CI integration: UI tests run in PR workflow

## infra/v6.2.3 — RFC3339 fast-lane (2025-11-08)
- STRICT guard on release tags; HINT on main/PRs
- Normalization step added for legacy epoch exports

This document outlines the standardized release process for Gemantria.

## Overview

Releases follow [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Process

### 1. Pre-Release Checklist
- [ ] All PRs in merge train merged successfully
- [ ] Main branch is green (all required checks pass)
- [ ] No outstanding merge conflicts
- [ ] Share directory synchronized (`make share.sync`)
- [ ] Canonical smoke targets pass (hermetic validation):
  ```bash
  make book.smoke
  make ci.exports.smoke
  make eval.graph.calibrate.adv
  ```
- [ ] All guards pass (run `make guards.all`)
- [ ] Housekeeping complete (`make housekeeping`)
- [ ] Evidence artifacts present in `evidence/` directory:
  - `evidence/exports_guard.verdict.json`
  - `evidence/exports_rfc3339.verdict.json`
  - `evidence/guard_knowledge.json`
  - `evidence/guard_dsn_centralized.json` (if applicable)

### 2. Determine Version Bump
```bash
# Review recent commits to determine version type
git log --oneline --since="last release date"

# Examples:
# - New features → minor bump (1.2.0 → 1.3.0)
# - Bug fixes only → patch bump (1.2.0 → 1.2.1)
# - Breaking changes → major bump (1.2.0 → 2.0.0)
```

### 3. Tagging Flow

#### 3.1. Create and Push Tag

```bash
# Ensure you're on main branch and up to date
git checkout main
git pull --ff-only

# Create annotated tag (recommended for releases)
git tag -a v{major}.{minor}.{patch} -m "Release v{major}.{minor}.{patch}: {brief description}"

# Example:
git tag -a v1.3.0 -m "Release v1.3.0: Add correlation UI and DSN centralization"

# Push tag to remote
git push origin v{major}.{minor}.{patch}
```

**Tag Naming Convention:**
- Use semantic versioning: `v{major}.{minor}.{patch}`
- Pre-releases: `v{major}.{minor}.{patch}-rc.{n}` (e.g., `v1.3.0-rc.1`)
- Development tags: `dev/{feature}` (not for releases)

#### 3.2. Create Release via GitHub UI

1. Go to [Releases](https://github.com/mccoy/Gemantria.v2/releases)
2. Click "Draft a new release"
3. Select the tag you just pushed (e.g., `v1.3.0`)
4. **Enable "Generate release notes"** - GitHub will automatically compile:
   - PRs merged since last release
   - Contributors
   - Commit summaries
5. Review and edit the auto-generated notes as needed
6. **Attach evidence artifacts** (if applicable):
   - Upload `evidence/guard_knowledge.json`
   - Upload `evidence/exports_guard.verdict.json`
   - Upload any other relevant evidence files
7. Click "Publish release"

#### 3.3. Tag Build Verification

After pushing the tag, CI will run in **STRICT mode** (not HINT-only):

- **Required checks**:
  - `ruff` (formatting + linting)
  - `build-pr` (CI pipeline)
  - All guards run in STRICT mode (`STRICT_*` env vars enabled)
- **Evidence requirements**:
  - All smoke targets must pass
  - All guards must pass (no HINT-only mode)
  - Evidence artifacts must be present and valid
  - Atlas screenshots: REQUIRED (Rule-067 webproof)
- **RO-DSN requirement**: Tag builds require `GEMATRIA_RO_DSN` or `ATLAS_DSN_RO` (peer equivalence, fail-closed if neither present)

### 4. Post-Release Verification

#### 4.1. CI Verification
- [ ] CI runs successfully on the tag (check GitHub Actions)
- [ ] All required checks pass (ruff, build-pr)
- [ ] All guards pass in STRICT mode (no HINT-only)
- [ ] Evidence artifacts are generated and valid

#### 4.2. Evidence Verification
- [ ] Quality badges update automatically (via quality-badges workflow)
- [ ] Evidence files present in `evidence/` directory:
  - `evidence/exports_guard.verdict.json` (exports validation)
  - `evidence/exports_rfc3339.verdict.json` (timestamp validation)
  - `evidence/guard_knowledge.json` (governance drift check)
  - `evidence/guard_dsn_centralized.json` (DSN centralization check)
- [ ] Share directory synchronized (`make share.sync`)
- [ ] Release appears in CHANGELOG.md (if automated)

#### 4.3. Documentation Verification
- [ ] README.md badges reflect new release
- [ ] Version references updated (if applicable)
- [ ] Release notes are clear and actionable

### 5. Update Documentation (if needed)
- Update version references in README.md
- Update any version-specific documentation
- Run `make share.sync` if docs changed

## Automation

The following workflows handle release-related automation:

- **quality-badges.yml**: Updates README badges after releases
- **ci.yml**: Validates releases (runs on tag pushes)
- **share-sync**: Mirrors documentation changes

## Branch Protection

Main branch requires:
- Required status checks: `ruff`, `ci/build`
- Reviews from code owners (CODEOWNERS file)
- No merge conflicts

## Notes

- Releases are immutable once published (per GitHub's design)
- Use pre-releases (e.g., `v1.3.0-rc.1`) for testing major changes
- Keep release notes focused and actionable for users
## v0.0.3 (2025-11-12)


### Highlights

- **STRICT tag lane:** Added read-only MCP guard step (`make guard.mcp.db.ro STRICT_DB_PROBE=1`) proving `mcp.v_catalog` on tags.

- **Hermetic PRs:** No DB/network probes in PR CI; STRICT proofs run only in tagproof.

- **Governance:** Tool Bus remains **OFF** by default; Guarded Tool Calls P0 execution landed with TVs 01–05 green.

### Proofs (tagproof)

- RO guard executed successfully (see `share/releases/v0.0.3/tagproof/*`).

- Webproof artifacts mirrored when locally available.

## v0.0.3 (2025-11-12)


### Highlights

- **STRICT tag lane:** Added read-only MCP guard step (`make guard.mcp.db.ro STRICT_DB_PROBE=1`) proving `mcp.v_catalog` on tags.

- **Hermetic PRs:** No DB/network probes in PR CI; STRICT proofs run only in tagproof.

- **Governance:** Tool Bus remains **OFF** by default; Guarded Tool Calls P0 execution landed with TVs 01–05 green.

### Proofs (tagproof)

- RO guard executed successfully (see `share/releases/v0.0.3/tagproof/*`).

- Webproof artifacts mirrored when locally available.


