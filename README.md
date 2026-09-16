# AI-Worker Retrieval Layer (MCP + Vector Search + RAG)

Retrieval infrastructure that gives **AI workers** governed access to customer knowledge
via **MCP servers**, **FastAPI** tool APIs, embeddings, vector search, and RAG grounding checks
over a ClickHouse-style data lake (DuckDB locally).

> **Status: evaluation milestone complete.** MCP tools, FastAPI, embedding index, retrieval,
> grounding checks, a 50-query gold set, regression gates, tests, and demo scripts run locally.
> Production ClickHouse, hosted embeddings, authentication, and tenant isolation remain planned.

## What works today vs. planned

| Area | Status | Notes |
|------|--------|-------|
| MCP tool server | Done | `search_customer_knowledge`, `reason_over_customer_data`, `summarize_account` |
| FastAPI retrieval API | Done | `/retrieve`, `/reason`, `/reindex`, `/health` with audit logging |
| Pluggable embedding provider | Done | Offline hashing default; hosted provider stubbed behind an interface |
| Vector search over ClickHouse-style lake | Done | DuckDB `knowledge_docs` + `embeddings` + cosine top-k |
| Lexical reranker | Done | Blends vector score with lexical overlap for precision |
| Query-embedding cache | Done | In-process LRU with hit-rate stats (Redis in prod) |
| RAG grounding checks | Done | Rejects answers unsupported by retrieved context |
| Offline eval harness | Done | 50-query gold set with top-1, recall@3, MRR, grounding metrics, and regression gates |
| Tests + CI | Done | pytest suite + GitHub Actions |
| Hosted embedding model | Planned | Swap provider to sentence-transformers / OpenAI |
| Production ClickHouse vector search | Planned | Or a dedicated vector DB |
| Full MCP handshake (initialize/notifications) | Planned | Demo exposes tool call/list |
| Auth + tenant isolation | Planned | Multi-customer AI worker governance |

## Implemented

- Two tool-callable interfaces: `search_customer_knowledge` and
  `reason_over_customer_data`
- FastAPI endpoints for retrieval, grounded reasoning, and index rebuilds
- Deterministic local embeddings and cosine-similarity retrieval for repeatable demos
- DuckDB knowledge and retrieval logs for auditable document IDs, scores, and outcomes
- Grounding checks that reject answers unsupported by retrieved context
- Docker packaging, local demo data, automated tests, and GitHub Actions CI

## Reproducible evaluation

The versioned benchmark contains **50 unique queries across 10 synthetic customer
accounts**. It tests retrieval by company, firmographics, lifecycle stage, customer
need, and recent activity. Run it locally with:

```bash
python data/seed_knowledge.py
python -m eval.grounding_eval
python -m pytest -q
```

Measured with the deterministic offline hashing embedder and lexical reranker:

| Metric | Result | Regression gate |
|---|---:|---:|
| Top-1 account accuracy | **98.0%** | ≥ 90% |
| Recall@3 | **98.0%** | ≥ 98% |
| Mean reciprocal rank | **0.982** | ≥ 0.940 |
| Average supported-token ratio | **85.2%** | ≥ 60% |
| Grounding-gate pass rate | **100%** | ≥ 95% |

All regression gates pass, and the test suite reports **9 passing tests**. The
single retrieval miss is preserved in the case-level output rather than hidden.
These results characterize the bundled synthetic benchmark; they are not claims
about production traffic or a hosted embedding model.

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
