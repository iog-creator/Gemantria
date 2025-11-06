# 🏗️ **Project Master Plan** - [PROJECT_NAME]

> **Template Version**: PMS v2.0
> **Created**: [DATE]
> **Purpose**: Complete governance specification for [PROJECT_NAME] using Project Management System

## 🎯 **Project Overview**

### **Mission Statement**
[Describe the core purpose and value proposition of this project]

### **Success Criteria**
- [ ] [Measurable success metric 1]
- [ ] [Measurable success metric 2]
- [ ] [Measurable success metric 3]

### **Technical Stack**
- **Primary Language**: [Python/Node.js/etc.]
- **Framework**: [Flask/React/etc.]
- **Infrastructure**: [AWS/GCP/etc.]
- **Database**: [PostgreSQL/MongoDB/etc.]

## 📋 **Critical Information Sources**

### **1. Hints Envelopes (Runtime Intelligence)**
- **Location**: `exports/*hints_envelope*.json`
- **Purpose**: Capture runtime decisions and enforce critical actions
- **Structure**:
```json
{
  "type": "hints_envelope",
  "version": "1.0",
  "items": ["hint1", "hint2"],
  "count": 2,
  "imperative_commands": [
    "AGENT_STOP_AND_PAY_ATTENTION",
    "CHECK_METADATA_REQUIREMENTS"
  ]
}
```

### **2. AGENTS.md Files (Plural Documentation)**
- **Required Files**:
  - `AGENTS.md` (root governance)
  - `docs/AGENTS.md` (documentation governance)
  - `src/AGENTS.md` (source code governance)
  - `src/[submodule]/AGENTS.md` (per-module governance)
- **Purpose**: Decentralized governance documentation
- **Auto-sync**: `make share.sync`

### **3. .mdc Rules (Cursor Rules)**
- **Location**: `.cursor/rules/*.mdc`
- **Purpose**: IDE-level governance enforcement
- **Examples**:
  - `001-project-safety.mdc`
  - `002-code-quality.mdc`
  - `003-deployment-rules.mdc`

## 🏛️ **Governance Structure**

### **Core Rules**
1. **Rule 001**: [Safety/critical requirement]
2. **Rule 002**: [Quality standard]
3. **Rule 003**: [Process requirement]

### **Enforcement Levels**
- **CRITICAL**: Pipeline abort if violated
- **HIGH**: PR block if violated
- **MEDIUM**: Warning + manual review
- **LOW**: Advisory only

## 🚀 **Project Phases**

### **Phase 1: Foundation** [Week 1-2]
- [ ] PMS deployment complete
- [ ] Core directory structure
- [ ] Basic CI/CD pipeline
- [ ] Initial AGENTS.md files

### **Phase 2: Development** [Week 3-8]
- [ ] Core functionality implemented
- [ ] Testing framework established
- [ ] Documentation synchronized
- [ ] Performance benchmarks

### **Phase 3: Production** [Week 9-12]
- [ ] Production deployment
- [ ] Monitoring/alerting
- [ ] User acceptance testing
- [ ] Final governance audit

## 🔧 **Technical Architecture**

### **Directory Structure**
```
[project-name]/
├── .cursor/rules/           # Cursor governance rules
├── docs/                    # Documentation
│   ├── ADRs/               # Architecture decisions
│   ├── SSOT/               # Single source of truth
│   └── AGENTS.md           # Docs governance
├── src/                     # Source code
│   ├── core/               # Core business logic
│   ├── services/           # External integrations
│   ├── utils/              # Utilities
│   └── AGENTS.md           # Source governance
├── tests/                   # Test suite
├── scripts/                 # Automation scripts
├── pms/                     # PMS system files
├── AGENTS.md               # Root governance
└── PROJECT_MASTER_PLAN.md  # This file
```

### **CI/CD Pipeline**
- **Lint**: `ruff check . && ruff format --check .`
- **Test**: `pytest --cov=. --cov-fail-under=90`
- **Security**: [Security scanning tool]
- **Deploy**: [Deployment strategy]

## 👥 **Team Roles & Responsibilities**

### **Technical Lead**
- **Responsibilities**:
  - Architecture decisions
  - Code review gatekeeper
  - PMS maintenance

### **Developers**
- **Responsibilities**:
  - Feature implementation
  - Test coverage
  - Documentation updates

### **QA/Test**
- **Responsibilities**:
  - Test automation
  - Quality gate enforcement
  - Bug triage

## 📊 **Quality Gates**

### **Code Quality**
- **Coverage**: ≥90%
- **Complexity**: ≤10 cyclomatic complexity
- **Duplication**: ≤2%
- **Security**: Zero critical/high vulnerabilities

### **Documentation**
- **Completeness**: 100% API documentation
- **Accuracy**: Documentation matches implementation
- **Accessibility**: Clear for all team members

### **Performance**
- **Latency**: [Response time requirements]
- **Throughput**: [Requests per second]
- **Resource Usage**: [CPU/memory limits]

## 🚨 **Risk Management**

### **Technical Risks**
- **Risk**: [Description]
  - **Probability**: High/Medium/Low
  - **Impact**: High/Medium/Low
  - **Mitigation**: [Strategy]

### **Project Risks**
- **Risk**: [Description]
  - **Probability**: High/Medium/Low
  - **Impact**: High/Medium/Low
  - **Mitigation**: [Strategy]

## 📈 **Success Metrics**

### **Quantitative Metrics**
- **Code Coverage**: Target 90%+
- **Build Success Rate**: Target 95%+
- **Mean Time to Resolution**: Target <4 hours
- **Deployment Frequency**: Target weekly

### **Qualitative Metrics**
- **Team Satisfaction**: Measured via surveys
- **Code Review Quality**: Measured via checklists
- **Documentation Quality**: Measured via audits
- **Process Efficiency**: Measured via retrospectives

## 🔄 **Continuous Improvement**

### **Regular Activities**
- **Daily**: Standup meetings
- **Weekly**: Code reviews, metrics review
- **Monthly**: Retrospective, planning
- **Quarterly**: Architecture review, roadmap update

### **Feedback Loops**
- **Immediate**: Code review feedback
- **Short-term**: Sprint retrospectives
- **Long-term**: Annual surveys, architecture reviews

---

## 📝 **PMS Implementation Checklist**

### **Phase 1: Setup** ✅
- [ ] PMS deployment script run
- [ ] Directory structure created
- [ ] Initial AGENTS.md files created
- [ ] Basic CI pipeline configured

### **Phase 2: Governance** ✅
- [ ] Core rules defined (.mdc files)
- [ ] Envelope system tested
- [ ] Metadata enforcement working
- [ ] Housekeeping automation active

### **Phase 3: Operations** ⏳
- [ ] Full pipeline tested
- [ ] Documentation synchronized
- [ ] Team trained on PMS
- [ ] Monitoring/alerting configured

---

**Template adapted from PMS v2.0 Specification**
**Last Updated**: [DATE]
**PMS Version**: 2.0
