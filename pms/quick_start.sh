#!/bin/bash
# PMS Quick Start Script - One-command PMS deployment

set -e  # Exit on any error

echo "🚀 PMS Quick Start - Deploying Project Management System"
echo "======================================================"

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Aborting."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed. Aborting."
    exit 1
fi

if [ ! -d ".git" ]; then
    echo "❌ Must be run from a git repository root. Aborting."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Step 1: Copy PMS system (if not already present)
if [ ! -d "pms" ]; then
    echo "📦 Setting up PMS system..."

    # For this demo, we'll assume PMS is already in the directory
    # In production, this would download from a repository
    if [ ! -d "pms" ]; then
        echo "❌ PMS system not found. Please ensure PMS files are available."
        exit 1
    fi
else
    echo "✅ PMS system already present"
fi

# Step 2: Make scripts executable
echo "🔧 Setting script permissions..."
chmod +x pms/scripts/*.py pms/scripts/*.sh 2>/dev/null || true
chmod +x pms/*.sh 2>/dev/null || true

# Step 3: Initialize PMS
echo "🏗️ Initializing PMS..."
python3 pms/scripts/pms_init.py

# Step 4: Create project master plan
if [ ! -f "PROJECT_MASTER_PLAN.md" ]; then
    echo "📋 Creating project master plan template..."
    cp pms/templates/PROJECT_MASTER_PLAN.template.md PROJECT_MASTER_PLAN.md
    echo "✏️  Please edit PROJECT_MASTER_PLAN.md with your project details"
fi

# Step 5: Set up governance files
echo "📝 Setting up governance files..."
for file in "AGENTS.md" "docs/AGENTS.md" "src/AGENTS.md"; do
    if [ ! -f "$file" ]; then
        mkdir -p "$(dirname "$file")"
        cp pms/templates/AGENTS.md.template "$file"
        echo "  Created: $file"
    fi
done

# Step 6: Set up Cursor rules
echo "📏 Setting up Cursor rules..."
mkdir -p .cursor/rules
if [ ! -f ".cursor/rules/001-project-safety.mdc" ]; then
    cp pms/templates/example-rules.mdc .cursor/rules/
    echo "  Copied example rules (please customize)"
fi

# Step 7: Set up Makefile
echo "🔨 Setting up Makefile..."
if [ ! -f "Makefile" ]; then
    cat > Makefile << 'EOF'
# Project Makefile
include pms/templates/Makefile.pms

# Add your custom targets here
EOF
    echo "  Created: Makefile"
elif ! grep -q "include pms/templates/Makefile.pms" Makefile; then
    echo "include pms/templates/Makefile.pms" >> Makefile
    echo "  Updated: Makefile (added PMS include)"
fi

# Step 8: Create exports directory
echo "📤 Setting up exports directory..."
mkdir -p exports

# Step 9: Validate installation
echo "🔍 Validating PMS installation..."
if python3 pms/scripts/validate_pms.py; then
    echo "✅ PMS validation passed!"
else
    echo "⚠️  PMS validation found issues (this is normal for initial setup)"
    echo "   Run 'python3 pms/scripts/pms_recover.py' to fix automatically"
fi

# Step 10: Show next steps
echo ""
echo "🎉 PMS Quick Start Complete!"
echo "============================"
echo ""
echo "Next steps:"
echo "1. Edit PROJECT_MASTER_PLAN.md with your project details"
echo "2. Customize .cursor/rules/*.mdc files for your project"
echo "3. Update AGENTS.md files with your team structure"
echo "4. Run 'make housekeeping' regularly"
echo "5. Use 'make pms.status' to check system health"
echo ""
echo "Available commands:"
echo "  make pms.validate     - Validate PMS system"
echo "  make housekeeping      - Run complete housekeeping"
echo "  make envelope.process  - Process hints envelopes"
echo "  make rules.audit       - Audit project rules"
echo "  make pms.help          - Show all PMS commands"
echo ""
echo "Documentation:"
echo "  pms/docs/PMS_README.md"
echo "  pms/docs/PMS_DEPLOYMENT_GUIDE.md"
echo "  pms/docs/PROJECT_MANAGEMENT_SYSTEM_SPEC.md"
echo ""
echo "🚀 Happy coding with PMS!"
