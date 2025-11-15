# StoryMaker Project Documentation

## Quick Start Guide

### **One-Command Setup**
```bash
git clone https://github.com/iog-creator/storymaker-bundle-v1.6.git
cd storymaker-bundle-v1.6-unified-full
make bootstrap
```

**That's it!** The system automatically:
- ✅ Sets up environment and configuration
- ✅ Starts all infrastructure (Docker services)
- ✅ Detects and integrates with LM Studio
- ✅ Initializes AgentPM workspace
- ✅ Syncs rules and enforces guardrails
- ✅ Verifies everything is working

### **Start Using StoryMaker**
```bash
# Start all services
make start

# Check status
make status

# Launch live monitoring dashboard
make ui.live
```

### **Access StoryMaker**
- **Web UI**: http://localhost:3000
- **API**: http://localhost:8000-8004
- **Live Dashboard**: `make ui.live` (real-time monitoring)
- **Verification**: `make verify-all`

## System Architecture

### Service Architecture
- **worldcore** (port 8000): World building and lore
- **narrative** (port 8001): Story generation and plot
- **screenplay** (port 8002): Script formatting and dialogue
- **media** (port 8003): Images and multimedia
- **interact** (port 8004): User interactions and chat

### Directory Structure
```
storymaker-bundle-v1.6-unified-full/
├── services/
│   ├── narrative/          # Creative generation (Groq)
│   ├── worldcore/          # QA/Retrieval (LM Studio)
│   ├── orchestration/      # Graph host
│   └── ...
├── apps/
│   └── webui/              # Frontend React app
├── ci/                     # Guards and validation
└── docs/                   # SSOT/documentation
```

## SSOT v1.2 Requirements

- **Envelope v1.2 mandatory** - all responses must include `status`, `data`, `error`, `meta`, `proof`
- **Proof SHA256 validation** - `proof.sha256` must match canonicalized response
- **Provider isolation** - Groq for creative, LM Studio for QA/retrieval
- **Model lock** - exact model IDs required and validated
- **QA validation** - non-empty analysis required, `latency_ms > 0`

## Environment Setup

```bash
# Groq (Creative Generation)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# LM Studio (QA & Retrieval)
OPENAI_API_BASE=http://127.0.0.1:1234/v1
OPENAI_API_KEY=lm-studio
CHAT_MODEL_PRIMARY=qwen/qwen3-8b
CHAT_MODEL_REASON=qwen/qwen3-4b-thinking-2507
RERANKER_MODEL=qwen.qwen3-reranker-0.6b
EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
EMBEDDING_DIMS=1024

# Production Controls
DISABLE_MOCKS=1
MOCK_LMS=0
REDIS_URL=redis://localhost:6380
```

## Live Monitoring Dashboard

The live dashboard provides real-time visual monitoring of all StoryMaker systems:

```bash
# Launch live dashboard
make ui.live
# Press 'q' to exit
```

**Dashboard Features:**
- **8 monitoring tiles** with 1-second refresh
- **Color-coded status**: Green (healthy), Yellow (warnings), Red (errors)
- **Live file watching** with blinking indicators on changes
- **Real-time guard execution** showing pass/fail status
- **Service health checks** for LM Studio and Groq
- **Proof statistics** and document change tracking

**Monitored Systems:**
- LM Studio (health + model info)
- Groq (environment validation)
- AgentPM (SSOT document changes)
- StoryMaker (implementation status)
- SSOT Rules (.mdc file count)
- Envelopes & Proofs (statistics + age)
- Docs Autosync (canonicalization status)
- Rerank & QA Guards (live execution results)

## Quick Verify

```bash
make -s rules.emit && make -s guards
```

## Global Defaults

- Envelope v1.2 + `proof.sha256` required
- Provider split enforced (Groq vs LM Studio)
- `/api/v1/*` endpoints only

## Troubleshooting

### "Bootstrap failed"
- Check Docker is running: `docker ps`
- Verify internet connection for model downloads
- Run `make bootstrap` again (idempotent)

### "LM Studio not found"
- Download from [lmstudio.ai](https://lmstudio.ai)
- Load Qwen chat + embedding models
- Start server on port 1234
- System works without LM Studio but with limited AI features

### "Database connection failed"
- Run: `docker compose up -d db redis minio`
- Check services: `docker compose ps`

### "Services won't start"
- Run: `make restart`
- Check logs: `docker compose logs`

### "Dashboard won't start"
- Install Node.js: `curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs`
- Run: `make ui.install` to install dependencies
- Check: `node --version` and `npm --version`

## Need Help?

Run `make help` to see all available commands.

