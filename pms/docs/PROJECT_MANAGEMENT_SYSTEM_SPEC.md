# 🏗️ **Project Management System (PMS) Specification v2.0**

> **Purpose**: Generic, reproducible project management system that can be deployed in any Cursor workspace. Provides robust governance through 3 critical information sources and automated enforcement mechanisms.

## 🎯 **Core Philosophy**

**"Build what works, enforce what matters"** - Focus on proven patterns that prevent project drift and maintain quality without over-engineering.

## 📋 **3 Critical Information Sources**

### 1. **Hints Envelopes** (Runtime Intelligence)
- **Purpose**: Capture runtime intelligence and enforce imperative actions
- **Structure**:
```json
{
  "type": "hints_envelope",
  "version": "1.0",
  "items": ["hint1", "hint2"],
  "count": 2,
  "imperative_commands": [
    "AGENT_STOP_AND_PAY_ATTENTION",
    "PROCESS_HINTS_ENVELOPE_IMMEDIATELY",
    "CHECK_METADATA_REQUIREMENTS",
    "VALIDATE_ENVELOPE_CONTENTS"
  ],
  "enforcement_level": "CRITICAL",
  "ignore_risk": "PIPELINE_ABORT"
}
```

### 2. **AGENTS.md Files** (Plural Documentation)
- **Purpose**: Directory-specific documentation with Related ADRs table
- **Required Locations**:
  - `src/services/AGENTS.md` - Service layer integrations
  - `webui/*/AGENTS.md` - UI component documentation
  - `src/*/AGENTS.md` - Source module documentation
- **Structure**:
```markdown
# AGENTS.md - [Directory Name]

## Directory Purpose
[Purpose description]

## Key Components
[Component documentation]

## Related ADRs
| Component/Function | Related ADRs |
|-------------------|--------------|
| component1 | ADR-001, ADR-002 |
```

### 3. **.mdc Rules** (Governance Constraints)
- **Purpose**: Cursor workspace rules that enforce project standards
- **Structure**: `.cursor/rules/[NNN]-[title].mdc` files
- **Categories**:
  - DB safety and SQL discipline
  - Code quality and formatting
  - Documentation synchronization
  - Process enforcement

## 🛠️ **Core Components**

### **Master Plan Structure**
```
PROJECT_MASTER_PLAN.md
├── Executive Summary
├── Non-Negotiables for Cursor
├── Gotchas & Auto-Fixes
├── Safe Defaults
├── Cursor Runbook
├── Makefile Targets
└── Project-Specific Configuration
```

### **Makefile Target System**
```makefile
# Core targets that Cursor must use
setup:                # Initial project setup
agentmd-sync:         # Sync AGENTS.md → .cursor/rules
gates:                # Quality gates and validation
housekeeping:         # Auto-housekeeping (rules audit, share sync, forest)
metadata-check:       # Verify metadata requirements
envelope-process:     # Process hints envelopes
```

### **Envelope Error System**
```python
# Envelope errors that Cursor cannot ignore
{
  "status": "error",
  "error": {
    "code": "METADATA_REQUIREMENTS_FAILED",
    "message": "Files missing required metadata",
    "files": ["src/module.py"],
    "fix_command": "python scripts/enforce_metadata.py --fix"
  }
}
```

## 🚀 **Cursor Setup Instructions**

### **Step 1: Project Initialization**
```bash
# 1. Create project with master plan
echo "PROJECT_MASTER_PLAN.md" > .project_plan

# 2. Initialize PMS
make pms-init

# 3. Setup Cursor rules
make agentmd-init && make agentmd-sync

# 4. Verify system health
make pms-health-check
```

### **Step 2: Daily Development Workflow**
```bash
# Before coding
make pms-preflight

# After changes
make housekeeping

# Before commit
make gates

# Process any envelope errors
make envelope-process
```

## 📁 **Directory Structure Template**

```
project/
├── PROJECT_MASTER_PLAN.md           # SSOT for project requirements
├── AGENTS.md                        # Main project documentation
├── Makefile                         # All Cursor operations
├── .cursor/
│   └── rules/                       # .mdc rule files
├── scripts/
│   ├── enforce_metadata.py          # Metadata enforcement
│   ├── create_agents_md.py          # AGENTS.md management
│   ├── rules_audit.py              # Rules compliance
│   └── envelope_processor.py        # Envelope handling
├── src/
│   ├── services/
│   │   └── AGENTS.md               # Service documentation
│   └── [modules]/
│       └── AGENTS.md               # Module documentation
├── docs/
│   ├── ADRs/                       # Architecture decisions
│   ├── SSOT/                       # Single source of truth docs
│   └── forest/                     # Documentation index
├── share/                           # Synchronized artifacts
└── [project-specific]/             # Project code
    └── AGENTS.md                   # Component documentation
```

## 🔧 **Automated Scripts**

### **Metadata Enforcement (`scripts/enforce_metadata.py`)**
```python
#!/usr/bin/env python3
"""
Automated metadata enforcement for touched files.
Checks files for required metadata and adds it when missing.
Called automatically from hints envelopes.
"""

def enforce_metadata():
    # Check all Python files in src/, scripts/
    # Add missing metadata with Related Rules/ADRs
    # Report violations as envelope errors
    pass
```

### **AGENTS.md Management (`scripts/create_agents_md.py`)**
```python
#!/usr/bin/env python3
"""
Create missing AGENTS.md files in required directories.
Ensures all required locations have proper documentation.
"""

def create_missing_agents_md():
    # Find directories missing AGENTS.md
    # Create with proper Related ADRs table
    # Exclude cache/special directories
    pass
```

