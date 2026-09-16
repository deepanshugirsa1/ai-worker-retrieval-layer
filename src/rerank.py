from __future__ import annotations

"""Lightweight lexical reranker.

Vector similarity is recall-oriented; a cheap lexical-overlap signal sharpens
precision on the top candidates. In production this interface would front a
cross-encoder, but the blend stays deterministic and offline for the demo.
"""

from src.embeddings import tokenize


def _lexical_overlap(query: str, text: str) -> float:
    q = set(tokenize(query))
    if not q:
        return 0.0
    d = set(tokenize(text))
    return len(q & d) / len(q)


def rerank(query: str, docs: list[dict], alpha: float = 0.7) -> list[dict]:
    """Blend vector score with lexical overlap into ``rerank_score``.

    ``alpha`` weights the original vector score; ``1 - alpha`` weights lexical
    overlap against the doc title + body.
    """
    out: list[dict] = []
    for d in docs:
        text = f"{d.get('title', '')} {d.get('body', '')}"
        lexical = _lexical_overlap(query, text)
        blended = alpha * float(d.get("score", 0.0)) + (1 - alpha) * lexical
        item = dict(d)
        item["lexical_overlap"] = round(lexical, 4)
        item["rerank_score"] = round(blended, 4)
        out.append(item)
    out.sort(key=lambda x: x["rerank_score"], reverse=True)
    return out
