#!/bin/bash
# Native (non-Docker) deployment script

set -e

echo "Starting native deployment..."

# 1. Install/Check uv
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# 2. Frontend setup
echo "Installing frontend dependencies..."
npm install
echo "Building frontend..."
npm run build

# 3. Backend setup
echo "Setting up backend with uv..."
cd backend
uv sync
cd ..

echo "Deployment complete."
echo
echo "To start the application, run:"
echo "cd backend && uv run python -m uvicorn server:app --host 0.0.0.0 --port 8000"
