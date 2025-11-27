# API Server Hardening Guide

## Problem

The API server was constantly going down, causing wasted tokens during troubleshooting. This guide documents the hardening measures implemented to prevent server crashes and ensure automatic recovery.

## Solutions Implemented

### 1. Process Manager Script (`scripts/api_server_manager.sh`)

A robust process manager that:
- **Auto-restart**: Automatically restarts the server if it crashes
- **Health monitoring**: Continuously checks if the server is responding
- **Logging**: Logs all operations to `logs/api_server_manager.log`
- **PID tracking**: Tracks server process ID for clean shutdowns
- **Max restarts**: Limits restart attempts to prevent infinite loops

**Usage:**
```bash
# Start server
make api.start
# OR
bash scripts/api_server_manager.sh start

# Start with auto-restart watcher (recommended)
make api.watch
# OR
bash scripts/api_server_manager.sh watch

# Check status
make api.status
# OR
bash scripts/api_server_manager.sh status

# Stop server
make api.stop
# OR
bash scripts/api_server_manager.sh stop

# Restart server
make api.restart
# OR
bash scripts/api_server_manager.sh restart
```

### 2. Systemd Service (`systemd/gemantria-api.service`)

For production deployments, a systemd service provides:
- **Automatic startup**: Starts on boot
- **Auto-restart**: systemd automatically restarts on failure
- **Resource limits**: Memory and file descriptor limits
- **Logging**: Integrated with systemd journal

**Installation:**
```bash
# Copy service file (adjust user/group/paths as needed)
sudo cp systemd/gemantria-api.service /etc/systemd/system/

# Edit service file to match your user
sudo nano /etc/systemd/system/gemantria-api.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable gemantria-api.service
sudo systemctl start gemantria-api.service

# Check status
sudo systemctl status gemantria-api.service

# View logs
sudo journalctl -u gemantria-api.service -f
```

### 3. Health Check Endpoint (`/api/health`)

A dedicated health check endpoint for monitoring:
- **Status**: Returns `healthy`, `degraded`, or `unhealthy`
- **Component checks**: Verifies exports directory, database connectivity
- **Monitoring**: Can be used by load balancers, monitoring tools

**Usage:**
```bash
# Check health
make api.health
# OR
curl http://localhost:8000/api/health

# Response:
{
  "status": "healthy",
  "timestamp": 1234567890.123,
  "version": "1.0.0",
  "exports": "available",
  "database": "configured"
}
```

### 4. Improved Error Handling

Enhanced global exception handler:
- **Full traceback logging**: Logs complete stack traces for debugging
- **Structured logging**: Includes path, method, and error details
- **Production safety**: Hides internal details in production (DEBUG=0)
- **Non-fatal errors**: Server continues running after handling exceptions

### 5. Makefile Targets

Convenient Makefile targets for all operations:
- `make api.start` - Start server
- `make api.stop` - Stop server
- `make api.restart` - Restart server
- `make api.status` - Check status
- `make api.watch` - Start with auto-restart
- `make api.health` - Check health endpoint

## Recommended Setup

### Development

Use the process manager with auto-restart:

```bash
# Start with watcher (auto-restarts on failure)
make api.watch
```

This runs in the foreground and automatically restarts the server if it crashes.

### Production

Use systemd service:

```bash
# Install and enable
sudo cp systemd/gemantria-api.service /etc/systemd/system/
sudo systemctl enable gemantria-api.service
sudo systemctl start gemantria-api.service
```

## Monitoring

### Check Server Status

```bash
# Quick status check
make api.status

# Health endpoint
make api.health

# Process check
ps aux | grep uvicorn
lsof -i :8000
```

### View Logs

```bash
# Process manager logs
tail -f logs/api_server_manager.log

# Server logs
tail -f logs/api_server.log

# Systemd logs (if using systemd)
sudo journalctl -u gemantria-api.service -f
```

## Troubleshooting

### Server Won't Start

1. **Check venv**: Ensure virtual environment is activated
   ```bash
   source .venv/bin/activate
   ```

2. **Check port**: Verify port 8000 is not in use
   ```bash
   lsof -i :8000
   ```

3. **Check logs**: Review error logs
   ```bash
   tail -50 logs/api_server.log
   ```

### Server Keeps Crashing

1. **Check error logs**: Look for Python exceptions
   ```bash
   tail -100 logs/api_server.log | grep -i error
   ```

2. **Check health endpoint**: Verify what's failing
   ```bash
   curl http://localhost:8000/api/health
   ```

3. **Increase restart delay**: Edit `RESTART_DELAY` in `api_server_manager.sh`

### Max Restarts Reached

If the watcher stops due to max restarts:
1. Check logs for root cause
2. Fix the underlying issue
3. Restart the watcher: `make api.watch`

## Configuration

### Environment Variables

- `API_PORT`: Server port (default: 8000)
- `API_HOST`: Bind address (default: 0.0.0.0)
- `LOG_DIR`: Log directory (default: `logs/`)
- `DEBUG`: Enable debug mode (default: 0)

### Process Manager Settings

Edit `scripts/api_server_manager.sh`:
- `MAX_RESTARTS`: Maximum restart attempts (default: 10)
- `RESTART_DELAY`: Delay between restarts in seconds (default: 2)

## Best Practices

1. **Always use the process manager**: Don't run `uvicorn` directly
2. **Monitor logs**: Regularly check logs for issues
3. **Use health checks**: Integrate `/api/health` into monitoring
4. **Set resource limits**: Configure memory/CPU limits in systemd
5. **Keep dependencies updated**: Regularly update Python packages

## Future Enhancements

- [ ] Graceful shutdown handling
- [ ] Metrics collection (Prometheus)
- [ ] Rate limiting
- [ ] Request timeout handling
- [ ] Circuit breaker pattern
- [ ] Distributed tracing

