# ClickHouse production notes

Local demo uses DuckDB. For production, create `knowledge_docs` and `embeddings` on ClickHouse
MergeTree and point `configs/retrieval.yaml` `lake.path` / client DSN at the cluster.

Vector search can move to ClickHouse cosine distance UDFs or a dedicated vector index.
