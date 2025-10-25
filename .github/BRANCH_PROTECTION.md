# Branch Protection Configuration for `main`

## Required Status Checks
- `Rules numbering check`
- `Data completeness gate (Rule 037)`
- `Exports smoke (Rule 038)`
- `Share consistency check (no drift)`
- `NEXT_STEPS check`

## Branch Protection Rules
- **Require PR reviews**: Enabled
- **Dismiss stale reviews**: Enabled
- **Require code owner reviews**: Enabled (via CODEOWNERS)
- **Restrict pushes**: Enabled (disallow direct pushes by non-admins)
- **Include administrators**: Disabled (admins must follow same rules)

## Status Check Enforcement
All PRs to `main` must pass the following status checks:
- `Rules numbering check` (Rule numbering integrity - no duplicates, required rules present)
- `Data completeness gate (Rule 037)` (Data persistence completeness - tables exist, joins work)
- `Exports smoke (Rule 038)` (Exports readiness - concept graph non-empty, integrity checks)
- `Share consistency check (no drift)` (Share mirror up-to-date - no drift from manifest)
- `NEXT_STEPS check` (Task completion - no unchecked boxes in NEXT_STEPS.md)

## Configuration Details
- **Branch**: `main`
- **Protection type**: Branch protection rules + status checks + CODEOWNERS
- **Admin enforcement**: Same rules apply to administrators
- **Code owner reviews**: Required for governance-critical files
- **Timestamp**: Configured via GitHub UI
- **Configured by**: Repository administrators

## Verification
To verify current configuration:
1. Go to Repository Settings → Branches
2. Check `main` branch protection rules
3. Confirm required status checks match exactly
4. Verify CODEOWNERS file is active and reviews are required
