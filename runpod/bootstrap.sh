#!/bin/bash
# Bootstrap script for RunPod LLM endpoint
# Downloads Ollama and starts the server

set -e

echo "Starting bootstrap..."

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Start Ollama server in background
echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for server to be ready
echo "Waiting for Ollama server to start..."
sleep 10

# Pull the model (this will download it on first run)
echo "Pulling model: mistral"
ollama pull mistral || echo "Model pull failed, but continuing..."

echo "Bootstrap complete. Ollama PID: $OLLAMA_PID"

# Keep container alive
wait $OLLAMA_PID

