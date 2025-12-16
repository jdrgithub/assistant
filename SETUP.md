# Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- RunPod account with API key

## Step 1: Install Dependencies

### Backend
```bash
./install_deps.sh
```

### Frontend
```bash
cd frontend
npm install
```

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY` - Generate a strong random key
- `RUNPOD_API_KEY` - Your RunPod API key
- `RUNPOD_EMBEDDING_POD_ID` - Your embedding endpoint ID
- `RUNPOD_LLM_POD_ID` - Your LLM inference endpoint ID

For frontend, create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 3: Start Docker Services

```bash
docker-compose -f docker/docker-compose.yml up -d
```

This starts:
- PostgreSQL on port 5432
- Qdrant on ports 6333 (HTTP) and 6334 (gRPC)

## Step 4: Initialize Database

```bash
.venv/bin/python backend/scripts/init_db.py
```

Or use Alembic migrations:
```bash
.venv/bin/alembic -c backend/alembic.ini upgrade head
```

## Step 5: Set Up RunPod

1. Build the RunPod Docker image:
```bash
cd runpod
docker build -t your-registry/assistant-runpod:latest .
docker push your-registry/assistant-runpod:latest
```

2. Create RunPod endpoints:
   - Embedding endpoint: Use `embed.py` as entrypoint
   - LLM endpoint: Use `inference.py` as entrypoint

3. Update `.env` with the endpoint IDs

## Step 6: Start the Application

### Backend (Terminal 1)
```bash
.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

## Step 7: Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## First Use

1. Register a user via `/api/auth/register` or the frontend
2. Login to get an access token
3. Upload or ingest documents via `/api/upload/` or `/api/ingest/`
4. Start chatting via the frontend or `/api/chat/`

## Troubleshooting

### Qdrant connection errors
- Ensure Qdrant is running: `docker ps | grep qdrant`
- Check `QDRANT_HOST` and `QDRANT_PORT` in `.env`

### Database connection errors
- Ensure PostgreSQL is running: `docker ps | grep postgres`
- Check `DATABASE_URL` in `.env`
- Verify database exists: `docker exec -it assistant_postgres psql -U postgres -l`

### RunPod errors
- Verify API key is correct
- Check endpoint IDs are valid
- Ensure endpoints are active in RunPod dashboard

