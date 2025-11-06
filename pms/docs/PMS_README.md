# 🏗️ Project Management System (PMS) v2.0

**Reproducible, robust project management for any Cursor workspace**

## 🎯 What is PMS?

PMS is a complete project management system that provides **3 critical information sources** and **automated governance** to prevent project drift and maintain quality. It's designed to be deployed in any project with just a master plan.

## 📋 3 Critical Information Sources

### 1. **Hints Envelopes** (Runtime Intelligence)
- Capture runtime intelligence and enforce imperative actions
- Agents **cannot ignore** the commands - they must execute them
- Structure:
```json
{
  "type": "hints_envelope",
  "version": "1.0",
  "imperative_commands": [
    "AGENT_STOP_AND_PAY_ATTENTION",
    "CHECK_METADATA_REQUIREMENTS",
    "VALIDATE_ENVELOPE_CONTENTS"
  ],
  "enforcement_level": "CRITICAL",
  "ignore_risk": "PIPELINE_ABORT"
}
```

### 2. **AGENTS.md Files** (Plural Documentation)
- Directory-specific documentation with Related ADRs tables
- Required locations: `src/services/AGENTS.md`, `webui/*/AGENTS.md`, etc.
- Automatic maintenance and enforcement

### 3. **.mdc Rules** (Governance Constraints)
- Cursor workspace rules that enforce project standards
- Categories: DB safety, code quality, documentation sync, process enforcement
- Automatic auditing and compliance checking

## 🚀 Quick Start

### Step 1: Create Your Master Plan

Create `PROJECT_MASTER_PLAN.md` in your project root:

```markdown
# My Awesome Project

## Project Overview
[Describe what you're building and why]

## Technology Stack
- Backend: [frameworks, languages]
- Frontend: [frameworks, libraries]
- Database: [type, schema approach]

## Key Components
[List main architectural elements]

## Development Workflow
[How your team works - branching, reviews, deployment]

## Quality Gates
[What must pass before merging - tests, reviews, etc.]
```

### Step 2: Deploy PMS

Run the deployment script:

```bash
# Download and run the PMS deployment
curl -fsSL https://raw.githubusercontent.com/your-repo/pms/main/pms_deploy.sh | bash

# Or if you have the files locally:
./pms_deploy.sh
```

### Step 3: Start Development

```bash
# After any changes
make housekeeping

# Check metadata compliance
make metadata-check

# Process hints envelopes
make envelope-process
```

## 🛠️ Core Components

### **Envelope Processor** (`scripts/envelope_processor.py`)
- Processes hints envelopes with imperative commands
- Cannot be ignored - enforces critical actions
- Supports commands like `CHECK_METADATA_REQUIREMENTS`

### **Metadata Enforcement** (`scripts/enforce_metadata.py`)
- Automatically adds required metadata to Python files
- Checks `src/` and `scripts/` directories
- Adds Related Rules/ADRs docstrings

### **Rules Audit** (`scripts/rules_audit.py`)
- Validates .mdc rule numbering and completeness
- Updates AGENTS.md with rules inventory
- Ensures governance compliance

### **PMS Init** (`scripts/pms_init.py`)
- Deploys complete PMS system from master plan
- Creates directory structure and initial files
- Sets up Cursor rules and documentation

## 📁 Directory Structure

```
project/
├── PROJECT_MASTER_PLAN.md           # SSOT for project requirements
├── AGENTS.md                        # Main project documentation
├── Makefile                         # All PMS operations
├── PROJECT_MANAGEMENT_SYSTEM_SPEC.md # PMS specification
├── pms_deploy.sh                    # Deployment script
├── .cursor/
│   └── rules/                       # .mdc rule files
├── scripts/
│   ├── envelope_processor.py        # Envelope handling
│   ├── enforce_metadata.py          # Metadata enforcement
│   ├── rules_audit.py              # Rules compliance
│   └── pms_init.py                 # PMS initialization
├── src/
│   ├── services/
│   │   └── AGENTS.md               # Service documentation
│   └── [modules]/
│       └── AGENTS.md               # Module documentation
├── docs/
│   ├── ADRs/                       # Architecture decisions
│   ├── SSOT/                       # Single source of truth
│   └── forest/                     # Documentation index
├── share/                           # Synchronized artifacts
└── exports/                         # Pipeline outputs
```

## 📝 Makefile Targets

