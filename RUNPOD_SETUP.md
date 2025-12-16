# RunPod Setup - Detailed Guide

This guide explains exactly how to set up RunPod endpoints for embeddings and LLM inference.

## Understanding RunPod

RunPod provides GPU compute on-demand. Instead of buying expensive GPUs, you:
1. Create "endpoints" (like serverless functions)
2. Submit jobs to endpoints via API
3. Pay only when GPUs are active
4. Endpoints auto-shutdown when idle (saves money)

## Architecture

```
Your Backend → RunPod API → GPU Pod → Returns Result
```

When you call `runpod_service.embed_texts()`:
1. Backend sends job to RunPod API
2. RunPod spins up a GPU pod (if not already running)
3. Pod runs `embed.py` with your text
4. Pod returns embeddings
5. Pod shuts down after idle timeout

## Step-by-Step Setup

### 1. Create RunPod Account

1. Go to https://runpod.io
2. Sign up (free account works)
3. Add payment method (required, but you only pay for usage)

### 2. Get API Key

1. Dashboard → Settings → API Keys
2. Click "Create API Key"
3. Copy the key (you won't see it again)
4. Add to `.env`: `RUNPOD_API_KEY=your-key-here`

### 3. Build Docker Image

The image contains our scripts and dependencies.

```bash
cd runpod

# Build
docker build -t your-dockerhub-username/assistant-runpod:latest .

# Login to Docker Hub
docker login

# Push
docker push your-dockerhub-username/assistant-runpod:latest
```

**Note**: Replace `your-dockerhub-username` with your actual Docker Hub username. If you don't have one, sign up at https://hub.docker.com (free).

### 4. Create Embedding Endpoint

1. RunPod Dashboard → Endpoints → Create Endpoint

2. Fill in:
   - **Name**: `assistant-embedding`
   - **Container Image**: `your-dockerhub-username/assistant-runpod:latest`
   - **Container Disk**: `10 GB` (enough for sentence-transformers models)
   - **GPU Type**: 
     - Cheapest: `RTX 3090` (~$0.29/hour)
     - Faster: `RTX 4090` (~$0.49/hour)
   - **Docker Command**: 
     ```
     python3 /workspace/embed.py sentence-transformers/all-MiniLM-L6-v2
     ```
   - **Volume Mount**: `/workspace` (persists model cache)
   - **Environment Variables**: Leave empty
   - **Idle Timeout**: `5` minutes (auto-shutdown)
   - **Scale Type**: `Queue Delay` (recommended)
   - **Max Workers**: `1` (one job at a time)

3. Click "Create Endpoint"

4. Wait 2-3 minutes for deployment

5. Copy the **Endpoint ID** (looks like `abc123def456ghi789`)

6. Add to `.env`:
   ```bash
   RUNPOD_EMBEDDING_POD_ID=abc123def456ghi789
   ```

### 5. Test Embedding Endpoint

In RunPod dashboard:
1. Click on your endpoint
2. Go to "Test" tab
3. Enter:
   ```json
   {
     "texts": ["This is a test"],
     "model": "sentence-transformers/all-MiniLM-L6-v2"
   }
   ```
4. Click "Run"
5. Should return embeddings array

Or test from your backend:
```bash
.venv/bin/python -c "
import asyncio
from backend.services.runpod_service import runpod_service
async def test():
    result = await runpod_service.embed_texts(['test'])
    print(f'Success: {len(result)} embeddings')
asyncio.run(test())
"
```

### 6. Create LLM Endpoint

**Important**: The LLM endpoint needs Ollama running. Our `bootstrap.sh` handles this.

1. Create new endpoint:
   - **Name**: `assistant-llm`
   - **Container Image**: `your-dockerhub-username/assistant-runpod:latest`
   - **Container Disk**: `20 GB` (LLM models are large)
   - **GPU Type**: 
     - Budget: `RTX 3090` (~$0.29/hour)
     - Recommended: `A100` (~$1.79/hour, much faster)
   - **Docker Command**: 
     ```
     ./bootstrap.sh
     ```
     This starts Ollama server, then keeps container alive
   - **Volume Mount**: `/workspace` (persists downloaded models)
   - **Idle Timeout**: `5` minutes
   - **Scale Type**: `Queue Delay`
   - **Max Workers**: `1`

2. **First Run**: The pod will download the Mistral model (~4GB). This takes 5-10 minutes. You can see progress in the endpoint logs.

3. Copy Endpoint ID to `.env`:
   ```bash
   RUNPOD_LLM_POD_ID=xyz789ghi012jkl345
   ```

### 7. Test LLM Endpoint

In RunPod dashboard test interface:
```json
{
  "prompt": "Hello, how are you?",
  "model": "mistral",
  "temperature": 0.7,
  "max_tokens": 100
}
```

Should return generated text.

### 8. How Jobs Work

When your backend calls `runpod_service.generate_completion()`:

1. Backend sends job to RunPod API:
   ```python
   {
     "prompt": "User: Hello\nAssistant:",
     "model": "mistral",
     "temperature": 0.7,
     "max_tokens": 1000
   }
   ```

2. RunPod API routes to your LLM endpoint

3. If pod is off, RunPod starts it (cold start ~30 seconds)

4. Pod receives job, calls `inference.py`:
   - `inference.py` reads JSON from stdin
   - Connects to Ollama (running via bootstrap.sh)
   - Generates completion
   - Returns JSON to stdout

5. RunPod returns result to your backend

6. Pod stays alive for 5 minutes (idle timeout), then shuts down

### 9. Monitoring

- **Dashboard**: See active pods, job queue, costs
- **Logs**: Click endpoint → Logs tab (see what's happening)
- **Metrics**: See GPU utilization, response times

### 10. Cost Optimization

- **Idle Timeout**: Lower = less cost, but more cold starts
- **GPU Type**: Smaller GPUs are cheaper but slower
- **Model Size**: Smaller models = faster inference = less cost
- **Batch Jobs**: Process multiple items in one job (more efficient)

Example costs (approximate):
- Embedding job: ~$0.001 per 1000 texts (very cheap)
- LLM completion: ~$0.01-0.05 per response (depends on length)

## Troubleshooting

### Endpoint Won't Start

- Check logs in RunPod dashboard
- Verify Docker image is public (or you have access)
- Check GPU availability (some regions have limited GPUs)

### Embeddings Return Empty

- Check endpoint logs
- Verify model name matches in code and endpoint
- Test endpoint directly in RunPod dashboard

### LLM Returns Errors

- Check Ollama is running (see logs)
- Verify model is downloaded: `ollama list` (in pod logs)
- Check model name matches: should be "mistral"
- First run takes time to download model

### Jobs Timeout

- Increase timeout in `runpod_service.py` (default 300 seconds)
- Check endpoint logs for errors
- Verify GPU has enough memory for model

### High Costs

- Check idle timeout is set (5 minutes recommended)
- Monitor dashboard for unexpected usage
- Use smaller GPU types if speed isn't critical
- Consider using smaller models

## Alternative: Self-Hosted Ollama

If you want to avoid RunPod costs, you can run Ollama on your own server:

1. Install Ollama on your server
2. Modify `runpod_service.py` to call local Ollama instead
3. For embeddings, use local sentence-transformers

But this requires a GPU on your server, which may not be cost-effective.

