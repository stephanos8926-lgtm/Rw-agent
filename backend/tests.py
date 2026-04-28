import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.semantic_cache import semantic_cache, compute_context_hash
from google import genai
import time

def run_experiment():
    print("Starting Semantic Cache Threshold Experiment...")
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    context_mock = [{"role": "user", "content": "hello"}]
    ctx_hash = compute_context_hash(context_mock)

    # 1. Warm the cache
    semantic_cache.store(client, "list all files in src", ctx_hash, {"role": "tool", "content": "src/ main.py utils.py"})
    semantic_cache.store(client, "execute tests on backend", ctx_hash, {"role": "tool", "content": "tests passed"})

    # 2. Test exact matches
    print("\n[Testing Exact Matches]")
    semantic_cache.search(client, "list all files in src", ctx_hash)
    
    # 3. Test highly similar matches
    print("\n[Testing High Similarity]")
    semantic_cache.search(client, "list files in src folder", ctx_hash)
    semantic_cache.search(client, "run tests on the backend", ctx_hash)
    
    # 4. Test low similarity / different intent
    print("\n[Testing Low Similarity]")
    semantic_cache.search(client, "read content of main.py", ctx_hash)
    semantic_cache.search(client, "delete all files in src", ctx_hash)

if __name__ == "__main__":
    run_experiment()
