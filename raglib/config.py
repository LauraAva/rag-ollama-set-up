import os

def env_int(key: str, default: int) -> int:
    v = os.getenv(key)
    return default if v is None else int(v)

def env_float(key: str, default: float) -> float:
    v = os.getenv(key)
    return default if v is None else float(v)

EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
CHAT_MODEL  = os.getenv("CHAT_MODEL", "gemma3:4b")
AUDIT_MODEL = os.getenv("AUDIT_MODEL", CHAT_MODEL)

TOP_K = env_int("TOP_K", 5)

# cosine distance: smaller = more similar
RELEVANCE_MAX_DISTANCE = env_float("RELEVANCE_MAX_DISTANCE", 0.25)