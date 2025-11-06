# ADR-060: Automated Metadata Enforcement

## Status
Accepted

## Related ADRs
- ADR-058: Project Management System (PMS) v2.0
- ADR-059: Hints Envelope Architecture
- ADR-017: Agent documentation presence enforcement

## Related Rules
- Rule-047: AI navigation metadata (AlwaysApply)
- Rule-050: OPS contract
- Rule-058: Auto-housekeeping

## Context

The Gemantria project has grown to include multiple governance systems and documentation sources:

- **AGENTS.md files**: Project governance documentation (plural - root, docs/, src/)
- **Cursor rules**: IDE-level governance enforcement (.mdc files)
- **Architecture decisions**: ADR documentation for significant changes
- **Code metadata**: Module-level documentation and governance links

Without automated enforcement, we experienced:

- **Metadata drift**: Files missing required governance metadata
- **Inconsistent documentation**: Some files documented, others not
- **Maintenance burden**: Manual checking and updating of metadata
- **Quality degradation**: Governance metadata becoming stale or incorrect

The project needed a system that automatically enforces metadata requirements across all files and maintains consistency with governance sources.

## Decision

Implement **Automated Metadata Enforcement System** that:

### Core Requirements
1. **File Metadata Standards**: All source files must include governance metadata
2. **Automated Enforcement**: Metadata requirements checked and enforced automatically
3. **Envelope Integration**: Triggered by hints envelopes with imperative commands
4. **Recovery Mechanisms**: Automatic fixing of missing or incorrect metadata

### Metadata Standards
```python
"""
Module description and purpose.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""

# Required metadata block at file start
# Links to governance sources and architectural decisions
```

### Enforcement Triggers
- **Pre-commit**: Staged file validation
- **CI Pipeline**: Comprehensive metadata checking
- **Envelope Commands**: `CHECK_METADATA_REQUIREMENTS` imperative command
- **Manual**: `python pms/scripts/enforce_metadata.py --staged --fix`

### Enforcement Levels
1. **REQUIRED**: Must be present and correct, blocks commits
2. **RECOMMENDED**: Suggested but not enforced, warnings only
3. **OPTIONAL**: Nice to have, no enforcement

## Rationale

### Benefits
- **Consistency**: All files follow the same metadata standards
- **Discoverability**: Clear links between code and governance decisions
- **Maintenance**: Automated enforcement reduces manual overhead
- **Quality**: Prevents metadata drift and staleness
- **Navigation**: AI and human developers can understand governance context

### Trade-offs
- **Development Overhead**: Initial metadata addition for existing files
- **Enforcement Overhead**: Runtime checking adds minor performance cost
- **Learning Curve**: New metadata format to learn and apply
- **Maintenance**: Metadata standards require occasional updates

### Quantitative Impact
- **Metadata Compliance**: 100% vs variable (significant improvement)
- **Discovery Time**: Reduced through clear governance links
- **Review Efficiency**: Faster code reviews with context
- **Maintenance Time**: Automated vs manual metadata management

## Alternatives Considered

### Alternative 1: Manual Metadata Management
- **Pros**: No automation overhead, direct control
- **Cons**: Inconsistent application, high maintenance burden
- **Rejected**: Doesn't scale and leads to quality degradation

### Alternative 2: IDE Plugins Only
- **Pros**: Developer-friendly, real-time feedback
- **Cons**: Not enforced in CI, dependent on IDE usage
- **Rejected**: Doesn't provide comprehensive enforcement

### Alternative 3: Database-Driven Metadata
- **Pros**: Queryable, centralized, comprehensive
- **Cons**: Complex, requires additional infrastructure
- **Rejected**: Overkill for file-level metadata requirements

## Consequences

### Positive Outcomes
- **Immediate**: Clear governance links in all source files
- **Short-term**: Automated enforcement prevents metadata drift
- **Long-term**: Consistent, discoverable codebase with clear architectural context

### Implementation Requirements
- **Metadata Standards**: Clear format and requirements specification
- **Enforcement Engine**: Automated checking and fixing system
- **Integration Points**: Pre-commit hooks, CI pipeline, envelope commands
- **Templates**: Standardized metadata blocks for different file types

### Risks
- **Resistance to Change**: Developers may resist additional metadata requirements
- **Template Staleness**: Metadata templates may become outdated
- **Enforcement Intrusiveness**: Overly strict enforcement could hinder development

### Mitigation Strategies
- **Gradual Adoption**: Start with new files, migrate existing files gradually
- **Clear Benefits**: Demonstrate value through better navigation and understanding
- **Flexible Enforcement**: Allow some customization while maintaining standards

## Implementation Notes

### Metadata Format Standards

#### Python Files
```python
"""
Module docstring with governance links.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""

# Implementation follows ADR-019 data contracts
# Rule-050 governs operational procedures
```

#### Markdown Files
```markdown
---
rules: [039, 050, 058]
adrs: [032, 019]
---

# Document Title

Related Rules: Rule-039, Rule-050, Rule-058
Related ADRs: ADR-032, ADR-019
```

#### Configuration Files
```yaml
# Governance metadata for configuration files
# rules: rule-039, rule-050
# adrs: adr-032, adr-019
```

### Enforcement Workflow
1. **Detection**: Pre-commit hooks or CI checks identify missing metadata
2. **Validation**: Automated checking against standards and references
3. **Correction**: Auto-fix for common issues, suggestions for complex cases
4. **Verification**: Post-fix validation ensures compliance

### Integration Points
- **Git Hooks**: Pre-commit validation of staged files
- **CI Pipeline**: Comprehensive metadata checking
- **Envelope System**: `CHECK_METADATA_REQUIREMENTS` command triggers enforcement
- **IDE Integration**: Real-time feedback and auto-completion

### Safety Mechanisms
- **Non-destructive**: Enforcement never modifies working code logic
- **Backup Creation**: Original files backed up before modification
- **Rollback Support**: Easy reversion of automated changes
- **Gradual Enforcement**: Warnings before strict enforcement

## Notes

### File Type Coverage
- **Source Code**: Python, TypeScript, Go, Rust, etc.
- **Documentation**: Markdown files, READMEs, guides
- **Configuration**: YAML, JSON, TOML, INI files
- **Infrastructure**: Docker, Kubernetes, Terraform files

### Future Enhancements
- **AI-Powered Metadata**: ML-assisted metadata generation and validation
- **Cross-Reference Validation**: Automated checking of rule and ADR references
- **Metadata Analytics**: Usage patterns and effectiveness metrics
- **Template Evolution**: Automated template updates based on project changes

### Success Metrics
- **Compliance Rate**: >95% of files with correct metadata
- **Auto-fix Rate**: >80% of issues resolved automatically
- **Developer Satisfaction**: Positive feedback on discoverability improvements
- **Review Efficiency**: Measurable reduction in review time due to better context

---

**Implementation**: Complete metadata enforcement system with envelope integration
**Date**: [Current Date]
**Status**: Accepted and implemented
