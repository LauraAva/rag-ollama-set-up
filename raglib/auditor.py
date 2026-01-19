import json
from ollama import chat
from .config import AUDIT_MODEL

AUDIT_PROMPT = """You are an auditor for a RAG system.
Given Question, Context, and Answer, grade whether the answer is supported ONLY by the context.

Return STRICT JSON:
{
  "groundedness": 0-5,
  "completeness": 0-5,
  "safety": 0-5,
  "verdict": "PASS" or "FAIL",
  "rationale": "short reason"
}

Rules:
- FAIL groundedness if answer includes facts not in context.
- If context is insufficient, best answer is a refusal ("I don't have enough information in the knowledge base.").
"""

def audit(question: str, context: str, answer: str) -> dict:
    msg = f"{AUDIT_PROMPT}\n\nQuestion:\n{question}\n\nContext:\n{context}\n\nAnswer:\n{answer}\n"
    resp = chat(model=AUDIT_MODEL, messages=[{"role": "user", "content": msg}], options={"temperature": 0})
    txt = resp["message"]["content"].strip()

    try:
        return json.loads(txt)
    except Exception:
        return {
            "groundedness": 0,
            "completeness": 0,
            "safety": 0,
            "verdict": "FAIL",
            "rationale": f"Auditor returned non-JSON: {txt[:200]}",
        }