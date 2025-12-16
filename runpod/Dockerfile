FROM python:3.10-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY embed.py .
COPY inference.py .
COPY bootstrap.sh .
RUN chmod +x bootstrap.sh

# Default entrypoint (can be overridden in RunPod endpoint config)
# For embedding: python3 /workspace/embed.py
# For LLM: ./bootstrap.sh (starts Ollama, then inference.py can use it)
CMD ["./bootstrap.sh"]

