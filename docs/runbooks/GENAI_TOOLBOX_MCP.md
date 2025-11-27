# GenAI Toolbox MCP Server Installation

This document describes the installation and configuration of the [MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) server for Gemantria.

## Overview

MCP Toolbox for Databases is an open source MCP server that enables AI agents to interact with databases through a standardized tool interface. It provides:

- **Simplified development**: Integrate database tools in less than 10 lines of code
- **Better performance**: Connection pooling, authentication handling
- **Enhanced security**: Integrated auth for secure data access
- **End-to-end observability**: Built-in metrics and tracing with OpenTelemetry support

## Installation

### Binary Installation (Linux AMD64)

The binary has been installed to `~/mcp/genai-toolbox/`:

```bash
# Binary location
~/mcp/genai-toolbox/toolbox

# Version
~/mcp/genai-toolbox/toolbox --version
```

### Configuration

Configuration file: `~/mcp/genai-toolbox/tools.yaml`

The configuration defines:
- **Sources**: Database connections (gematria-db, bible-db)
- **Tools**: SQL queries exposed as MCP tools
- **Toolsets**: Groups of tools for easy loading

### Starting the Server

Use the provided startup script:

```bash
# Start server
/home/mccoy/Projects/Gemantria.v2/scripts/mcp/genai_toolbox_start.sh

# Or manually:
cd ~/mcp/genai-toolbox
PGHOST=/var/run/postgresql ./toolbox \
    --tools-file tools.yaml \
    --port 5000 \
    --address 127.0.0.1 \
    --log-level info
```

### Server Endpoints

- **Health**: `http://127.0.0.1:5000/health`
- **MCP**: `http://127.0.0.1:5000/mcp`
- **Logs**: `/tmp/genai-toolbox.log`

## Configuration Notes

### Database Authentication

The project uses Unix socket authentication (`/var/run/postgresql`), but genai-toolbox requires TCP connections (`localhost:5432`) with password authentication.

**Current Status:**
- ✅ Unix socket authentication works: `psql -h /var/run/postgresql -U mccoy -d gematria`
- ❌ TCP authentication requires password: `psql -h localhost -U mccoy -d gematria`

**Solution Options:**

1. **Configure Postgres Trust Authentication** (Recommended for local development):
   ```bash
   # Edit pg_hba.conf (location varies by installation)
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   
   # Add or modify line for localhost connections:
   host    gematria    mccoy    127.0.0.1/32    trust
   host    bible_db    mccoy    127.0.0.1/32    trust
   
   # Reload Postgres configuration
   sudo systemctl reload postgresql
   ```

2. **Use Actual Database Password**:
   - If your Postgres user has a password, set it in `tools.yaml`
   - Update the `password` field with the actual password

3. **Use .pgpass File**:
   - Create `~/.pgpass` with format: `hostname:port:database:username:password`
   - Set permissions: `chmod 600 ~/.pgpass`
   - Note: This may require Postgres to be configured to use .pgpass

### Current Configuration

The `tools.yaml` file includes:

- **Sources**:
  - `gematria-db`: Gematria application database (read-write)
  - `bible-db`: Bible scripture database (read-only)

- **Tools**:
  - `query-gematria-nodes`: Query concept network nodes
  - `query-bible-verses`: Query Bible verses by reference

- **Toolsets**:
  - `gematria-tools`: Gematria-specific tools
  - `bible-tools`: Bible-specific tools
  - `all-tools`: All available tools

## Integration with Cursor/MCP

To use this server with Cursor or other MCP clients:

1. **Configure MCP Client** (e.g., Cursor's `~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "genai-toolbox": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "http://127.0.0.1:5000/mcp"
      ]
    }
  }
}
```

2. **Or use HTTP transport**:
   - MCP endpoint: `http://127.0.0.1:5000/mcp`
   - Configure client to connect to this endpoint

## Status

✅ **Server is running successfully!**

- **PID**: Check `/tmp/genai-toolbox.pid`
- **Health**: Server responds on port 5000
- **MCP Endpoint**: `http://127.0.0.1:5000/mcp`
- **Logs**: `/tmp/genai-toolbox.log`

## Troubleshooting

### Server Won't Start

1. **Check logs**: `/tmp/genai-toolbox.log`
2. **Verify database connectivity**: Test Postgres connection manually
3. **Check port availability**: Ensure port 5000 is not in use
4. **Verify tools.yaml syntax**: Validate YAML structure
5. **Check Postgres authentication**: Verify `pg_hba.conf` has trust rules before general rules

### Authentication Errors

- **Password authentication failed**: 
  - Verify `pg_hba.conf` has trust rules for `gematria` and `bible_db` databases
  - Ensure trust rules are placed BEFORE the general `all/all` rule
  - Reload Postgres: `sudo systemctl reload postgresql`
- **Connection refused**: Verify Postgres is running and accessible
- **Unix socket issues**: Check `PGHOST` environment variable and socket permissions

### Testing Connection

```bash
# Test Postgres connection
psql -h /var/run/postgresql -U mccoy -d gematria

# Test server health
curl http://127.0.0.1:5000/health

# Check server logs
tail -f /tmp/genai-toolbox.log
```

## References

- [GenAI Toolbox GitHub](https://github.com/googleapis/genai-toolbox)
- [MCP Toolbox Documentation](https://googleapis.github.io/genai-toolbox/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

## Next Steps

1. **Configure Authentication**: Set up proper password or Unix socket authentication
2. **Add More Tools**: Extend `tools.yaml` with additional database queries
3. **Integrate with Cursor**: Configure Cursor to use this MCP server
4. **Add Monitoring**: Set up OpenTelemetry export for observability

