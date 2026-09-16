from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.index import rebuild_index
from src.lake import connect, init_schema

DOCS = [
    {
        "doc_id": "doc-acme-001",
        "account_id": "acc_acme",
        "title": "Acme account overview",
        "body": "Acme is a SaaS lead with 120 employees. Primary contact alex@acme.io. Interested in AI SDR outreach.",
        "source": "crm_enrichment",
    },
    {
        "doc_id": "doc-acme-002",
        "account_id": "acc_acme",
        "title": "Acme recent activity",
        "body": "Opened pricing page twice this week. HubSpot lifecycle stage is lead. Salesforce status Open.",
        "source": "product_events",
    },
    {
        "doc_id": "doc-globex-001",
        "account_id": "acc_globex",
        "title": "Globex firmographics",
        "body": "Globex manufacturing company ~5000 employees. Contact jordan@globex.com. Priority enterprise account.",
        "source": "crm_enrichment",
    },
    {
        "doc_id": "doc-initech-001",
        "account_id": "acc_initech",
        "title": "Initech opportunity notes",
        "body": "Initech enterprise software. Contact sam@initech.com. Deal stage opportunity. Needs retrieval-backed AI worker follow-up.",
        "source": "crm",
    },
]


def main() -> None:
    con = connect()
    init_schema(con)
    con.execute("DELETE FROM knowledge_docs")
    now = datetime.now(timezone.utc).isoformat()
    for d in DOCS:
        con.execute(
            """
            INSERT INTO knowledge_docs (doc_id, account_id, title, body, source, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [d["doc_id"], d["account_id"], d["title"], d["body"], d["source"], now],
        )
    n = rebuild_index()
    print(f"seeded {len(DOCS)} docs, indexed {n}")


if __name__ == "__main__":
    main()
