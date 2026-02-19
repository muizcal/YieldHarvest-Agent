#!/bin/bash
set -e

echo "Starting YieldHarvest services..."

# Start API server in background
echo "Starting API server..."
python3 api-server.py &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start agent in foreground
echo "Starting autonomous agent..."
python3 agent/core/agent.py &
AGENT_PID=$!

# Wait for both processes
wait $API_PID $AGENT_PID