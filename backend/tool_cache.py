import time
from typing import Any, Dict

class ToolCache:
    def __init__(self, ttl_seconds: int = 5):
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get_cache_key(self, func_name: str, args: dict) -> str:
        # Create a stable string representation
        args_str = str(sorted(args.items()))
        return f"{func_name}:{args_str}"

    def get(self, func_name: str, args: dict) -> Any:
        key = self.get_cache_key(func_name, args)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] <= self.ttl_seconds:
                print(f"[Tool Cache HIT] {func_name}")
                return entry["result"]
            else:
                del self.cache[key]
        return None

    def store(self, func_name: str, args: dict, result: Any):
        key = self.get_cache_key(func_name, args)
        self.cache[key] = {
            "timestamp": time.time(),
            "result": result
        }

tool_cache = ToolCache(ttl_seconds=5)
