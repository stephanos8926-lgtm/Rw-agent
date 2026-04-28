#!/bin/bash
# Start script for the Forge Agentic OS Backend
echo "Starting Forge Agentic OS Backend on port 8000..."
python3 -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
