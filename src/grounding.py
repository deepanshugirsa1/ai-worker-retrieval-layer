from __future__ import annotations

import re

from src.embeddings import tokenize


def grounding_check(answer: str, contexts: list[str], max_unsupported_ratio: float = 0.25) -> dict:
    """Heuristic RAG grounding: fraction of answer tokens supported by retrieved context."""
    answer_toks = set(tokenize(answer))
    if not answer_toks:
        return {"grounded": False, "supported_ratio": 0.0, "reason": "empty_answer"}
    ctx = " ".join(contexts).lower()
    supported = {t for t in answer_toks if t in ctx}
    ratio = len(supported) / len(answer_toks)
    unsupported = 1.0 - ratio
    grounded = unsupported <= max_unsupported_ratio
    return {
        "grounded": grounded,
        "supported_ratio": round(ratio, 3),
        "unsupported_ratio": round(unsupported, 3),
        "reason": "ok" if grounded else "too_many_unsupported_tokens",
    }


def draft_answer(query: str, docs: list[dict]) -> str:
    if not docs:
        return "No supporting customer knowledge found."
    cites = "; ".join(f"[{d['doc_id']}] {d['title']}" for d in docs[:3])
    snippets = " ".join(d["body"][:180] for d in docs[:2])
    return f"Based on retrieved account knowledge ({cites}): {snippets}"
