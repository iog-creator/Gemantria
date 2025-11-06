# ADR-061: Imperative Command Protocol

## Status
Accepted

## Related ADRs
- ADR-058: Project Management System (PMS) v2.0
- ADR-059: Hints Envelope Architecture
- ADR-022: System enforcement bridge

## Related Rules
- Rule-039: Execution contract
- Rule-050: OPS contract
- Rule-058: Auto-housekeeping

## Context

Traditional agent communication relies on voluntary cooperation and passive messaging:

- **Request-response patterns**: Agents may ignore or delay responses
- **Event-driven systems**: No guarantee of processing or action
- **Logging systems**: Information capture without enforcement capability
- **Human oversight**: Manual intervention required for critical actions

The Gemantria project needed a communication protocol that ensures **critical commands are executed** regardless of agent autonomy or discretion. This is essential for:

- **Safety mechanisms**: Commands that must execute to prevent harm
- **Compliance requirements**: Regulatory or contractual obligations
- **Quality gates**: Actions that cannot be bypassed
- **Emergency procedures**: Immediate response to critical situations

## Decision

Implement **Imperative Command Protocol** - a communication system where designated commands **MUST** be executed by receiving agents:

### Protocol Structure
```json
{
  "type": "hints_envelope",
  "version": "1.0",
  "imperative_commands": [
    "AGENT_STOP_AND_PAY_ATTENTION",
    "CHECK_METADATA_REQUIREMENTS",
    "ENFORCE_PROJECT_GOVERNANCE"
  ],
  "enforcement_level": "CRITICAL",
  "ignore_risk": "PIPELINE_ABORT",
  "command_metadata": {
    "timeout_seconds": 300,
    "retry_policy": "exponential_backoff",
    "rollback_on_failure": true
  }
}
```

### Command Categories

#### Critical Commands (Pipeline Abort Risk)
- **`AGENT_STOP_AND_PAY_ATTENTION`**: Forces immediate attention to envelope
- **`ABORT_IF_CRITICAL_ISSUES`**: Terminates pipeline if critical issues detected
- **`VALIDATE_ENVELOPE_CONTENTS`**: Ensures envelope integrity (cannot be bypassed)

#### High Priority Commands (Pre-continuation Execution)
- **`CHECK_METADATA_REQUIREMENTS`**: Validates file metadata requirements
- **`PROCESS_HINTS_ENVELOPE_IMMEDIATELY`**: Immediate hints processing
- **`ENFORCE_PROJECT_GOVERNANCE`**: Executes governance rules and policies

#### Extensible Framework
- **Command Registry**: Pluggable command system for future extensions
- **Priority System**: Commands executed in priority order
- **Timeout Protection**: Prevents infinite command execution
- **Audit Trail**: Complete record of command execution and results

### Safety Mechanisms
- **Timeout Protection**: Commands cannot run indefinitely
- **Circuit Breakers**: Prevent cascade failures
- **Rollback Support**: Failed commands can trigger rollback procedures
- **Resource Limits**: CPU and memory limits on command execution

## Rationale

### Benefits
- **Execution Guarantee**: Critical commands cannot be ignored or delayed
- **System Safety**: Ensures safety mechanisms always activate
- **Compliance Assurance**: Regulatory requirements automatically enforced
- **Quality Control**: Prevents quality degradation through enforcement
- **Predictable Behavior**: System behavior becomes deterministic for critical operations

### Trade-offs
- **Reduced Autonomy**: Agents lose some decision-making freedom
- **Performance Impact**: Command execution adds processing overhead
- **Complexity**: Additional protocol layer increases system complexity
- **Maintenance**: Command system requires careful maintenance

### Quantitative Impact
- **Command Execution Rate**: 100% for imperative commands vs variable for voluntary
- **Safety Incident Rate**: Significant reduction through guaranteed enforcement
- **Compliance Rate**: 100% automated vs manual verification
- **System Predictability**: Deterministic behavior for critical operations

## Alternatives Considered

### Alternative 1: Voluntary Command System
- **Pros**: Respects agent autonomy, simple implementation
- **Cons**: Commands may be ignored, no enforcement guarantee
- **Rejected**: Doesn't provide the safety and compliance guarantees needed

### Alternative 2: Direct API Calls
- **Pros**: Immediate execution, clear success/failure
- **Cons**: Tight coupling, no audit trail, synchronous only
- **Rejected**: Doesn't work across different systems and agents

### Alternative 3: Database-Driven Commands
- **Pros**: Persistent, queryable, transactional
- **Cons**: Complex infrastructure, not suitable for real-time enforcement
- **Rejected**: Too heavy for imperative command execution needs

