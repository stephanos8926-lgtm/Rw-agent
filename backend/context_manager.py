import json
import logging
from typing import Dict, Any, Optional

class ContextManager:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        logging.info("ContextManager initialized.")

    def set(self, key: str, value: Any):
        self._cache[key] = value
        logging.info(f"Context updated for key: {key}")

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def clear_cache(self):
        self._cache.clear()
        logging.info("Context cache cleared.")

context_manager = ContextManager()
