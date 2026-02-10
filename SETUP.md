# Complete Setup Guide

This guide walks you through setting up the entire system, including RunPod configuration.

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- Docker and Docker Compose installed
- RunPod account (sign up at https://runpod.io)
- Basic familiarity with terminal/command line

## Part 1: Local Setup

### Step 1: Install Python Dependencies

```bash
cd /home/jdr/jdrgithub/assistant
./install_deps.sh
```

This creates `.venv` and installs all Python packages. Verify it worked:

```bash
.venv/bin/python -c "import fastapi; print('FastAPI installed')"
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set these values:

```bash
# Generate a strong secret key (use this command):
# python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key-here

# Database (defaults are fine for local setup)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/assistant_db

# Qdrant (defaults are fine)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# RunPod - we'll set these after creating endpoints
RUNPOD_API_KEY=
RUNPOD_EMBEDDING_POD_ID=
RUNPOD_LLM_POD_ID=

# Embedding model (default is fine)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# LLM model (default is fine)
LLM_MODEL=mistral
```

For frontend, create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Start Docker Services

```bash
docker-compose -f docker/docker-compose.yml up -d
```

This starts:
- PostgreSQL on port 5432
- Qdrant on ports 6333 (HTTP) and 6334 (gRPC)

Verify they're running:

```bash
docker ps | grep -E "postgres|qdrant"
```

You should see both containers.

### Step 5: Initialize Database

```bash
.venv/bin/python backend/scripts/init_db.py
```

Or use Alembic migrations:

```bash
.venv/bin/alembic -c backend/alembic.ini upgrade head
```

### Step 6: CLI Capture (Recommended)

Set environment variables and run the CLI:

```bash
export ASSISTANT_API_URL=http://localhost:8000
export ASSISTANT_TOKEN=your-jwt-token
.venv/bin/python backend/cli/assistant_cli.py
```

## Part 2: RunPod Setup

RunPod provides GPU pods on-demand. We'll create two endpoints:
1. **Embedding endpoint** - Converts text to vectors
2. **LLM endpoint** - Generates text completions

### Step 1: Get Your RunPod API Key

1. Go to https://runpod.io and sign up/login
2. Navigate to Settings → API Keys
3. Create a new API key
4. Copy it to your `.env` file:
   ```bash
   RUNPOD_API_KEY=your-api-key-here
   ```

### Step 2: Build and Push Docker Image

The RunPod pods need a Docker image with our scripts. We'll build it and push to a registry.

**Option A: Using Docker Hub (easiest)**

```bash
cd runpod

# Build the image
docker build -t your-dockerhub-username/assistant-runpod:latest .

# Login to Docker Hub
docker login

# Push the image
docker push your-dockerhub-username/assistant-runpod:latest
```

**Option B: Using RunPod's Registry**

RunPod provides a registry. Check their docs for the exact commands, but it's similar:

```bash
docker build -t runpod/assistant-runpod:latest .
docker push runpod/assistant-runpod:latest
```

### Step 3: Create Embedding Endpoint

1. Go to RunPod dashboard → Endpoints → Create Endpoint
2. Configure:
   - **Name**: `assistant-embedding`
   - **Container Image**: `your-dockerhub-username/assistant-runpod:latest`
   - **Container Disk**: 10GB (enough for model weights)
   - **GPU Type**: RTX 3090 or similar (cheaper options work fine)
   - **Docker Command**: `python3 /workspace/embed.py sentence-transformers/all-MiniLM-L6-v2`
   - **Volume Mount**: `/workspace` (for model cache)
   - **Environment Variables**: None needed
   - **Idle Timeout**: 5 minutes (auto-shutdown when not in use)

3. Click "Create Endpoint"
4. Wait for it to deploy (may take a few minutes)
5. Copy the **Endpoint ID** (looks like `abc123def456`)
6. Add to `.env`:
   ```bash
   RUNPOD_EMBEDDING_POD_ID=abc123def456
   ```

### Step 4: Create LLM Endpoint

1. Create another endpoint:
   - **Name**: `assistant-llm`
   - **Container Image**: `your-dockerhub-username/assistant-runpod:latest`
   - **Container Disk**: 20GB (LLM models are larger)
   - **GPU Type**: A100 or similar (for faster inference)
   - **Docker Command**: `python3 /workspace/inference.py`
   - **Volume Mount**: `/workspace`
   - **Idle Timeout**: 5 minutes

2. **Important**: Before creating, you need to modify the Dockerfile or add a startup script that downloads the Ollama model. The `inference.py` script expects Ollama to be running.

   Create `runpod/bootstrap.sh`:
   ```bash
   #!/bin/bash
   # Download Ollama if not present
   if ! command -v ollama &> /dev/null; then
       curl -fsSL https://ollama.ai/install.sh | sh
   fi
   
   # Start Ollama server
   ollama serve &
   
   # Wait for server to be ready
   sleep 5
   
   # Pull the model (this will download it on first run)
   ollama pull mistral
   
   # Keep container alive
   wait
   ```

   Update `runpod/Dockerfile` to include Ollama:
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /workspace

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       curl \
       && rm -rf /var/lib/apt/lists/*

   # Install Ollama
   RUN curl -fsSL https://ollama.ai/install.sh | sh

   # Install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy scripts
   COPY embed.py .
   COPY inference.py .
   COPY bootstrap.sh .
   RUN chmod +x bootstrap.sh

   # Start Ollama and keep container alive
   CMD ["./bootstrap.sh"]
   ```

   Rebuild and push:
   ```bash
   docker build -t your-dockerhub-username/assistant-runpod:latest .
   docker push your-dockerhub-username/assistant-runpod:latest
   ```

3. Create the endpoint with the updated image
4. Copy the Endpoint ID to `.env`:
   ```bash
   RUNPOD_LLM_POD_ID=xyz789ghi012
   ```

### Step 5: Test RunPod Endpoints

Test the embedding endpoint:

```bash
# Create a test script
cat > test_runpod.py << 'EOF'
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from backend.services.runpod_service import runpod_service

async def test():
    texts = ["This is a test document", "Another test"]
    embeddings = await runpod_service.embed_texts(texts)
    print(f"Got {len(embeddings)} embeddings")
    print(f"First embedding dimension: {len(embeddings[0])}")

asyncio.run(test())
EOF

.venv/bin/python test_runpod.py
```

If it works, you'll see embedding vectors. If not, check:
- Endpoint is active in RunPod dashboard
- API key is correct
- Endpoint ID is correct

## Part 3: Start the Application

### Start Backend

```bash
.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it:
```bash
curl http://localhost:8000/health
```

### Start Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
- ready started server on 0.0.0.0:3000
```

### Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Part 4: First Use

### 1. Register a User

Go to http://localhost:3000/login and register a new account.

Or via API:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 2. Login

Login via the frontend, or get a token:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

Save the `access_token` from the response.

### 3. Ingest a Document

Create a test document:

```bash
cat > test_doc.md << 'EOF'
# My First Document

This is a test document about artificial intelligence.
AI assistants can help with many tasks.
EOF
```

Ingest it:

```bash
TOKEN="your-access-token-here"

curl -X POST http://localhost:8000/api/ingest/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# My First Document\n\nThis is a test document about artificial intelligence.\nAI assistants can help with many tasks.",
    "source": "test_doc.md",
    "tags": ["test", "ai"]
  }'
```

This will:
1. Chunk the document
2. Send chunks to RunPod embedding endpoint
3. Store embeddings in Qdrant
4. Store metadata in PostgreSQL

### 4. Chat

Go to http://localhost:3000 and start chatting. Ask questions about your ingested documents.

Or via API:

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "use_rag": true
  }'
