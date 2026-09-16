from __future__ import annotations

from src.embeddings import embed
from src.lake import connect, init_schema


def rebuild_index(dim: int = 64) -> int:
    con = connect()
    init_schema(con)
    docs = con.execute("SELECT doc_id, title, body FROM knowledge_docs").fetchall()
    con.execute("DELETE FROM embeddings")
    for doc_id, title, body in docs:
        vector = embed(f"{title}\n{body}", dim=dim)
        con.execute(
            "INSERT INTO embeddings (doc_id, vector) VALUES (?, ?)",
            [doc_id, vector],
        )
    return len(docs)
