#!/bin/bash
# Docker deployment script

set -e

echo "Building Docker image..."
docker build -t forge-agentic-app .

echo "Docker image built successfully: forge-agentic-app"
echo
echo "To run the container, use:"
echo "docker run -p 8000:8000 -e GEMINI_API_KEY=your_key_here forge-agentic-app"
