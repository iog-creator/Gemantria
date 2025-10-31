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
- **Linear history**: Enabled
- **Require signed commits**: Enabled
- **Allow force pushes**: Disabled
- **Allow deletions**: Disabled

## Configuration Details
- **Timestamp**: [Date and Time of Configuration]
- **Configured By**: [GitHub User/Team]
- **Rationale**: These settings ensure the integrity and quality of the `main` branch by enforcing automated checks and mandatory human review for all changes, including those made by administrators.
