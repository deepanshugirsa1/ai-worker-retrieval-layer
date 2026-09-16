from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.index import rebuild_index
from src.lake import connect, init_schema

ACCOUNTS = [
    {
        "account_id": "acc_acme",
        "name": "Acme",
        "industry": "SaaS",
        "employees": 120,
        "priority": "growth",
        "stage": "lead",
        "need": "AI SDR outreach",
        "activity": "opened the pricing page twice this week",
    },
    {
        "account_id": "acc_globex",
        "name": "Globex",
        "industry": "manufacturing",
        "employees": 5000,
        "priority": "enterprise",
        "stage": "opportunity",
        "need": "supply-chain forecasting",
        "activity": "requested a security review",
    },
    {
        "account_id": "acc_initech",
        "name": "Initech",
        "industry": "enterprise software",
        "employees": 850,
        "priority": "strategic",
        "stage": "opportunity",
        "need": "retrieval-backed AI worker follow-up",
        "activity": "completed a technical discovery call",
    },
    {
        "account_id": "acc_umbrella",
        "name": "Umbrella",
        "industry": "biotechnology",
        "employees": 2300,
        "priority": "enterprise",
        "stage": "evaluation",
        "need": "governed research-document search",
        "activity": "downloaded the compliance whitepaper",
    },
    {
        "account_id": "acc_hooli",
        "name": "Hooli",
        "industry": "consumer technology",
        "employees": 12000,
        "priority": "strategic",
        "stage": "negotiation",
        "need": "customer-support summarization",
        "activity": "ran a product pilot with twenty users",
    },
    {
        "account_id": "acc_stark",
        "name": "Stark Industries",
        "industry": "aerospace",
        "employees": 18000,
        "priority": "enterprise",
        "stage": "discovery",
        "need": "engineering knowledge retrieval",
        "activity": "requested architecture documentation",
    },
    {
        "account_id": "acc_wayne",
        "name": "Wayne Enterprises",
        "industry": "industrial conglomerate",
        "employees": 42000,
        "priority": "strategic",
        "stage": "evaluation",
        "need": "risk-analysis automation",
        "activity": "scheduled an executive workshop",
    },
    {
        "account_id": "acc_wonka",
        "name": "Wonka Industries",
        "industry": "consumer goods",
        "employees": 640,
        "priority": "growth",
        "stage": "lead",
        "need": "quality-incident classification",
        "activity": "viewed the API documentation",
    },
    {
        "account_id": "acc_tyrell",
        "name": "Tyrell Corporation",
        "industry": "robotics",
        "employees": 7600,
        "priority": "enterprise",
        "stage": "opportunity",
        "need": "robotics telemetry analysis",
        "activity": "submitted a data-governance questionnaire",
    },
    {
        "account_id": "acc_cyberdyne",
        "name": "Cyberdyne Systems",
        "industry": "autonomous systems",
        "employees": 1400,
        "priority": "strategic",
        "stage": "discovery",
        "need": "safety-evaluation reporting",
        "activity": "requested an evaluation-framework demo",
    },
]


def build_docs() -> list[dict]:
    docs: list[dict] = []
    for account in ACCOUNTS:
        slug = account["account_id"].removeprefix("acc_")
        docs.extend(
            [
                {
                    "doc_id": f"doc-{slug}-profile",
                    "account_id": account["account_id"],
                    "title": f"{account['name']} account profile",
                    "body": (
                        f"{account['name']} is a {account['industry']} company with "
                        f"{account['employees']} employees. The account priority is "
                        f"{account['priority']} and the lifecycle stage is {account['stage']}."
                    ),
                    "source": "crm_enrichment",
                },
                {
                    "doc_id": f"doc-{slug}-activity",
                    "account_id": account["account_id"],
                    "title": f"{account['name']} activity and needs",
                    "body": (
                        f"{account['name']} needs {account['need']} and recently "
                        f"{account['activity']}. This note is approved for customer follow-up."
                    ),
                    "source": "product_events",
                },
            ]
        )
    return docs


DOCS = build_docs()


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