```

## Troubleshooting

### RunPod Endpoint Not Responding

1. Check endpoint status in RunPod dashboard
2. Check logs in RunPod dashboard (click on endpoint → Logs)
3. Verify API key and endpoint ID in `.env`
4. Test endpoint manually in RunPod dashboard (they have a test interface)

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec -it assistant_postgres psql -U postgres -c "SELECT 1;"

# Reset database (WARNING: deletes all data)
docker-compose -f docker/docker-compose.yml down -v
docker-compose -f docker/docker-compose.yml up -d
.venv/bin/python backend/scripts/init_db.py
```

### Qdrant Connection Errors

```bash
# Check Qdrant is running
docker ps | grep qdrant

# Check Qdrant health
curl http://localhost:6333/health

# View Qdrant collections
curl http://localhost:6333/collections
```

### Embeddings Not Working

1. Verify RunPod embedding endpoint is active
2. Check endpoint logs in RunPod dashboard
3. Test embedding endpoint directly:
   ```bash
   # Use RunPod's test interface in dashboard
   # Input: {"texts": ["test"], "model": "sentence-transformers/all-MiniLM-L6-v2"}
   ```
4. Check that model name matches in `.env` and endpoint

### LLM Not Working

1. Verify Ollama model is downloaded in the pod
2. Check LLM endpoint logs
3. Test LLM endpoint directly in RunPod dashboard
4. Ensure model name in `.env` matches what's available in Ollama

### Frontend Can't Connect to Backend

1. Check backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Check CORS settings in `backend/main.py` (should allow localhost:3000)
4. Check browser console for errors

## Next Steps

- Ingest more documents (Markdown files, notes, etc.)
- Experiment with different assistant roles (coach, counselor, planner)
- Customize prompts in `backend/services/prompt_service.py`
- Add more document types (PDF processing, etc.)
- Set up file watcher for auto-ingestion (see `for_later.txt`)

## Cost Considerations

- RunPod charges per GPU-hour when pods are active
- With 5-minute idle timeout, pods auto-shutdown when not in use
- Embedding jobs are fast (seconds), so cost is minimal
- LLM inference depends on model size and response length
- Monitor usage in RunPod dashboard
