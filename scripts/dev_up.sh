#!/usr/bin/env bash
set -euo pipefail

# scripts/dev_up.sh - Hermetic development environment startup
# Starts both API server and Web UI in background, waits for health checks

echo "🚀 Starting Gemantria Development Environment..."

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != *"Gemantria"* ]]; then
    echo "❌ Please activate the virtual environment first:"
    echo "   source .venv/bin/activate"
    exit 1
fi

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo "⚠️  Port $port is already in use"
        return 1
    fi
    return 0
}

# Check ports before starting
echo "🔍 Checking port availability..."
if ! check_port 8000; then
    echo "❌ API port 8000 is busy. Please free it or use a different port."
    exit 1
fi

if ! check_port 5173; then
    echo "❌ Web UI port 5173 is busy. Please free it or use a different port."
    exit 1
fi

# Start API server in background
echo "🔧 Starting API server on port 8000..."
python -m src.services.api_server &
API_PID=$!

# Start Web UI in background
echo "🌐 Starting Web UI on port 5173..."
cd webui/graph
npm run dev &
UI_PID=$!
cd ../..

# Wait for services to start
echo "⏳ Waiting for services to initialize..."

# Check API health
echo "🏥 Checking API server health..."
for i in {1..30}; do
    if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ API server ready on http://localhost:8000"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API server failed to start within 30 seconds"
        kill $API_PID 2>/dev/null || true
        kill $UI_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Check Web UI
echo "🌐 Checking Web UI..."
for i in {1..30}; do
    if curl -s -f http://localhost:5173 >/dev/null 2>&1; then
        echo "✅ Web UI ready on http://localhost:5173"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Web UI failed to start within 30 seconds"
        kill $API_PID 2>/dev/null || true
        kill $UI_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 Development environment is ready!"
echo "   🌐 Web UI: http://localhost:5173"
echo "   🔌 API:    http://localhost:8000"
echo "   📊 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Services are running in background. To stop:"
echo "   kill $API_PID $UI_PID"
echo "   # or use Ctrl+C in respective terminals"

# Keep script running to show logs
echo ""
echo "📋 Service logs (Ctrl+C to exit):"
echo "─" | tr -s '-' | head -c 50
echo ""

# Show logs until interrupted
trap "echo ''; echo '🛑 Shutting down services...'; kill $API_PID $UI_PID 2>/dev/null || true; exit 0" INT

# Keep alive
while true; do
    sleep 1

    # Check if processes are still running
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ API server process died"
        kill $UI_PID 2>/dev/null || true
        exit 1
    fi

    if ! kill -0 $UI_PID 2>/dev/null; then
        echo "❌ Web UI process died"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
done
