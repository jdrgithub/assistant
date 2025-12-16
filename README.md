# Hybrid Personal AI Assistant

Self-hosted personal AI assistant with local Qdrant vector DB and RunPod for GPU-based embeddings and LLM inference.

## Architecture

- **Backend**: FastAPI with PostgreSQL and Qdrant
- **Frontend**: Next.js with React
- **Vector DB**: Qdrant (local, Dockerized)
- **Metadata DB**: PostgreSQL
- **GPU Tasks**: RunPod (embeddings + LLM inference)

## Setup

### Prerequisites

- Python 3.10+
- Poetry
- Node.js 18+
- Docker and Docker Compose
- RunPod account with API key

### Backend Setup

1. Install dependencies:
```bash
poetry install
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration (RunPod API keys, database URLs, etc.)

4. Start PostgreSQL and Qdrant:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

5. Run database migrations (when Alembic is set up):
```bash
poetry run alembic upgrade head
```

6. Start the backend:
```bash
poetry run uvicorn backend.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

### RunPod Setup

1. Build and push Docker image for RunPod pods:
```bash
cd runpod
docker build -t your-registry/assistant-runpod:latest .
docker push your-registry/assistant-runpod:latest
```

2. Create RunPod endpoints:
   - Embedding endpoint: Use `embed.py` script
   - LLM endpoint: Use `inference.py` script

3. Update `.env` with your RunPod endpoint IDs.

## Usage

1. Register a user via `/api/auth/register`
2. Login via `/api/auth/login` to get access token
3. Ingest documents via `/api/ingest/`
4. Chat via `/api/chat/` or use the frontend UI

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `POST /api/ingest/` - Ingest document
- `POST /api/chat/` - Chat with RAG
- `POST /api/search/` - Search documents

## Project Structure

```
backend/          # FastAPI backend
frontend/         # Next.js frontend
runpod/           # RunPod job scripts
docker/           # Docker Compose configs
```

