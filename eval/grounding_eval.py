from __future__ import annotations

"""Offline retrieval and grounding evaluation harness.

Expands a versioned gold set into individual cases, runs retrieval, lexical
reranking, answer drafting, and grounding checks, then reports quality metrics
and regression-gate status. The deterministic local embedder keeps CI repeatable.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.grounding import draft_answer, grounding_check
from src.rerank import rerank
from src.retrieve import retrieve

GOLD = Path(__file__).resolve().parent / "gold_set.json"
DEFAULT_THRESHOLDS = {
    "top1_accuracy": 0.90,
    "recall_at_3": 0.98,
    "mean_reciprocal_rank": 0.94,
    "avg_supported_ratio": 0.60,
    "grounding_match_rate": 0.95,
}


def load_cases(gold_path: Path = GOLD) -> list[dict]:
    """Expand grouped account fixtures into independently scored queries."""
    groups = json.loads(gold_path.read_text(encoding="utf-8"))
    cases: list[dict] = []
    for group in groups:
        expected = group["expected_account_id"]
        for query in group["queries"]:
            cases.append({"query": query, "expected_account_id": expected})
    return cases


def _account_ranking(docs: list[dict]) -> list[str]:
    """Return account IDs in rank order, deduplicating multiple account docs."""
    ranked: list[str] = []
    for doc in docs:
        account_id = doc["account_id"]
        if account_id not in ranked:
            ranked.append(account_id)
    return ranked


def evaluate(
    gold_path: Path = GOLD,
    support_threshold: float = 0.6,
    thresholds: dict[str, float] | None = None,
) -> dict:
    cases = load_cases(gold_path)
    thresholds = thresholds or DEFAULT_THRESHOLDS
    top1_hits = recall_at_3_hits = grounded_hits = 0
    reciprocal_rank_sum = support_sum = 0.0
    details: list[dict] = []

    for case in cases:
        candidates = retrieve(case["query"], top_k=10, min_score=-1.0)
        docs = rerank(case["query"], candidates, alpha=0.55)
        account_ranking = _account_ranking(docs)
        expected = case["expected_account_id"]
        rank = account_ranking.index(expected) + 1 if expected in account_ranking else None

        answer_docs = docs[:3]
        answer = draft_answer(case["query"], answer_docs)
        grounding = grounding_check(answer, [d["body"] for d in answer_docs])
        supported = grounding["supported_ratio"]

        top1 = rank == 1
        recalled_at_3 = rank is not None and rank <= 3
        grounded_pass = supported >= support_threshold

        top1_hits += int(top1)
        recall_at_3_hits += int(recalled_at_3)
        reciprocal_rank_sum += 1.0 / rank if rank else 0.0
        support_sum += supported
        grounded_hits += int(grounded_pass)

        details.append(
            {
                "query": case["query"],
                "expected_account_id": expected,
                "top_account_id": account_ranking[0] if account_ranking else None,
                "expected_rank": rank,
                "top1": top1,
                "recalled_at_3": recalled_at_3,
                "supported_ratio": supported,
                "grounded": grounded_pass,
            }
        )

    n = max(len(cases), 1)
    metrics = {
        "top1_accuracy": round(top1_hits / n, 3),
        "recall_at_3": round(recall_at_3_hits / n, 3),
        "mean_reciprocal_rank": round(reciprocal_rank_sum / n, 3),
        "avg_supported_ratio": round(support_sum / n, 3),
        "grounding_match_rate": round(grounded_hits / n, 3),
    }
    gates = {
        metric: {
            "actual": metrics[metric],
            "minimum": minimum,
            "passed": metrics[metric] >= minimum,
        }
        for metric, minimum in thresholds.items()
    }
    return {
        "cases": len(cases),
        **metrics,
        "regression_passed": all(gate["passed"] for gate in gates.values()),
        "gates": gates,
        "details": details,
    }


def main() -> None:
    report = evaluate()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