```makefile
# Core PMS operations
make housekeeping         # Auto-housekeeping after changes
make metadata-check       # Verify metadata requirements
make envelope-process     # Process hints envelopes
make agentmd-sync         # Sync AGENTS.md to Cursor rules
make pms-health-check     # Verify PMS is working

# Development workflow
make setup               # Initial project setup
make gates               # Quality gates and validation
make share-sync          # Sync share directory
```

## 🛡️ Governance Principles

### **Non-Negotiables for Cursor**
1. **Master Plan is Law** - `PROJECT_MASTER_PLAN.md` overrides all guidance
2. **Makefile Targets Only** - Never invent commands, use provided targets
3. **Envelope Errors Block** - Stop immediately on envelope errors
4. **Auto-Housekeeping** - Run `make housekeeping` after any changes
5. **Metadata Required** - All Python files need Related Rules/ADRs
6. **AGENTS.md Sync** - Always run `make agentmd-sync` after changes

### **Envelope Error System**
```python
# Critical envelope errors that cannot be ignored
{
  "status": "error",
  "error": {
    "code": "METADATA_REQUIREMENTS_FAILED",
    "message": "Files missing required metadata",
    "fix_command": "python scripts/enforce_metadata.py --fix"
  }
}
```

## ⚡ Gotchas & Auto-Fixes

### **Silent Success While Tests Fail**
- **Auto-Fix**: `make gates` after any changes
- **Prevention**: Gates run automatically in housekeeping

### **AGENTS.md Rules Drift**
- **Auto-Fix**: `make agentmd-sync` after AGENTS.md changes
- **Prevention**: Rules audit in housekeeping

### **Missing Metadata on Files**
- **Auto-Fix**: `make metadata-check` runs enforcement
- **Prevention**: Envelope processing triggers checks

### **Unprocessed Hints Envelopes**
- **Auto-Fix**: `make envelope-process` in housekeeping
- **Prevention**: Pipeline automatically processes envelopes

## 🎯 Success Metrics

- ✅ **100% metadata compliance** on Python files
- ✅ **0 envelope errors** in normal operation
- ✅ **AGENTS.md ↔ .cursor/rules** always synchronized
- ✅ **Housekeeping runs** after every change
- ✅ **Envelope processing** is automatic and reliable

## 🔄 Customization

### **Adapting for Your Project**

1. **Edit `PROJECT_MASTER_PLAN.md`** with your specific requirements
2. **Customize AGENTS.md files** for your directory structure
3. **Add project-specific rules** in `.cursor/rules/`
4. **Extend Makefile targets** for your workflow
5. **Configure envelope commands** for your needs

### **Extending PMS**

- **Add new envelope commands** in `envelope_processor.py`
- **Create custom rules** following the .mdc format
- **Extend metadata templates** in `enforce_metadata.py`
- **Add new housekeeping steps** to the Makefile

## 📚 Examples

### **Processing a Hints Envelope**
```bash
# Create test envelope
python scripts/envelope_processor.py --create-test-envelope

# Process all envelopes
make envelope-process
```

### **Checking Metadata**
```bash
# Check staged files
python scripts/enforce_metadata.py --staged

# Auto-fix missing metadata
python scripts/enforce_metadata.py --staged --fix
```

### **Rules Compliance**
```bash
# Audit all rules
python scripts/rules_audit.py

# Check specific rule
python scripts/rules_audit.py --rule 039
```

## 🔗 Integration

### **With Existing Projects**
- PMS can be deployed alongside existing code
- Master plan captures current project state
- Gradual adoption with `make pms-init`

### **With CI/CD**
```yaml
# GitHub Actions example
- name: PMS Housekeeping
  run: make housekeeping

- name: Metadata Check
  run: make metadata-check

- name: Envelope Processing
  run: make envelope-process
```

## 🤝 Contributing

### **Improving PMS**
1. **Follow the PMS process** - use `make housekeeping` after changes
2. **Update master plan** when adding features
3. **Test envelope processing** with `--create-test-envelope`
4. **Verify metadata enforcement** works correctly

### **Reporting Issues**
- Use envelope error format for PMS issues
- Include `PROJECT_MASTER_PLAN.md` when reporting
- Run `make pms-health-check` before submitting

---

## 📋 Checklist

- [ ] Created `PROJECT_MASTER_PLAN.md`
- [ ] Ran `./pms_deploy.sh`
- [ ] Reviewed generated files
- [ ] Tested `make housekeeping`
- [ ] Verified envelope processing works
- [ ] Confirmed metadata enforcement
- [ ] Ready for development!

**Remember**: PMS focuses on **building what works** and **enforcing what matters**. It handles governance so you can focus on building great software.
