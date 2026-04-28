# Build Stage
FROM node:22 AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Final Production Image
FROM python:3.10-slim

# Install system dependencies (needed by LangGraph and Python app)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python backend dependencies
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend files
COPY backend/ backend/

# Copy built frontend from build stage
COPY --from=frontend-builder /app/dist /app/dist

# Expose port (ensure it matches the backend config in server.py)
EXPOSE 8000

# Start command (assumes uvicorn is installed in the python environment)
CMD ["python", "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
