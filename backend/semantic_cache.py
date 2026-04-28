import json
import hashlib
from typing import Any, Dict, List, Optional
import chromadb

CACHE_DIR = "chroma_cache_db"

class SemanticCache:
    """
    A semantic cache utilizing Google Gemini's embedding model to cache LLM 
    responses and tool outputs dynamically based on input similarity, backed by ChromaDB.
    """
    def __init__(self, threshold: float = 0.98):
        self.threshold = threshold
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=CACHE_DIR)
        
        # Create or get collection. We use cosine distance.
        self.collection = self.client.get_or_create_collection(
            name="semantic_cache",
            metadata={"hnsw:space": "cosine"}
        )

        # Tracking thresholds for experimentation
        self.test_thresholds = [0.95, 0.96, 0.97, 0.98, 0.99]
        self.stats = { t: {"hits": 0, "misses": 0} for t in self.test_thresholds }

    def get_embedding(self, client, text: str) -> List[float]:
        try:
            response = client.models.embed_content(
                model="text-embedding-004",
                contents=text,
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Embedding error: {e}")
            return []

    def log_stats(self):
        print("\n--- Semantic Cache Threshold Experiment Stats ---")
        for t in self.test_thresholds:
            hits = self.stats[t]["hits"]
            misses = self.stats[t]["misses"]
            total = hits + misses
            rate = (hits / total * 100) if total > 0 else 0
            print(f"Threshold {t:.2f}: Hits={hits}, Misses={misses}, Hit Rate={rate:.2f}%")
        print("------------------------------------------------\n")

    def search(self, client, query_text: str, context_hash: str) -> Optional[Dict[str, Any]]:
        """
        Searches the cache for a highly similar query within the same context hash using ChromaDB.
        """
        full_query = f"Context[{context_hash}]\nQuery: {query_text}"
        query_vec = self.get_embedding(client, full_query)
        if not query_vec:
            return None

        # Query ChromaDB. We want to find the nearest neighbor.
        try:
            results = self.collection.query(
                query_embeddings=[query_vec],
                n_results=1
            )
        except Exception as e:
            print(f"ChromaDB Query Error: {e}")
            return None
            
        if not results["distances"] or not len(results["distances"]) or not len(results["distances"][0]):
            return None
            
        # ChromaDB cosine distance is 1 - cosine_similarity. So cosine_similarity = 1 - distance
        distance = results["distances"][0][0]
        similarity = 1.0 - distance
        
        # Track experimental stats
        for t in self.test_thresholds:
            if similarity >= t:
                self.stats[t]["hits"] += 1
            else:
                self.stats[t]["misses"] += 1
        
        self.log_stats()

        if similarity >= self.threshold:
            print(f"[Semantic Cache HIT] Similarity Score: {similarity:.4f} (Threshold: {self.threshold})")
            # Since we store JSON in metadata
            response_json = results["metadatas"][0][0].get("response")
            return json.loads(response_json) if response_json else None

        print(f"[Semantic Cache MISS] Best Score: {similarity:.4f} (Threshold: {self.threshold})")
        return None

    def store(self, client, query_text: str, context_hash: str, response: Dict[str, Any]):
        full_query = f"Context[{context_hash}]\nQuery: {query_text}"
        query_vec = self.get_embedding(client, full_query)
        if not query_vec:
            return
            
        doc_id = hashlib.sha256(full_query.encode('utf-8')).hexdigest()

        try:
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[query_vec],
                documents=[full_query],
                metadatas=[{"response": json.dumps(response)}]
            )
        except Exception as e:
            print(f"ChromaDB Upsert Error: {e}")

semantic_cache = SemanticCache()

def compute_context_hash(messages: list) -> str:
    """Computes a SHA-256 hash of the conversational history and state to enforce context locality."""
    # We stringify the messages except the very last one (which is the current query)
    history = messages[:-1]
    history_str = json.dumps(history, sort_keys=True)
    return hashlib.sha256(history_str.encode('utf-8')).hexdigest()
