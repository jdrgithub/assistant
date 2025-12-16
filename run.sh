#!/bin/bash
# Startup script for the assistant

echo "Starting Personal AI Assistant..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Copy from .env.example"
fi

# Start Docker services
echo "Starting Docker services (PostgreSQL, Qdrant)..."
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Initialize database if needed
echo "Initializing database..."
poetry run python backend/scripts/init_db.py

# Start backend
echo "Starting FastAPI backend..."
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &

# Start frontend (if needed)
# cd frontend && npm run dev &

echo "Backend running at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"

