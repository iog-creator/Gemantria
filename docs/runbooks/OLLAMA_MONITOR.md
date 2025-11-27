# Ollama Monitor

**Purpose:** Monitor all Ollama API requests and responses in real-time through a proxy layer.

## Overview

The Ollama Monitor sits in front of the Ollama server as a proxy, logging every request/response with:
- Model name
- Endpoint (generate, chat, embeddings, raw)
- Timestamps
- Duration
- Token counts (when available)
- HTTP status
- Error messages

## Architecture

### Backend (Python/FastAPI)

1. **Proxy Router** (`src/services/routers/ollama_proxy.py`)
   - `/api/ollama/proxy/{path}` - Proxies all requests to Ollama
   - Logs requests before forwarding
   - Logs responses after receiving

2. **Monitor Store** (`src/services/ollama_monitor/store.py`)
   - In-memory ring buffer (max 200 recent requests)
   - Tracks active and recent requests
   - Thread-safe operations

3. **Monitor API** (`/api/ollama/monitor`)
   - Returns current snapshot of active and recent requests
   - JSON format for frontend consumption

### Frontend (React/TypeScript)

1. **OllamaMonitorPanel** (`webui/orchestrator-shell/OllamaMonitorPanel.tsx`)
   - Real-time dashboard (polls every 2 seconds)
   - Shows active requests (in-flight)
   - Shows recent requests (completed)
   - Summary statistics (total, errors, avg duration)

2. **TypeScript Types** (`webui/orchestrator-shell/types/ollamaMonitor.ts`)
   - Type-safe interfaces for monitor data

## Usage

### Accessing the Monitor

1. Start the API server:
   ```bash
   python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Open the Orchestrator Shell:
   - Navigate to the web UI
   - Click the "🔍" (Ollama Monitor) icon in the left rail

### Configuration

Set `OLLAMA_BASE_URL` environment variable (defaults to `http://localhost:11434`):

```bash
export OLLAMA_BASE_URL=http://localhost:11434
```

### Using the Proxy

All Ollama calls should go through the proxy:

**Before:**
```typescript
fetch("http://localhost:11434/api/chat", { ... })
```

**After:**
```typescript
fetch("/api/ollama/proxy/api/chat", { ... })
```

The proxy automatically forwards to the configured Ollama server.

## Features

### Active Requests
- Shows requests currently in-flight
- Updates in real-time
- Displays: status, model, endpoint, start time, prompt preview

### Recent Requests
- Shows last 200 completed requests
- Displays: status, model, endpoint, duration, HTTP status, tokens, prompt preview
- Color-coded by status (green=success, red=error, yellow=pending)

### Summary Statistics
- Total recent requests
- Error count
- Average duration

## Data Retention

- **Active Requests:** Removed when status changes from "pending"
- **Recent Requests:** Ring buffer of last 200 requests (FIFO)
- **Storage:** In-memory only (resets on server restart)

## Future Enhancements

- [ ] Persistent storage (PostgreSQL)
- [ ] Filtering by model, endpoint, status
- [ ] Export logs to JSON/CSV
- [ ] Streaming updates (SSE/WebSocket)
- [ ] Request/response body inspection
- [ ] Rate limiting metrics
- [ ] Performance analytics

## Troubleshooting

### Monitor shows no requests

1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Check that calls are going through the proxy:
   - Look for `/api/ollama/proxy/` in network tab
   - Direct calls to `localhost:11434` won't be logged

3. Verify API server is running:
   ```bash
   curl http://localhost:8000/api/ollama/monitor
   ```

### Proxy errors

1. Check `OLLAMA_BASE_URL` is correct
2. Verify Ollama server is accessible from API server
3. Check API server logs for connection errors

## Integration Notes

The monitor is integrated into:
- **Orchestrator Shell:** Available as "Ollama Monitor" tool (🔍 icon)
- **API Server:** Routes registered at `/api/ollama/*`

No changes needed to existing Ollama adapter code - it can continue using direct calls, but calls through the proxy will be monitored.

