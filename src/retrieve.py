from __future__ import annotations

from src.embeddings import cosine, embed
from src.lake import connect, init_schema


def retrieve(query: str, top_k: int = 5, min_score: float = 0.15, dim: int = 64) -> list[dict]:
    con = connect()
    init_schema(con)
    q = embed(query, dim=dim)
    rows = con.execute(
        """
        SELECT d.doc_id, d.account_id, d.title, d.body, d.source, e.vector
        FROM knowledge_docs d
        JOIN embeddings e ON d.doc_id = e.doc_id
        """
    ).fetchall()
    scored = []
    for doc_id, account_id, title, body, source, vector in rows:
        score = cosine(q, list(vector))
        if score >= min_score:
            scored.append(
                {
                    "doc_id": doc_id,
                    "account_id": account_id,
                    "title": title,
                    "body": body,
                    "source": source,
                    "score": round(score, 4),
                }
            )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
