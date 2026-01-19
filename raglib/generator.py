from ollama import chat
from .config import CHAT_MODEL

def generate_answer(question: str, rows):
    # rows: (id, content, distance)
    chunk_ids = [r[0] for r in rows]
    context = "\n\n".join([f"[chunk {rid}]\n{txt}" for rid, txt, _dist in rows])

    prompt = f"""You are a QA system. Use ONLY the context to answer.
If the context is not enough, say: "I don't have enough information in the knowledge base."

Context:
{context}

Question: {question}

Answer (short and direct):"""

    resp = chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2},
    )
    return resp["message"]["content"], chunk_ids, context