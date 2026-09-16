from __future__ import annotations

from pathlib import Path

import duckdb

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "processed" / "knowledge.duckdb"


def connect(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    path = db_path or DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge_docs (
            doc_id VARCHAR PRIMARY KEY,
            account_id VARCHAR,
            title VARCHAR,
            body VARCHAR,
            source VARCHAR,
            updated_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS embeddings (
            doc_id VARCHAR PRIMARY KEY,
            vector FLOAT[]
        );
        CREATE TABLE IF NOT EXISTS retrieval_log (
            query VARCHAR,
            doc_ids VARCHAR[],
            scores FLOAT[],
            grounded BOOLEAN,
            created_at TIMESTAMP DEFAULT current_timestamp
        );
        """
    )
