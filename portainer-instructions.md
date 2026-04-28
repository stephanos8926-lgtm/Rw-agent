# Using Portainer to Deploy the Application

Portainer makes managing containerized applications on a home server straightforward. Follow these steps to deploy this application.

## Prerequisites
- **Portainer installed** on your home server.
- **Docker installed** on your home server.
- **Project code** copied to a directory on your server.

## Steps

1. **Log in to Portainer** via your web browser (usually `http://<your-server-ip>:9000`).
2. **Create a Stack:**
   - Go to **Stacks** in the left menu.
   - Click **+ Add stack**.
   - Name your stack (e.g., `forge-agentic-os`).
   - Choose **Repository** (if using GitHub) or **Web editor** (paste the configuration below).
   - If using **Web editor**, paste the following `docker-compose.yml` configuration:

```yaml
version: '3.8'
services:
  app:
    image: my-forge-app:latest # Build this tag locally or via CI
    build: .
    container_name: forge-agentic-os
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=your_key_here # REQUIRED
      - WORKSPACE_DIR=/app # Or map a volume to your local path
    volumes:
      - ./workspace:/app/workspace # Map a local folder as the workspace
    restart: unless-stopped
```

3. **Deploy:**
   - Ensure the `Dockerfile` is present in your project root directory.
   - Click **Deploy the stack**.

4. **Access:**
   - Once the stack is running, access your app at `http://<your-server-ip>:8000`.

---
*Note: Make sure to replace `your_key_here` with your actual GEMINI_API_KEY environment variable within Portainer's environment variable configuration section for the container.*
