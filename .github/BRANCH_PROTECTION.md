# Branch Protection Configuration for `main`

## Required Status Checks
- `make ci.data.verify`
- `make ci.exports.smoke`

## Branch Protection Rules
- **Require PR reviews**: Enabled
- **Dismiss stale reviews**: Enabled
- **Require code owner reviews**: Disabled
- **Restrict pushes**: Enabled (disallow direct pushes by non-admins)
- **Include administrators**: Disabled (admins must follow same rules)

## Status Check Enforcement
All PRs to `main` must pass the following status checks:
- `make ci.data.verify` (Data Persistence Completeness - Rule 037)
- `make ci.exports.smoke` (Exports Smoke Gate - Rule 038)

## Configuration Details
- **Branch**: `main`
- **Protection type**: Branch protection rules + status checks
- **Admin enforcement**: Same rules apply to administrators
- **Timestamp**: Configured via GitHub UI
- **Configured by**: Repository administrators

## Verification
To verify current configuration:
1. Go to Repository Settings → Branches
2. Check `main` branch protection rules
3. Confirm required status checks match exactly
