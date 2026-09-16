from __future__ import annotations

from src.lake import connect, init_schema
from src.providers import get_embedding_provider


def rebuild_index(dim: int = 64) -> int:
    con = connect()
    init_schema(con)
    provider = get_embedding_provider(dim=dim)
    docs = con.execute("SELECT doc_id, title, body FROM knowledge_docs").fetchall()
    con.execute("DELETE FROM embeddings")
    for doc_id, title, body in docs:
        vector = provider.embed(f"{title}\n{body}")
        con.execute(
            "INSERT INTO embeddings (doc_id, vector) VALUES (?, ?)",
            [doc_id, vector],
        )
    return len(docs)