### **Envelope Processor (`scripts/envelope_processor.py`)**
```python
#!/usr/bin/env python3
"""
Process hints envelopes and execute imperative commands.
Cannot be ignored - enforces critical actions.
"""

def process_envelope(envelope):
    # Execute imperative commands
    # CHECK_METADATA_REQUIREMENTS → run metadata enforcement
    # PROCESS_HINTS_ENVELOPE_IMMEDIATELY → immediate processing
    # Return success/failure status
    pass
```

## 📝 **Makefile Targets**

```makefile
# PMS Core Targets
pms-init:
	# Initialize PMS in new project
	@echo "Initializing Project Management System..."
	# Create directory structure
	# Setup basic configuration
	# Create initial AGENTS.md files

pms-health-check:
	# Verify PMS is working correctly
	@echo "Checking PMS health..."
	# Verify all scripts exist
	# Check metadata compliance
	# Validate envelope processing

agentmd-sync:
	# Sync AGENTS.md → .cursor/rules
	@echo "Syncing AGENTS.md to Cursor rules..."
	# Convert AGENTS.md content to .mdc files
	# Update .cursor/rules/ directory

housekeeping:
	# Auto-housekeeping (rules audit, share sync, forest)
	@echo "Running auto-housekeeping..."
	make rules-audit
	make share-sync
	make forest-generate

metadata-check:
	# Verify metadata requirements on touched files
	@echo "Checking metadata requirements..."
	python scripts/enforce_metadata.py --staged

envelope-process:
	# Process any pending hints envelopes
	@echo "Processing hints envelopes..."
	python scripts/envelope_processor.py --process-pending
```

## ⚡ **Gotchas & Auto-Fixes**

### **1. Silent Success While Tests Fail**
- **Detection**: Tests pass but gates fail
- **Auto-Fix**: `make gates` after any changes
- **Error**: `{"code": "GATES_RED"}`

### **2. AGENTS.md Rules Drift**
- **Detection**: `.cursor/rules/*.mdc` stale or missing
- **Auto-Fix**: `make agentmd-sync` after AGENTS.md changes
- **Error**: `{"code": "AGENTMD_RULES_STALE"}`

### **3. Missing Metadata on Touched Files**
- **Detection**: Python files without Related Rules/ADRs
- **Auto-Fix**: `make metadata-check` runs enforcement
- **Error**: `{"code": "METADATA_REQUIREMENTS_FAILED"}`

### **4. Unprocessed Hints Envelopes**
- **Detection**: Envelope files present but not processed
- **Auto-Fix**: `make envelope-process` in pipeline
- **Error**: `{"code": "ENVELOPES_UNPROCESSED"}`

## 🔒 **Non-Negotiables for Cursor**

1. **Master Plan is Law**: `PROJECT_MASTER_PLAN.md` overrides all other guidance
2. **Makefile Targets Only**: Never invent commands - use provided targets
3. **Envelope Errors Block**: Stop immediately on envelope errors
4. **Auto-Housekeeping**: Run `make housekeeping` after any changes
5. **Metadata Required**: All Python files need Related Rules/ADRs
6. **AGENTS.md Sync**: Always run `make agentmd-sync` after AGENTS.md changes

## 🎯 **Project-Specific Adaptation**

### **Step 1: Create Master Plan**
```markdown
# [PROJECT_NAME] Master Plan

## Project Overview
[Describe what you're building]

## Technology Stack
[Languages, frameworks, databases]

## Key Components
[Main architectural elements]

## Development Workflow
[How the team works]

## Quality Gates
[What must pass before merging]
```

### **Step 2: Initialize PMS**
```bash
# Deploy the PMS system
make pms-init PROJECT_PLAN=PROJECT_MASTER_PLAN.md

# Customize for your project
make pms-customize
```

### **Step 3: Verify Working**
```bash
# Run full system check
make pms-verify

# Test envelope processing
make envelope-process

# Verify metadata enforcement
make metadata-check
```

## 📊 **Success Metrics**

### **Process Compliance**
- ✅ 100% files have required metadata
- ✅ 0 envelope errors in pipeline
- ✅ AGENTS.md ↔ .cursor/rules always in sync
- ✅ Housekeeping runs after every change

### **Quality Gates**
- ✅ All Makefile targets work
- ✅ Scripts are idempotent
- ✅ Envelope processing is reliable
- ✅ Metadata enforcement is automatic

## 🔄 **Evolution Path**

### **Phase 1: Core PMS** (Current)
- Hints envelopes with imperative commands
- AGENTS.md plural with Related ADRs
- .mdc rules enforcement
- Automated housekeeping

### **Phase 2: Enhanced Intelligence**
- AI-powered metadata generation
- Predictive envelope suggestions
- Automated ADR creation
- Learning from project patterns

### **Phase 3: Multi-Project Orchestration**
- PMS instances across multiple projects
- Cross-project consistency enforcement
- Shared rule libraries
- Unified governance dashboard

---

## 📋 **Quick Start Checklist**

- [ ] Create `PROJECT_MASTER_PLAN.md`
- [ ] Run `make pms-init`
- [ ] Run `make agentmd-init && make agentmd-sync`
- [ ] Run `make pms-health-check`
- [ ] Start development with `make housekeeping`

**Remember**: The PMS is designed to be reliable and low-maintenance. Focus on building your project - the PMS handles the governance automatically.