## Consequences

### Positive Outcomes
- **Immediate**: Guaranteed execution of critical safety and compliance commands
- **Short-term**: Predictable system behavior and automated enforcement
- **Long-term**: Self-regulating system with automatic quality maintenance

### Implementation Requirements
- **Command Registry**: Extensible system for registering new imperative commands
- **Execution Engine**: Safe command execution with timeout and resource limits
- **Audit System**: Complete logging of command execution and results
- **Testing Framework**: Comprehensive testing of command execution scenarios

### Risks
- **Command Abuse**: Overuse could create system brittleness
- **Performance Degradation**: Imperative commands could impact system performance
- **False Positives**: Incorrect command issuance could cause unnecessary aborts

### Mitigation Strategies
- **Conservative Command Set**: Start with essential commands only
- **Performance Monitoring**: Track command execution impact
- **Command Validation**: Strict criteria for when imperative commands can be issued
- **Gradual Rollout**: Test thoroughly before enabling in production

## Implementation Notes

### Command Execution Lifecycle
1. **Command Reception**: Envelope with imperative commands received
2. **Validation**: Commands validated against registry and permissions
3. **Priority Sorting**: Commands sorted by execution priority
4. **Sequential Execution**: Commands executed in priority order
5. **Result Aggregation**: Success/failure results collected
6. **Audit Logging**: Complete execution record maintained
7. **Follow-up Actions**: Rollback or notification based on results

### Command Registry Design
```python
COMMAND_REGISTRY = {
    "AGENT_STOP_AND_PAY_ATTENTION": {
        "handler": stop_and_pay_attention,
        "priority": "CRITICAL",
        "timeout": 30,
        "rollback": False,
        "description": "Forces immediate agent attention to envelope contents"
    },
    "CHECK_METADATA_REQUIREMENTS": {
        "handler": check_metadata_requirements,
        "priority": "HIGH",
        "timeout": 300,
        "rollback": True,
        "description": "Validates and enforces file metadata requirements"
    }
}
```

### Safety and Reliability Features
- **Timeout Management**: All commands have execution time limits
- **Resource Monitoring**: CPU and memory usage tracked during execution
- **Circuit Breaker Pattern**: Failed commands prevent further execution until reset
- **Rollback Mechanisms**: Failed commands can trigger system rollback
- **Audit Trail**: Complete record of command execution for debugging

### Integration Patterns
- **Envelope Integration**: Commands carried in hints envelopes
- **Pipeline Integration**: Automatic command execution at pipeline stages
- **Error Handling**: Imperative commands issued on error conditions
- **Quality Gates**: Commands enforce quality requirements

### Command Categories and Examples

#### System Safety
- **ABORT_IF_CRITICAL_ISSUES**: Emergency pipeline termination
- **VALIDATE_SYSTEM_HEALTH**: Comprehensive system validation
- **ENFORCE_SAFETY_PROTOCOLS**: Safety mechanism activation

#### Governance Enforcement
- **ENFORCE_PROJECT_GOVERNANCE**: Governance rule execution
- **CHECK_COMPLIANCE_REQUIREMENTS**: Compliance validation
- **VALIDATE_ARCHITECTURAL_CONSTRAINTS**: Architecture rule enforcement

#### Quality Assurance
- **CHECK_METADATA_REQUIREMENTS**: Metadata validation
- **VALIDATE_CODE_QUALITY**: Code quality enforcement
- **ENFORCE_TESTING_REQUIREMENTS**: Testing standard enforcement

## Notes

### Future Enhancements
- **Command Analytics**: Analysis of command usage patterns and effectiveness
- **Dynamic Commands**: Runtime command generation based on system state
- **Cross-System Commands**: Commands that span multiple systems
- **AI-Generated Commands**: ML-driven command optimization

### Command Extensions
Future imperative commands could include:
- **EMERGENCY_SYSTEM_SHUTDOWN**: Controlled system shutdown procedures
- **DATA_CORRUPTION_RECOVERY**: Automated data recovery protocols
- **SECURITY_INCIDENT_RESPONSE**: Automated security incident handling
- **PERFORMANCE_DEGRADATION_MITIGATION**: Automated performance optimization

### Success Metrics
- **Command Success Rate**: >99.9% successful execution of imperative commands
- **Execution Time**: <5 seconds average for critical commands
- **False Abort Rate**: <0.1% incorrect pipeline aborts
- **Audit Completeness**: 100% command execution logging

---

**Implementation**: Complete imperative command protocol with 6 core commands
**Date**: [Current Date]
**Status**: Accepted and implemented
