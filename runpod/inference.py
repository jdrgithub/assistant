"""
RunPod LLM inference job script.
Takes JSON input, returns completion.
"""
import json
import sys
from ollama import Client


def main():
    """Main inference job function."""
    # Read input from stdin
    input_data = json.load(sys.stdin)
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

