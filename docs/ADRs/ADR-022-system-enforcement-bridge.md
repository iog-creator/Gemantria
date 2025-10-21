# ADR-022: System Enforcement Bridge

## Status
Accepted

## Related ADRs
- ADR-000: LangGraph adoption for pipeline orchestration
- ADR-013: Comprehensive documentation synchronization enhancement
- ADR-017: Agent documentation presence enforcement
- ADR-019: Forest governance & phase gate system

## Related Rules
- Rule 026: System Enforcement Bridge
- Rule 027: Docs Sync Gate
- Rule 028: Phase Freshness
- Rule 029: ADR Coverage

## Context

The Gemantria project faced a critical architectural flaw: Cursor rules were designed as AI behavioral guidelines but presented as system constraints. This created a gap between stated behavior and actual enforcement, requiring manual intervention for every documentation update and phase transition.

**Root Cause Analysis:**
- Cursor rules appeared to be "ALWAYS APPLIED - NO EXCEPTIONS"
- In reality, they were voluntary AI guidelines masquerading as system constraints
- No automated enforcement mechanisms existed (CI, pre-commit, branch protection)
- Manual prompting required for all documentation sync and phase gate validation

**Evidence of the Gap:**
- 4 missing ADRs for critical rules (Rules 009, 016, 017, 019)
- Documentation sync violations went undetected by CI
- Phase gates weren't enforced (forest freshness ignored)
- System presented false sense of security

## Decision

Implement a **System Enforcement Bridge** that transforms voluntary AI guidelines into mandatory system constraints through:

1. **Pre-commit hooks** for local enforcement
2. **CI workflows** for PR validation
3. **Branch protection rules** requiring green checks
4. **Automated verification** via `rules_guard.py` script

## Rationale

### Why This Solution

**Closes the Enforcement Gap:**
- Pre-commit hooks catch violations before commits
- CI workflows prevent merges of non-compliant PRs
- Branch protection ensures no green = no merge
- Rules now have real teeth, not just documentation

**Maintains Developer Experience:**
- Fast local feedback via pre-commit
- Clear error messages explaining violations
- Override mechanisms for emergency situations
- Automated verification reduces manual overhead

**Aligns with Project Priorities:**
- **Correctness**: Enforces code > bible_db > LLM priority through documentation requirements
- **Determinism**: Prevents drift between stated rules and actual behavior
- **Safety**: Fail-closed enforcement of critical safety rules (Qwen Live Gate, DB read-only)

### Alternatives Considered

**Alternative 1: Manual Enforcement Only**
- Continue requiring manual rule following
- Pros: Simple, no tooling overhead
- Cons: **Violates project determinism**, requires perfect human compliance

**Alternative 2: IDE Integration Only**
- VS Code/Cursor plugins for rule enforcement
- Pros: Real-time feedback
- Cons: **Not system-level**, works only in specific IDE, no CI enforcement

**Alternative 3: CI-Only Enforcement**
- Remove pre-commit, enforce only at PR time
- Pros: Simpler setup
- Cons: **Poor developer experience**, late feedback, wasted CI time

**Chosen Solution Superior:**
- **System-level enforcement** (works everywhere)
- **Early feedback** (pre-commit catches issues immediately)
- **CI validation** (prevents bad merges)
- **Branch protection** (enforces at repository level)

## Consequences

### Positive Outcomes

**Documentation Integrity:**
- Code changes automatically require documentation updates
- ADR coverage enforced for rule/schema changes
- Forest freshness validated before PRs
- Schema validation ensures export consistency

**Developer Productivity:**
- Fast feedback via pre-commit hooks
- Clear violation messages with fix instructions
- Automated verification reduces manual review burden
- Consistent enforcement across all environments

**Project Safety:**
- Qwen Live Gate enforcement (no mocks in production)
- Database safety rules (read-only enforcement)
- Schema change requirements (ADR + tests mandatory)
- Phase gate validation prevents architectural drift

### Implementation Requirements

**New Files Required:**
- `.pre-commit-config.yaml`: Hook configuration
- `scripts/rules_guard.py`: Enforcement logic
- `.github/workflows/system-enforcement.yml`: CI validation
- `.github/pull_request_template.md`: Updated PR template

**New Rules Required:**
- Rule 026: System Enforcement Bridge
- Rule 027: Docs Sync Gate
- Rule 028: Phase Freshness
- Rule 029: ADR Coverage

