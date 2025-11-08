# Release Process

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

### 2. Determine Version Bump
```bash
# Review recent commits to determine version type
git log --oneline --since="last release date"

# Examples:
# - New features → minor bump (1.2.0 → 1.3.0)
# - Bug fixes only → patch bump (1.2.0 → 1.2.1)
# - Breaking changes → major bump (1.2.0 → 2.0.0)
```

### 3. Create Release via GitHub UI

1. Go to [Releases](https://github.com/mccoy/Gemantria.v2/releases)
2. Click "Draft a new release"
3. Choose tag: `v{major}.{minor}.{patch}` (e.g., `v1.3.0`)
4. **Enable "Generate release notes"** - GitHub will automatically compile:
   - PRs merged since last release
   - Contributors
   - Commit summaries
5. Review and edit the auto-generated notes as needed
6. Click "Publish release"

### 4. Post-Release Verification
- [ ] CI runs successfully on the tag
- [ ] Quality badges update automatically (via quality-badges workflow)
- [ ] Release appears in CHANGELOG.md (if automated)

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
