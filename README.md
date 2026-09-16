# AI-Worker Retrieval Layer (MCP + Vector Search + RAG)

Retrieval infrastructure that gives **AI workers** governed access to customer knowledge
via **MCP servers**, **FastAPI** tool APIs, embeddings, vector search, and RAG grounding checks
over a ClickHouse-style data lake (DuckDB locally).

> **Status: ~65% complete.** MCP tools, FastAPI, embedding index, retrieval, grounding checks,
> and demo scripts run locally. Production ClickHouse + hosted embedding model + auth are planned.

## Implemented

- Two tool-callable interfaces: `search_customer_knowledge` and
  `reason_over_customer_data`
- FastAPI endpoints for retrieval, grounded reasoning, and index rebuilds
- Deterministic local embeddings and cosine-similarity retrieval for repeatable demos
- DuckDB knowledge and retrieval logs for auditable document IDs, scores, and outcomes
- Grounding checks that reject answers unsupported by retrieved context
- Docker packaging, local demo data, automated tests, and GitHub Actions CI

## Architecture

```text
AI worker / agent
       |
  MCP tools or FastAPI
       |
Retrieval + grounding checks
       |
Embedding index + DuckDB lake
       |
Knowledge documents + retrieval audit log
```

## Quickstart

```bash
python -m venv .venv && .venv\\Scripts\\activate
pip install -r requirements.txt
python data/seed_knowledge.py
python run_demo.py
uvicorn src.api.app:app --reload --port 8090
python -m mcp_server.server
```

## Example API request

```bash
curl -X POST http://localhost:8090/reason \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Which customer accounts need follow-up?\",\"top_k\":5}"
```

The response includes the drafted answer, retrieved source records and scores, and the
grounding result. The local hashing embedder keeps the demo deterministic; it is not
presented as a production embedding model.
