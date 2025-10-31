# Figma MCP Integration Setup Guide

This guide explains how to set up and use Figma MCP (Model Context Protocol) integration with Cursor for design automation and collaboration.

## Overview

The Figma MCP integration allows Cursor to communicate with Figma, enabling:
- Reading Figma designs programmatically
- Creating and modifying design elements
- Bulk text replacement
- Component management
- Prototyping and connector creation
- Real-time collaboration between design and development

## Prerequisites

- **Cursor AI** with MCP support
- **Bun** runtime (for the MCP server)
- **Node.js** (for WebSocket server)
- **Figma account** with plugin access
- **Localtunnel** (for web version access)

## Current Status

✅ **MCP Server**: Configured in Cursor
✅ **WebSocket Tunnel**: Active at https://figmatunnel.loca.lt
⚠️ **Port Conflict**: Port 3055 is currently in use
🔄 **Figma Plugin**: Needs to be configured for tunnel access

## Quick Start (Automated)

For the fastest setup, use the automated startup script:

```bash
cd /home/mccoy/Projects/Gemantria.v2
./scripts/start_figma_mcp.sh
```

This script handles port conflicts, starts the tunnel, and provides connection information automatically.

## Installation Steps

### 1. Install Required Packages

```bash
# Install Figma MCP packages
cd /home/mccoy
npm install cursor-talk-to-figma-mcp cursor-talk-to-figma-socket

# Install localtunnel for web access
npm install localtunnel
```

### 2. Configure Cursor MCP

The MCP server is already configured in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "TalkToFigma": {
      "command": "node",
      "args": [
        "/home/mccoy/node_modules/cursor-talk-to-figma-mcp/dist/server.cjs"
      ]
    }
  }
}
```

### 3. Start WebSocket Server

**For Desktop Figma:**
```bash
cd /home/mccoy
bunx cursor-talk-to-figma-socket
```

**For Web Figma:**
```bash
# Start tunnel first
npx localtunnel --port 3055 --subdomain figmatunnel

# Then start WebSocket server (in another terminal)
node -e "
const WebSocket = require('ws');
const server = new WebSocket.Server({
  port: 3055,
  host: '0.0.0.0',
  perMessageDeflate: false
});
server.on('connection', (ws) => {
  console.log('Client connected from web version');
  ws.on('message', (message) => {
    console.log('Received:', message.toString());
  });
});
console.log('WebSocket server running on 0.0.0.0:3055 for web browser access');
"
```

### 4. Install Figma Plugin

1. Go to [Figma Community Plugin](https://www.figma.com/community/plugin/1485687494525374295/cursor-talk-to-figma-mcp-plugin)
2. Click "Install" or "Try it out"
3. The plugin should appear in your Figma plugins list

### 5. Configure Plugin Connection

**For Desktop Figma:**
- Open Figma
- Go to Plugins → Cursor MCP Plugin
- The plugin should automatically connect to `ws://localhost:3055`

**For Web Figma:**
- Open Figma in your browser
- Go to Plugins → Cursor MCP Plugin
- **Important**: The plugin may need to be modified to use the tunnel URL
- Look for configuration options to set the WebSocket URL to: `wss://figmatunnel.loca.lt`

## Usage

### 1. Join a Channel

In Cursor, use the `join_channel` tool:

```
join_channel with channel name: "myproject"
```

### 2. Available MCP Tools

Once connected, you have access to 35+ Figma automation tools:

#### Document & Selection
- `get_document_info` - Get current document details
- `get_selection` - Get current selection
- `read_my_design` - Get detailed design information

#### Creating Elements
- `create_rectangle` - Create rectangles with custom properties
- `create_frame` - Create frames/containers
- `create_text` - Create text elements

#### Modifying Elements
- `set_fill_color` - Change fill colors
- `set_stroke_color` - Change stroke/border colors
- `move_node` - Move elements
- `resize_node` - Resize elements
- `set_text_content` - Change text content

