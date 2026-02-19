#!/bin/bash
set -e

echo "Starting API..."
python3 api-server.py &

echo "Starting Agent..."
python3 agent/core/agent.py &

wait -n
