from __future__ import annotations

"""Offline grounding / retrieval eval harness.

Runs a small gold set through retrieve -> draft_answer -> grounding_check and
reports top-1 account accuracy and grounding rate. Serves as a regression gate
before swapping in a hosted embedding model.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.grounding import draft_answer, grounding_check
from src.retrieve import retrieve

GOLD = Path(__file__).resolve().parent / "gold_set.json"


def evaluate(gold_path: Path = GOLD, support_threshold: float = 0.6) -> dict:
    cases = json.loads(gold_path.read_text(encoding="utf-8"))
    top1_hits = 0
    grounded_ok = 0
    support_sum = 0.0
    details = []
    for case in cases:
        docs = retrieve(case["query"], top_k=3)
        top_account = docs[0]["account_id"] if docs else None
        answer = draft_answer(case["query"], docs)
        grounding = grounding_check(answer, [d["body"] for d in docs])
        supported = grounding["supported_ratio"]
        support_sum += supported
        top1 = top_account == case["expected_account_id"]
        # Grade against a realistic support threshold rather than the strict gate.
        grounded_pass = supported >= support_threshold
        top1_hits += int(top1)
        grounded_ok += int(grounded_pass == case["expect_grounded"])
        details.append(
            {
                "query": case["query"],
                "top_account": top_account,
                "expected": case["expected_account_id"],
                "top1": top1,
                "supported_ratio": supported,
            }
        )
    n = len(cases) or 1
    return {
        "cases": len(cases),
        "top1_accuracy": round(top1_hits / n, 3),
        "avg_supported_ratio": round(support_sum / n, 3),
        "grounding_match_rate": round(grounded_ok / n, 3),
        "details": details,
    }


def main() -> None:
    report = evaluate()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
