# Hybrid Personal AI Assistant

A self-hosted personal AI assistant that keeps all your data local while using RunPod's GPU infrastructure for computationally expensive tasks (embeddings and LLM inference).

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Your Local Server (Beelink/Ubuntu Box)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Next.js     │  │  FastAPI     │  │  PostgreSQL  │ │
│  │  Frontend    │→ │  Backend     │→ │  Metadata DB │ │
│  │  (Port 3000) │  │  (Port 8000) │  │  (Port 5432) │ │
│  └──────────────┘  └──────┬───────┘  └──────────────┘ │
│                            │                            │
│                            ↓                            │
│                    ┌──────────────┐                    │
│                    │   Qdrant     │                    │
│                    │  Vector DB   │                    │
│                    │  (Port 6333) │                    │
│                    └──────────────┘                    │
└────────────────────────────┬────────────────────────────┘
                             │
                             │ API Calls (embeddings, LLM)
                             ↓
┌─────────────────────────────────────────────────────────┐
│  RunPod GPU Pods (On-Demand)                             │
│  ┌──────────────┐              ┌──────────────┐        │
│  │  Embedding   │              │  LLM         │        │
│  │  Pod         │              │  Inference   │        │
│  │  (sentence-  │              │  Pod         │        │
│  │  transformers│              │  (Ollama/    │        │
│  │  / BGE)      │              │  Mistral)    │        │
│  └──────────────┘              └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document Ingestion:**
   - You upload a document (Markdown, text, JSON)
   - Backend chunks the text using LangChain
   - Chunks are sent to RunPod embedding pod
   - Embeddings are stored in local Qdrant vector DB
   - Metadata (source, tags, timestamps) stored in PostgreSQL

2. **Chat Query:**
   - You send a message via the frontend
   - Backend embeds your query using RunPod
   - Qdrant searches for similar document chunks (RAG)
   - Retrieved context + your message → RunPod LLM pod
   - LLM generates response using your knowledge base
   - Response + sources returned to frontend

3. **Why RunPod?**
   - Embeddings and LLM inference need GPUs
   - You don't want to run GPUs 24/7 on your local server
   - RunPod provides on-demand GPU pods
   - You only pay when processing (auto-shutdown when idle)
   - All your data stays on your server; only text chunks/prompts go to RunPod

## Components

### Backend (FastAPI)
- **API Routes**: Authentication, document ingestion, chat, search
- **Services**: 
  - `runpod_service.py` - Communicates with RunPod API
  - `qdrant_service.py` - Manages vector database
  - `embedding_service.py` - Orchestrates embedding pipeline
  - `llm_service.py` - Handles LLM inference
  - `prompt_service.py` - Builds prompts with role injection
- **Database**: PostgreSQL for metadata, Qdrant for vectors

### Frontend (Next.js)
- Chat interface with role selection (coach, counselor, planner)
- Document upload/ingestion
- Authentication (login/register)
- Real-time chat with source citations

### RunPod Pods
- **Embedding Pod**: Runs `embed.py` script with sentence-transformers
- **LLM Pod**: Runs `inference.py` script with Ollama/Mistral

## Quick Start

See [SETUP.md](SETUP.md) for detailed setup instructions.

## CLI Capture (Recommended)

The CLI is the primary capture flow and replaces curl-based interactions.

```bash
export ASSISTANT_API_URL=http://localhost:8000
export ASSISTANT_TOKEN=your-jwt-token
.venv/bin/python backend/cli/assistant_cli.py
```

Use it to:
- Quick capture raw thoughts
- Capture via chatbot classification
- Review and approve/reject items
- Normal chat queries

## Project Structure

```
assistant/
├── backend/              # FastAPI backend
│   ├── api/routes/       # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   └── main.py          # Application entrypoint
├── frontend/            # Next.js frontend
│   ├── app/             # Next.js app directory
│   ├── components/      # React components
│   └── lib/             # Utilities
├── runpod/              # RunPod job scripts
│   ├── embed.py         # Embedding job
│   ├── inference.py     # LLM inference job
│   └── Dockerfile       # Container image
└── docker/              # Docker Compose configs
```

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/ingest/` - Ingest document (text/JSON)
- `POST /api/upload/` - Upload file (Markdown, text)
- `POST /api/chat/` - Chat with RAG
- `POST /api/search/` - Search documents
- `GET /api/documents/` - List documents
- `GET /health` - Health check

## Security

- All data stored locally (PostgreSQL, Qdrant)
- JWT authentication for API access
- RunPod only receives sanitized text chunks (no personal data)
- No cloud SaaS dependencies (Pinecone, OpenAI, etc.)
- Secrets in environment variables (never in code)

## License

MIT
