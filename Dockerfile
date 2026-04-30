# Build Stage
FROM node:22 AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Final Production Image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install Python backend dependencies using uv
COPY backend/requirements.txt backend/
COPY backend/pyproject.toml backend/
RUN cd backend && uv sync

# Copy backend files
COPY backend/ backend/

# Copy built frontend from build stage
COPY --from=frontend-builder /app/dist /app/dist

# Expose port
EXPOSE 8000

# Start command using uv
CMD ["uv", "run", "--project", "backend", "python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
