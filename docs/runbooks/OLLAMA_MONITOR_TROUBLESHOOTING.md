# Ollama Monitor Troubleshooting

## HTTP 500 Error

If you see "Error: HTTP 500" in the Ollama Monitor panel:

### 1. Check if API Server is Running

```bash
curl http://localhost:8000/api/ollama/monitor
```

If you get a connection error, start the API server:

```bash
cd /home/mccoy/Projects/Gemantria.v2
source .venv/bin/activate
python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Verify Router is Registered

The Ollama router should be included in `src/services/api_server.py`:

```python
from src.services.routers.ollama_proxy import router as ollama_router
app.include_router(ollama_router)
```

### 3. Test the Endpoint Directly

```bash
python3 scripts/test_ollama_monitor.py
```

### 4. Check Server Logs

Look for errors in the API server output when accessing `/api/ollama/monitor`.

### 5. Restart the API Server

If you just added the router, restart the server to pick up changes:

```bash
# Stop the server (Ctrl+C or kill the process)
# Then restart:
python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000 --reload
```

## Common Issues

### "Connection Refused"

- API server not running on port 8000
- Solution: Start the API server (see step 1 above)

### "404 Not Found"

- Router not registered
- Solution: Verify `app.include_router(ollama_router)` is in `api_server.py`

### "500 Internal Server Error"

- Check server logs for Python exceptions
- Common causes:
  - Import errors
  - JSON serialization issues
  - Missing dependencies

### Frontend Shows Error but curl Works

- Check browser console for CORS errors
- Verify Vite proxy is configured in `webui/graph/vite.config.ts`:
  ```typescript
  proxy: {
    "/api": {
      target: "http://localhost:8000",
      changeOrigin: true,
    },
  }
  ```

## Verification Steps

1. **Backend test:**
   ```bash
   curl http://localhost:8000/api/ollama/monitor
   ```
   Should return JSON with `lastUpdated`, `activeRequests`, `recentRequests`.

2. **Frontend test:**
   - Open browser console (F12)
   - Navigate to Ollama Monitor panel
   - Check Network tab for `/api/ollama/monitor` request
   - Verify response status is 200

3. **Full integration:**
   - Make a request through the proxy: `POST /api/ollama/proxy/api/chat`
   - Check monitor: `GET /api/ollama/monitor`
   - Should see the request in `recentRequests`

