# Setup Guide: LM Studio & Database

This guide helps you get LM Studio and the database working for the Gemantria project.

## Quick Setup

Run the setup script to check your current configuration:

```bash
./scripts/setup_lm_studio_and_db.sh
```

## Step-by-Step Setup

### 1. Database Setup

#### Option A: Use Existing Postgres (Recommended)

If you have Postgres installed but not running:

**Linux (systemd):**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Auto-start on boot
```

**macOS (Homebrew):**
```bash
brew services start postgresql
```

**Docker:**
```bash
docker run -d --name postgres-gemantria \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=gematria \
  -p 5432:5432 \
  postgres:15
```

#### Option B: Configure Auto-Start

Add to your `.env` file:

```bash
# For systemd (Linux)
DB_START_CMD="sudo systemctl start postgresql"

# For Homebrew (macOS)
DB_START_CMD="brew services start postgresql"
```

#### Verify Database Connection

```bash
# Check if Postgres is running
pg_isready

# Test connection
pmagent health db
```

### 2. LM Studio Setup

#### Step 1: Install LM Studio

Download and install from [lmstudio.ai](https://lmstudio.ai)

#### Step 2: Install LM Studio CLI

The CLI is usually installed with LM Studio. Verify it's available:

```bash
which lms
# Should show: /home/youruser/.lmstudio/bin/lms

# If not in PATH, add it:
export PATH="$HOME/.lmstudio/bin:$PATH"
```

#### Step 3: Configure Environment Variables

Add to your `.env` file:

```bash
# Enable LM Studio
LM_STUDIO_ENABLED=1

# Base URL (default port is 1234)
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1

# Model name (must match a model you have in LM Studio)
LM_STUDIO_MODEL=christian-bible-expert-v2.0-12b

# Optional: API key (any non-empty string works for local servers)
LM_STUDIO_API_KEY=sk-local-placeholder
```

#### Step 4: Start LM Studio Server

**Option A: Using CLI (Recommended)**
```bash
# Start server on port 1234
lms server start --port 1234

# Or with GPU acceleration
lms server start --port 1234 --gpu=1.0
```

**Option B: Using GUI**
1. Open LM Studio
2. Go to Settings → Local Server
3. Click "Start Server"
4. Note the port (default: 1234)

#### Step 5: Load a Model

Models can be loaded automatically on first use, or you can pre-load:

**Using CLI:**
```bash
# List available models
lms ls

# Load a specific model
lms load christian-bible-expert-v2.0-12b
```

**Using GUI:**
1. Go to Models tab
2. Select a model
3. Click "Load Model"

#### Step 6: Verify LM Studio

```bash
# Check health
pmagent health lm

# Expected output:
# LM_HEALTH: mode=lm_ready (ok)
# {"ok": true, "mode": "lm_ready", ...}
```

### 3. Complete Configuration Example

Here's a complete `.env` configuration:

```bash
# Database
GEMATRIA_DSN=postgresql://mccoy@/gematria?host=/var/run/postgresql
BIBLE_DB_DSN=postgresql://postgres@/bible_db?host=/var/run/postgresql

# Auto-start Postgres (adjust for your system)
DB_START_CMD="sudo systemctl start postgresql"

# LM Studio
LM_STUDIO_ENABLED=1
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=christian-bible-expert-v2.0-12b
LM_STUDIO_API_KEY=sk-local-placeholder

# Model Configuration
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
MATH_MODEL=self-certainty-qwen3-1.7b-base-math
EMBEDDING_MODEL=text-embedding-bge-m3
RERANKER_MODEL=qwen.qwen3-reranker-0.6b

# Optional: Auto-load model on server start
LM_STUDIO_MODEL_ID=christian-bible-expert-v2.0-12b
LM_STUDIO_SERVER_PORT=1234
```

### 4. Test Everything

Run the Reality Check #1 script to test the complete setup:

```bash
pmagent reality-check 1
```

This will:
1. Check/start Postgres
2. Check/start LM Studio
3. Run doc ingestion
4. Answer a test question

Expected output:
```json
{
  "ok": true,
  "steps": {
    "postgres": {"ok": true, "reason": "..."},
    "lm_studio": {"ok": true, "reason": "..."},
    "ingest_docs": {"ok": true, "reason": "..."},
    "golden_question": {"ok": true, "reason": "..."}
  },
  "summary": "Reality Check #1 passed: All steps completed successfully"
}
```

## Troubleshooting

### Database Issues

**Problem**: `pmagent health db` shows `mode=db_off`

**Solutions**:
1. Check if Postgres is running: `pg_isready`
2. Verify DSN in `.env`: `GEMATRIA_DSN=...`
3. Check connection: `psql "$GEMATRIA_DSN" -c "SELECT 1"`
4. Start Postgres: Use `DB_START_CMD` or start manually

**Problem**: `driver_missing` error

**Solution**: Install psycopg:
```bash
pip install psycopg[binary,pool]
```

### LM Studio Issues

**Problem**: `pmagent health lm` shows `mode=lm_off`

**Solutions**:
1. Check if LM Studio server is running: `lsof -i :1234`
2. Verify configuration in `.env`:
   - `LM_STUDIO_ENABLED=1`
   - `LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1`
   - `LM_STUDIO_MODEL=...` (must be set)
3. Start LM Studio server: `lms server start --port 1234`
4. Test endpoint manually:
   ```bash
   curl -X POST http://127.0.0.1:1234/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"test","messages":[{"role":"user","content":"hi"}],"max_tokens":1}'
   ```

**Problem**: `lms CLI not found`

**Solution**: Add LM Studio CLI to PATH:
```bash
export PATH="$HOME/.lmstudio/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc to make permanent
```

**Problem**: Model not found

**Solution**:
1. Download model in LM Studio GUI
2. Verify model name matches `LM_STUDIO_MODEL` exactly
3. Check loaded models: `lms ps` (if available)

## Next Steps

Once everything is working:

1. **Run Reality Check #1**: `pmagent reality-check 1`
2. **Check health**: `pmagent health db && pmagent health lm`
3. **Test Q&A**: `pmagent ask docs "What does Phase-6P deliver?"`
4. **View usage patterns**: See `docs/runbooks/USAGE_PATTERNS_REFERENCE.md`

## Related Documentation

- **Usage Patterns**: `docs/runbooks/USAGE_PATTERNS_REFERENCE.md`
- **LM Studio Setup**: `docs/runbooks/LM_STUDIO_SETUP.md`
- **Database Health**: `docs/runbooks/DB_HEALTH.md`
- **Environment Config**: `env_example.txt`

