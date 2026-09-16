from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.grounding import draft_answer, grounding_check
from src.index import rebuild_index
from src.lake import connect, init_schema
from src.retrieve import retrieve

app = FastAPI(title="AI Worker Retrieval API", version="0.1.0")


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=20)


class ReasonRequest(BaseModel):
    query: str
    top_k: int = 5


@app.on_event("startup")
def _startup() -> None:
    init_schema(connect())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/retrieve")
def api_retrieve(req: RetrieveRequest):
    docs = retrieve(req.query, top_k=req.top_k)
    return {"query": req.query, "results": docs}


@app.post("/reason")
def api_reason(req: ReasonRequest):
    docs = retrieve(req.query, top_k=req.top_k)
    answer = draft_answer(req.query, docs)
    grounding = grounding_check(answer, [d["body"] for d in docs])
    con = connect()
    con.execute(
        """
        INSERT INTO retrieval_log (query, doc_ids, scores, grounded)
        VALUES (?, ?, ?, ?)
        """,
        [
            req.query,
            [d["doc_id"] for d in docs],
            [d["score"] for d in docs],
            grounding["grounded"],
        ],
    )
    return {"answer": answer, "docs": docs, "grounding": grounding}


@app.post("/reindex")
def api_reindex():
    n = rebuild_index()
    return {"indexed": n}
