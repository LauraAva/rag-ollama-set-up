from ollama import embed
from pgvector.psycopg import Vector
from .config import EMBED_MODEL

def embed_text(text: str) -> Vector:
    r = embed(model=EMBED_MODEL, input=text)
    v = r["embeddings"][0] if isinstance(r["embeddings"][0], list) else r["embeddings"]
    return Vector(v)