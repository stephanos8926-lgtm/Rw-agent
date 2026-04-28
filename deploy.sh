#!/bin/bash
# Non-dockerized deployment script

echo "Starting non-dockerized deployment..."

# 1. Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# 2. Build frontend
echo "Building frontend..."
npm run build

# 3. Ensure python dependencies are installed
# We assume virtualenv is best practice, but stick to pip install per previous context if user doesn't use venv
echo "Installing python backend dependencies..."
pip install -r backend/requirements.txt

echo "Deployment preparation complete."
echo
echo "To start the application, run:"
echo "python3 -m uvicorn backend.server:app --host 0.0.0.0 --port 8000"