**Makefile Updates:**
- `make hooks`: Install pre-commit hooks
- `make verify.all`: Run all verification gates

### Negative Outcomes

**Setup Complexity:**
- Additional tooling (pre-commit, jsonschema dependency)
- Configuration management across developer machines
- Learning curve for new team members

**Maintenance Overhead:**
- Pre-commit configuration must stay in sync with rules
- CI workflow updates when enforcement logic changes
- Branch protection settings must be configured

**Override Mechanisms:**
- Emergency override (`ALLOW_OLD_FOREST=1`) could be abused
- CI bypass possible through direct pushes (mitigated by branch protection)

## Implementation Details

### Pre-commit Hook Configuration

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks: [{ id: ruff, args: ["--fix"] }]
  # ... other standard hooks
  - repo: local
    hooks:
      - id: rules-guard
        name: rules-guard (docs/ADR/SSOT sync, forest gate, schemas, evidence)
        entry: python scripts/rules_guard.py
        language: python
        additional_dependencies: ["jsonschema==4.23.0"]
        pass_filenames: false
```

### Enforcement Logic (rules_guard.py)

**Core Checks:**
1. **Doc Sync**: Code changes require documentation updates
2. **ADR Coverage**: Rule/migrations changes require ADR updates
3. **Forest Freshness**: Overview must be regenerated within 24h
4. **Schema Presence**: Required SSOT schemas must exist
5. **Schema Validation**: Export files must validate against schemas
6. **PR Evidence**: Export changes require evidence markers in PR body

**Fail-Closed Design:**
- Any violation exits with code 2 (pre-commit failure)
- Clear error messages explaining violations
- Graceful handling of missing dependencies/config

### CI Integration

```yaml
name: system-enforcement
on:
  pull_request:
    types: [opened, synchronize, edited]
jobs:
  enforce:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: pre-commit/action@v3.0.1
      - name: Run rules guard (hard gate)
        run: python scripts/rules_guard.py
```

### Branch Protection Requirements

**Required Status Checks:**
- `system-enforcement (enforce)`: Must pass
- Existing checks: `verify-stats`, `verify-correlations`

**Settings:**
- Require branches to be up to date before merging
- Require PRs to have at least one approval
- Include administrators in restrictions

## Notes

### Emergency Overrides

**ALLOW_OLD_FOREST=1:**
- Allows stale forest for emergency hotfix branches
- **Never allowed on CI** (hard-coded restriction)
- Must be explicitly set locally for development emergencies
- Logged in PR body for transparency

### Future Extensions

**Planned Enhancements:**
- Automated ADR template generation
- Link validation across documentation
- Export consistency verification
- Schema drift detection

**Integration Points:**
- GitHub MCP for repository operations
- Prometheus metrics for enforcement statistics
- Automated documentation generation

### Migration Strategy

**Phase 1: Implementation**
- Deploy enforcement bridge
- Configure branch protection
- Update PR template
- Train team on new workflow

**Phase 2: Stabilization**
- Monitor false positives/negatives
- Refine error messages
- Add override safeguards
- Update documentation

**Phase 3: Enhancement**
- Add advanced validations
- Integrate with GitHub MCP
- Automated remediation suggestions

### Success Metrics

**Enforcement Effectiveness:**
- 100% documentation sync compliance
- Zero stale forest violations on main branch
- All PRs pass system enforcement checks
- ADR coverage maintained for schema changes

**Developer Experience:**
- Pre-commit hook failures < 5% of commits
- Average time to fix violations < 5 minutes
- Clear error messages in 100% of cases
- Override usage < 1% of PRs

### Risk Mitigation

**False Positives:**
- Comprehensive testing before deployment
- Override mechanisms for edge cases
- Clear documentation of expected behavior
- Team feedback integration

**Adoption Resistance:**
- Clear communication of benefits
- Training sessions for new workflow
- Support during transition period
- Gradual rollout with monitoring

### Related Changes

**Documentation Updates:**
- AGENTS.md: Update workflow section
- PR template: Add enforcement checklist
- Developer onboarding: Include hook setup
- Troubleshooting guide: Common violation fixes

**Tooling Updates:**
- Makefile: Add verification targets
- Scripts: New rules_guard.py
- CI: New enforcement workflow
- Branch protection: Updated requirements
