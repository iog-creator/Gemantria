# 🏗️ PMS Deployment Guide

**Complete guide to deploying the Project Management System (PMS) in any Cursor workspace.**

## 📋 Prerequisites

- **Git repository** initialized
- **Python 3.8+** installed
- **Virtual environment** (recommended)
- **Cursor IDE** (optional but recommended)

## 🚀 Quick Start (5 minutes)

### Step 1: Copy PMS to Your Project

```bash
# Option A: Copy from existing project
cp -r /path/to/source/project/pms ./pms

# Option B: Download from template
# (PMS templates will be available in a separate repository)
```

### Step 2: Initialize PMS

```bash
# Make deployment script executable
chmod +x pms/scripts/deploy.sh

# Run initialization
./pms/scripts/deploy.sh
```

### Step 3: Create Project Master Plan

```bash
# Copy template
cp pms/templates/PROJECT_MASTER_PLAN.template.md PROJECT_MASTER_PLAN.md

# Edit for your project
cursor PROJECT_MASTER_PLAN.md  # or your preferred editor
```

### Step 4: First Validation

```bash
# Include PMS targets in Makefile
echo "include pms/templates/Makefile.pms" >> Makefile

# Validate PMS installation
make pms.validate
```

## 📁 Directory Structure After Deployment

```
your-project/
├── .cursor/rules/           # Project governance rules (.mdc files)
├── docs/                    # Documentation
│   ├── ADRs/               # Architecture decisions
│   ├── SSOT/               # Single source of truth
│   └── AGENTS.md           # Documentation governance
├── src/                     # Source code
│   ├── core/               # Core business logic
│   ├── services/           # External integrations
│   └── AGENTS.md           # Source code governance
├── exports/                 # Generated artifacts
│   └── *hints_envelope*.json # Runtime intelligence
├── pms/                     # PMS system files
│   ├── core/               # Core PMS components
│   ├── scripts/            # PMS automation scripts
│   ├── templates/          # Project templates
│   └── docs/               # PMS documentation
├── AGENTS.md               # Root project governance
├── PROJECT_MASTER_PLAN.md  # Project specification
└── Makefile               # Build targets (includes PMS)
```

## ⚙️ Detailed Setup

### 1. Governance Files Setup

Create the required AGENTS.md files:

```bash
# Root governance
cp pms/templates/AGENTS.md.template AGENTS.md

# Source governance
cp pms/templates/AGENTS.md.template src/AGENTS.md

# Documentation governance
cp pms/templates/AGENTS.md.template docs/AGENTS.md
```

### 2. Cursor Rules Setup

```bash
# Create rules directory
mkdir -p .cursor/rules

# Copy example rules
cp pms/templates/example-rules.mdc .cursor/rules/

# Split into individual .mdc files (edit as needed)
# Each rule should be in its own .mdc file
```

### 3. Makefile Integration

```bash
# Add to your Makefile
cat >> Makefile << 'EOF'

# Include PMS targets
include pms/templates/Makefile.pms

# Your existing targets...
EOF
```

### 4. CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/ci.yml
- name: Validate PMS
  run: |
    source .venv/bin/activate
    make pms.validate

- name: Run Housekeeping
  run: |
    source .venv/bin/activate
    make housekeeping
```

## 🧪 Testing PMS Installation

### Run Full Test Suite

```bash
# Run PMS component tests
python pms/scripts/test_pms.py

# Validate system health
make pms.validate

# Check system status
make pms.status
```

### Manual Verification

```bash
# Check directory structure
find . -name "AGENTS.md" | sort

# Check rules
find .cursor/rules -name "*.mdc" | sort

# Check envelopes
find exports -name "*hints_envelope*.json" 2>/dev/null || echo "No envelopes yet"
```

## 🏛️ Governance Activation

### 1. Define Core Rules

Edit `.cursor/rules/` files to define your project's governance:

- **001-project-safety.mdc**: Security and safety requirements
- **002-code-quality.mdc**: Code quality standards
- **003-deployment-rules.mdc**: Deployment and operations rules

### 2. Set Up Quality Gates

```bash
# Add to CI pipeline
make quality.gate    # Run all quality checks
make quality.fix     # Auto-fix issues where possible
```

### 3. Enable Housekeeping

```bash
# Run daily/weekly
make housekeeping

# Or individual components
make rules.audit
make docs.sync
make envelope.process
```

## 📬 Hints Envelope System

### Creating Envelopes

Envelopes are created automatically by the pipeline, but you can create them manually:

```bash
# Create test envelope
make envelope.create-test

# Process pending envelopes
make envelope.process
```

### Envelope Commands

Envelopes can contain imperative commands that agents **must** execute:

```json
{
  "type": "hints_envelope",
  "version": "1.0",
  "imperative_commands": [
    "AGENT_STOP_AND_PAY_ATTENTION",
    "CHECK_METADATA_REQUIREMENTS",
    "ENFORCE_PROJECT_GOVERNANCE"
  ]
}
```

## 🔧 Customization

### Adapting for Your Project

1. **Edit PROJECT_MASTER_PLAN.md** with your project details
2. **Customize .mdc rules** in `.cursor/rules/`
3. **Modify AGENTS.md files** for your team structure
4. **Add project-specific make targets** to Makefile

### Extending PMS

- **Add new envelope commands** in `envelope_error_system.py`
- **Create project-specific rules** as new .mdc files
- **Extend validation** in `validate_pms.py`
- **Add automation** in PMS scripts

## 🚨 Troubleshooting

### Common Issues

**PMS validation fails:**
```bash
make pms.validate  # See detailed error messages
```

**Missing AGENTS.md files:**
```bash
# Check which are missing
find . -name "AGENTS.md" | sort
# Copy from template
cp pms/templates/AGENTS.md.template docs/AGENTS.md
```

**Rules not enforced:**
```bash
# Check .mdc files
find .cursor/rules -name "*.mdc"
# Validate syntax
make rules.validate
```

### Getting Help

1. **Check PMS documentation**: `pms/docs/`
2. **Run diagnostics**: `make pms.status`
3. **Validate components**: `python pms/scripts/test_pms.py`
4. **Check logs**: Look for hints envelopes in `exports/`

## 📈 Maintenance

### Regular Tasks

- **Daily**: `make housekeeping`
- **Weekly**: Review hints envelopes, update rules
- **Monthly**: Full system audit, update PMS version

### Updates

```bash
# Update PMS system
make pms.update

# Backup configuration
make pms.backup

# Restore if needed
make pms.restore
```

## 🎯 Success Metrics

Your PMS is working when:

- ✅ **3 critical information sources** are active
- ✅ **Housekeeping runs cleanly** daily
- ✅ **Quality gates pass** consistently
- ✅ **Envelope system** processes hints automatically
- ✅ **Metadata enforcement** works on all files
- ✅ **Governance rules** are followed automatically

## 📞 Support

- **Documentation**: `pms/docs/`
- **Tests**: `python pms/scripts/test_pms.py`
- **Validation**: `make pms.validate`
- **Status**: `make pms.status`
