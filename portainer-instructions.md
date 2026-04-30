# Using Portainer to Deploy the Application

Portainer makes managing containerized applications on a home server straightforward. Follow these steps to deploy this application.

## Prerequisites
- **Portainer installed** on your home server.
- **Docker installed** on your home server.

## Steps

1. **Log in to Portainer** via your web browser (usually `http://<your-server-ip>:9000`).
2. **Create a Stack:**
   - Go to **Stacks** in the left menu.
   - Click **+ Add stack**.
   - Name your stack (e.g., `forge-agentic-os`).
   - Create a `docker-compose.yml` file in your project root or use the Web editor and paste the configuration below:

```yaml
version: '3.8'
services:
  app:
    image: forge-agentic-app
    build: .
    container_name: forge-agentic-os
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=your_key_here # REQUIRED
    volumes:
      - ./data:/app/backend/data # Map for persistent SQLite data
    restart: unless-stopped
```

3. **Deploy:**
   - Ensure the `Dockerfile` is present in your project root directory.
   - Click **Deploy the stack**.

4. **Access:**
   - Once the stack is running, access your app at `http://<your-server-ip>:8000`.

---
*Note: Make sure to replace `your_key_here` with your actual GEMINI_API_KEY environment variable. Also, ensure the ./data directory exists on your host server to persist SQLite databases; otherwise, SQLite data won't survive container restarts.*
