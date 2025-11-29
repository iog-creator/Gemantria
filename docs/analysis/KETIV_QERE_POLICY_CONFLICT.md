# Ketiv/Qere Policy Conflict Analysis

## Summary

This document summarizes the policy decision regarding Ketiv (written form) vs. Qere (read form) for gematria calculations, and how the implementation enforces the chosen policy.

## Current Law (SSOT)

**Ketiv-Primary Policy** (ADR-002, Phase 2):
- **Ketiv** (כתיב, written form) is the primary source for gematria calculations
- Ketiv is stored in the `surface` field of noun records
- All gematria calculations use the Ketiv (written form)
- **Qere** (קרי, read form) is recorded as a variant in `variant_surface` when it differs from Ketiv
- Qere is **not** used for gematria calculations

**Rationale:**
- Ketiv represents the canonical written text preserved in manuscripts
- Gematria calculations must be consistent and reproducible
- The written form is the stable, authoritative source for numeric calculations

## Past Proposal (Rejected)

**Qere-First Policy** (Phase 13 concept, archived):
- Alternative approach where Qere (read form) would be primary for gematria
- **Status**: Explicitly rejected in Phase 2 (2025-01)
- **Reason**: Gematria must be based on the preserved manuscript form (Ketiv), not the vocalized reading tradition (Qere)
- **Archive Note**: This alternative is documented but not active policy. Any future reconsideration would require a new ADR superseding ADR-002.

## Implementation Behavior

### Database Schema (Migration 052)

The `gematria.nouns` table includes:
- `surface`: Ketiv (written form) - primary for gematria
- `variant_surface`: Qere (read form) - recorded as variant, not used for calculations
- `variant_type`: Type of variant (ketiv, qere, other)
- `is_ketiv`: Boolean flag (TRUE if surface is Ketiv, FALSE if Qere)
- `span_start`, `span_end`: Character positions for variant spans

### Code Enforcement

1. **Noun Adapter** (`src/ssot/noun_adapter.py`):
   - Enforces Ketiv-primary policy: Ketiv goes in `surface`, Qere in `variant_surface`
   - `is_ketiv` flag defaults to `True` (Ketiv is primary)

2. **Gematria Calculation** (`src/core/hebrew_utils.py`):
   - `calculate_gematria()` uses the surface form (Ketiv)
   - `get_ketiv_for_gematria()` helper ensures Ketiv is extracted for calculations
   - Qere is never used for gematria calculations

3. **Validation Guard** (`scripts/guards/guard_ketiv_primary.py`):
   - Validates that gematria calculations use Ketiv (surface), not Qere
   - Fails if Qere is used for calculations or if policy is violated
   - Integrated into `make guard.ketiv.primary` and `make reality.green` (STRICT mode)

### Schema Contract

The `graph.schema.json` includes variant fields:
- `surface`: Description explicitly states "Ketiv (written form) - primary for gematria calculations per ADR-002"
- `variant_surface`: Description states "Alternative surface form (e.g., Qere reading when surface is Ketiv)"
- `is_ketiv`: Boolean flag with description explaining Ketiv is primary for gematria

## Enforcement Mechanisms

1. **Guard**: `guard.ketiv.primary` validates policy compliance in exports
2. **Reality Green**: Guard runs in STRICT mode as part of `make reality.green`
3. **Tests**: 9 tests in `tests/unit/test_ketiv_primary.py` verify policy enforcement
4. **Schema**: JSON schema enforces variant field structure and descriptions

## How to Verify

```bash
# Run the guard directly
make guard.ketiv.primary

# Run full reality green (includes guard in STRICT mode)
make reality.green

# Run tests
python -m pytest tests/unit/test_ketiv_primary.py -v
```

## References

- **ADR-002**: Gematria and Normalization Rules (Ketiv-primary policy)
- **Migration 052**: Database schema for variant support
- **Phase 2**: Ketiv/Qere Policy implementation (PR #588)
- **Guard**: `scripts/guards/guard_ketiv_primary.py`
- **Tests**: `tests/unit/test_ketiv_primary.py`

## Future Considerations

If a Qere-first policy is ever reconsidered:
1. A new ADR must supersede ADR-002
2. Database schema would need migration to swap primary/secondary roles
3. All gematria calculations would need recalculation
4. Guard and tests would need updates
5. This document would need revision to reflect new policy

**Current Status**: Ketiv-primary policy is active and enforced. Qere-first is archived, not active.

