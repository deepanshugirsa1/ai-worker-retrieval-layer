from __future__ import annotations

from src.grounding import draft_answer, grounding_check
from src.rerank import rerank
from src.retrieve import retrieve


TOOLS = [
    {
        "name": "search_customer_knowledge",
        "description": "Retrieve lead/account enrichment docs for an AI worker query",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
                "rerank": {"type": "boolean", "default": True},
            },
            "required": ["query"],
        },
    },
    {
        "name": "reason_over_customer_data",
        "description": "Retrieve + draft a grounded answer with citations",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "summarize_account",
        "description": "Summarize what is known about a single account with grounding",
        "input_schema": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        },
    },
]


def call_tool(name: str, arguments: dict) -> dict:
    if name == "search_customer_knowledge":
        docs = retrieve(arguments["query"], top_k=int(arguments.get("top_k", 5)))
        if arguments.get("rerank", True):
            docs = rerank(arguments["query"], docs)
        return {"results": docs}
    if name == "reason_over_customer_data":
        docs = retrieve(arguments["query"])
        answer = draft_answer(arguments["query"], docs)
        grounding = grounding_check(answer, [d["body"] for d in docs])
        return {"answer": answer, "docs": docs, "grounding": grounding}
    if name == "summarize_account":
        account_id = arguments["account_id"]
        docs = [
            d
            for d in retrieve(account_id, top_k=10, min_score=0.0)
            if d["account_id"] == account_id
        ]
        answer = draft_answer(f"Summarize account {account_id}", docs)
        grounding = grounding_check(answer, [d["body"] for d in docs])
        return {"account_id": account_id, "answer": answer, "docs": docs, "grounding": grounding}
    raise ValueError(f"unknown tool: {name}")
