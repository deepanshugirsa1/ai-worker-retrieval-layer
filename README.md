# AI-Worker Retrieval Layer (MCP + Vector Search + RAG)

Retrieval infrastructure that gives **AI workers** governed access to customer knowledge
via **MCP servers**, **FastAPI** tool APIs, embeddings, vector search, and RAG grounding checks
over a ClickHouse-style data lake (DuckDB locally).

> **Status: ~65% complete.** MCP tools, FastAPI, embedding index, retrieval, grounding checks,
> and demo scripts run locally. Production ClickHouse + hosted embedding model + auth are planned.

## Quickstart

```bash
python -m venv .venv && .venv\\Scripts\\activate
pip install -r requirements.txt
python data/seed_knowledge.py
python run_demo.py
uvicorn src.api.app:app --reload --port 8090
python -m mcp_server.server
```