#### Layout & Design
- `set_layout_mode` - Set auto-layout properties
- `set_padding` - Configure padding
- `set_axis_align` - Set alignment properties

#### Components & Styles
- `get_local_components` - List available components
- `create_component_instance` - Create component instances
- `get_instance_overrides` - Get component overrides

#### Advanced Features
- `scan_text_nodes` - Bulk text analysis
- `set_multiple_text_contents` - Bulk text replacement
- `get_reactions` - Get prototyping connections
- `create_connections` - Create flow connectors

## Troubleshooting

### Port 3055 Already in Use

If you see `EADDRINUSE` errors:

```bash
# Kill existing processes on port 3055
sudo lsof -ti:3055 | xargs kill -9

# Or find what's using the port
sudo lsof -i :3055
```

### Web Version Connection Issues

For web Figma, ensure:
1. Localtunnel is running: `npx localtunnel --port 3055 --subdomain figmatunnel`
2. Plugin is configured to use: `wss://figmatunnel.loca.lt`
3. WebSocket server is bound to `0.0.0.0`

### Plugin Won't Connect

1. Check WebSocket server logs for connection attempts
2. Verify tunnel URL is accessible: `curl https://figmatunnel.loca.lt`
3. Restart both tunnel and WebSocket server
4. Check browser console for CORS errors

### No Tools Available in Cursor

1. Restart Cursor after MCP configuration changes
2. Check Cursor logs for MCP connection errors
3. Ensure WebSocket server is running before starting Cursor
4. Verify the MCP server path in `~/.cursor/mcp.json`

## Example Workflows

### Bulk Text Replacement

```bash
# 1. Scan all text in current selection
scan_text_nodes with nodeId: "current_selection_id"

# 2. Replace multiple text elements
set_multiple_text_contents with nodeId: "parent_id" and text: [{"nodeId": "text1", "text": "New content"}, {"nodeId": "text2", "text": "Updated text"}]
```

### Component Management

```bash
# 1. Get available components
get_local_components

# 2. Create component instance
create_component_instance with componentKey: "button_component" and x: 100 and y: 200

# 3. Get and apply overrides
get_instance_overrides with nodeId: "instance_id"
set_instance_overrides with sourceInstanceId: "source_id" and targetNodeIds: ["target1", "target2"]
```

### Prototyping Connections

```bash
# 1. Get existing reactions/flows
get_reactions with nodeIds: ["screen1", "screen2", "screen3"]

# 2. Set default connector style
set_default_connector with connectorId: "flow_connector"

# 3. Create connections between screens
create_connections with connections: [{"startNodeId": "screen1", "endNodeId": "screen2", "text": "User login"}, {"startNodeId": "screen2", "endNodeId": "screen3"}]
```

## Architecture

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   Cursor    │◄──►│   MCP Server    │◄──►│ WebSocket   │
│   (Local)   │    │   (Local)       │    │ Server      │
└─────────────┘    └─────────────────┘    │ (Port 3055) │
                                          └─────┬───────┘
                                                │
                                          ┌─────▼───────┐
                                          │  Local      │
                                          │  Tunnel     │
                                          │             │
                                          └─────┬───────┘
                                                │
                                          ┌─────▼───────┐
                                          │   Figma     │
                                          │   Plugin    │
                                          │ (Web/Desktop│
                                          └─────────────┘
```

## Support

For issues with:
- **MCP Server**: Check Cursor MCP logs
- **WebSocket Server**: Check terminal output
- **Figma Plugin**: Check Figma console and plugin logs
- **Tunnel**: Verify https://figmatunnel.loca.lt is accessible

## Next Steps

1. Test basic connection with `join_channel`
2. Experiment with `get_document_info` and `get_selection`
3. Try creating elements with `create_rectangle`
4. Explore bulk operations for text and components

This integration enables seamless collaboration between design and development workflows.
