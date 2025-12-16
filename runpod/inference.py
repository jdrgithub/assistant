"""
RunPod LLM inference job script.
Takes JSON input, returns completion.

This script is called by RunPod when a job is submitted.
It expects Ollama to be running (started by bootstrap.sh).
"""
import json
import sys
import time
from ollama import Client


def wait_for_ollama(max_wait=60):
    """Wait for Ollama server to be ready."""
    client = Client(host="http://localhost:11434")
    for _ in range(max_wait):
        try:
            client.list()  # Test connection
            return True
        except:
            time.sleep(1)
    return False


def main():
    """Main inference job function."""
    # Wait for Ollama to be ready
    if not wait_for_ollama():
        output = {"error": "Ollama server not available"}
        print(json.dumps(output))
        sys.exit(1)
    
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        output = {"error": "Invalid JSON input"}
        print(json.dumps(output))
        sys.exit(1)
    
    prompt = input_data.get("prompt", "")
    model = input_data.get("model", "mistral")
    temperature = input_data.get("temperature", 0.7)
    max_tokens = input_data.get("max_tokens", 1000)
    
    if not prompt:
        output = {"error": "No prompt provided"}
        print(json.dumps(output))
        sys.exit(1)
    
    # Initialize Ollama client
    client = Client(host="http://localhost:11434")
    
    # Generate completion
    try:
        response = client.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )
        
        text = response.get("response", "")
        
        output = {
            "text": text,
            "model": model
        }
        
    except Exception as e:
        output = {
            "error": str(e),
            "text": ""
        }
    
    print(json.dumps(output))


if __name__ == "__main__":
    main()

