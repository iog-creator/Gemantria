#!/bin/bash

# Figma MCP Startup Script
# Handles port conflicts and tunnel setup for Figma MCP integration

set -e

echo "🎨 Starting Figma MCP Integration..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."

    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi

    if ! command -v bunx &> /dev/null; then
        print_error "Bun is not installed. Please install Bun first."
        exit 1
    fi

    if ! command -v npx &> /dev/null; then
        print_error "npm/npx is not installed. Please install npm first."
        exit 1
    fi

    print_success "All dependencies found"
}

# Kill any existing processes on port 3055
cleanup_port() {
    print_status "Checking for port 3055 conflicts..."

    if lsof -i :3055 &> /dev/null; then
        print_warning "Port 3055 is in use. Cleaning up..."
        sudo lsof -ti:3055 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi

    print_success "Port 3055 is free"
}

# Start the tunnel in background
start_tunnel() {
    print_status "Starting localtunnel for web browser access..."

    # Kill any existing tunnel
    pkill -f "localtunnel.*3055" || true

    # Start new tunnel
    npx localtunnel --port 3055 --subdomain figmatunnel > /tmp/figma_tunnel.log 2>&1 &
    TUNNEL_PID=$!

    # Wait for tunnel to start
    sleep 5

    if curl -s https://figmatunnel.loca.lt > /dev/null; then
        print_success "Tunnel started successfully: https://figmatunnel.loca.lt"
        echo $TUNNEL_PID > /tmp/figma_tunnel.pid
    else
        print_error "Failed to start tunnel"
        exit 1
    fi
}

# Start WebSocket server
start_websocket_server() {
    print_status "Starting WebSocket server..."

    # Kill any existing WebSocket server
    pkill -f "node -e.*WebSocket.Server" || true

    # Start WebSocket server
    node -e "
    const WebSocket = require('ws');
    const server = new WebSocket.Server({
      port: 3055,
      host: '0.0.0.0',
      perMessageDeflate: false
    });

    server.on('connection', (ws) => {
      console.log('🎨 Client connected from Figma');
      ws.on('message', (message) => {
        console.log('📨 Received:', message.toString());
      });
    });

    console.log('🚀 WebSocket server running on 0.0.0.0:3055');
    console.log('🌐 Tunnel available at: https://figmatunnel.loca.lt');
    " > /tmp/figma_websocket.log 2>&1 &
    WS_PID=$!

    sleep 2

    if curl -s http://localhost:3055 > /dev/null; then
        print_success "WebSocket server started successfully"
        echo $WS_PID > /tmp/figma_websocket.pid
    else
        print_error "Failed to start WebSocket server"
        exit 1
    fi
}

# Test MCP server connection
test_mcp_connection() {
    print_status "Testing MCP server connection..."

    # Give it a moment to connect
    sleep 3

    if timeout 10s node /home/mccoy/node_modules/cursor-talk-to-figma-mcp/dist/server.cjs 2>&1 | grep -q "Connected to Figma socket server"; then
        print_success "MCP server connected successfully"
    else
        print_warning "MCP server connection test inconclusive (this is normal if no Figma plugin is connected yet)"
    fi
}

# Display connection information
show_connection_info() {
    echo ""
    echo "🎉 Figma MCP Integration Started!"
    echo "=================================="
    echo ""
    echo "📡 WebSocket Server: ws://localhost:3055"
    echo "🌐 Tunnel URL: https://figmatunnel.loca.lt"
    echo "🎨 MCP Server: Configured in Cursor"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Open Figma (web or desktop)"
    echo "2. Install the plugin: https://www.figma.com/community/plugin/1485687494525374295/cursor-talk-to-figma-mcp-plugin"
    echo "3. In Figma plugin, use WebSocket URL: wss://figmatunnel.loca.lt"
    echo "4. Join a channel using 'join_channel' tool in Cursor"
    echo ""
    echo "🛑 To stop: Run 'pkill -f figmatunnel && pkill -f WebSocket.Server'"
    echo ""
    echo "📊 Monitor logs:"
    echo "  WebSocket: tail -f /tmp/figma_websocket.log"
    echo "  Tunnel: tail -f /tmp/figma_tunnel.log"
}

# Main execution
main() {
    check_dependencies
    cleanup_port
    start_tunnel
    start_websocket_server
    test_mcp_connection
    show_connection_info
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}Shutting down Figma MCP...${NC}"; pkill -f figmatunnel 2>/dev/null || true; pkill -f "node -e.*WebSocket" 2>/dev/null || true; exit 0' INT TERM

# Run main function
main
