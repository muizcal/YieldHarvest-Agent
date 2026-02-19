#!/bin/bash

# Start API server in background
python3 api-server.py &

# Start agent in foreground
python3 agent/core/agent.py