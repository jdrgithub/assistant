"""
RunPod embedding job script.
Takes JSON input, returns embeddings.
"""
import json
import sys
from sentence_transformers import SentenceTransformer


def main():
    """Main embedding job function."""
    # Load model
    model_name = sys.argv[1] if len(sys.argv) > 1 else "sentence-transformers/all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    
    # Read input from stdin
    input_data = json.load(sys.stdin)
    texts = input_data.get("texts", [])
    
    if not texts:
        output = {"error": "No texts provided"}
        print(json.dumps(output))
        sys.exit(1)
    
    # Generate embeddings
    embeddings = model.encode(texts, convert_to_nested=True).tolist()
    
    # Output results
    output = {
        "embeddings": embeddings,
        "model": model_name,
        "count": len(embeddings)
    }
    
    print(json.dumps(output))


if __name__ == "__main__":
    main()

