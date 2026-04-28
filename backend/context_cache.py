from google import genai
from google.genai import types
import os

class ContextCacheManager:
    """
    Manages Google Gemini API Context Caching for large static contexts like 
    AST project maps and core system instructions.
    """
    def __init__(self):
        self.cached_content_name = None
        self.last_context_mtime = 0

    def get_or_create_cache(self, client: genai.Client, system_instruction: str) -> str:
        """
        Returns the cache name if successfully created/retrieved, else None.
        """
        if not os.path.exists("context.json"):
            return None

        mtime = os.path.getmtime("context.json")
        if self.cached_content_name and self.last_context_mtime >= mtime:
             # Cache is still valid based on file modification time
             return self.cached_content_name

        try:
            with open("context.json", "r", encoding="utf-8") as f:
                context_str = "Project Structure Context:\n" + f.read()

            cache = client.caches.create(
                model="gemini-2.5-flash",
                config=types.CreateCachedContentConfig(
                    system_instruction=system_instruction,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(context_str)])],
                    ttl="3600s", # 1 hour cache duration
                )
            )
            self.cached_content_name = cache.name
            self.last_context_mtime = mtime
            print(f"[Context Cache HIT (google.genai)] ID: {self.cached_content_name}")
            return self.cached_content_name
            
        except Exception as e:
            # Context caching typically requires >= 32k tokens. For smaller projects it will throw an API error.
            print(f"[Context Cache BYPASSED] Context likely too small (<32k SDK limit) or API error: {e}")
            self.cached_content_name = None
            return None

context_cache_manager = ContextCacheManager()
