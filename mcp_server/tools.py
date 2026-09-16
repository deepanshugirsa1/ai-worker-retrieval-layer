from __future__ import annotations

from src.grounding import draft_answer, grounding_check
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
]


def call_tool(name: str, arguments: dict) -> dict:
    if name == "search_customer_knowledge":
        docs = retrieve(arguments["query"], top_k=int(arguments.get("top_k", 5)))
        return {"results": docs}
    if name == "reason_over_customer_data":
        docs = retrieve(arguments["query"])
        answer = draft_answer(arguments["query"], docs)
        grounding = grounding_check(answer, [d["body"] for d in docs])
        return {"answer": answer, "docs": docs, "grounding": grounding}
    raise ValueError(f"unknown tool: {name}")
