from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    subprocess.check_call([sys.executable, str(ROOT / "data" / "seed_knowledge.py")])
    sys.path.insert(0, str(ROOT))
    from src.grounding import draft_answer, grounding_check
    from src.retrieve import retrieve

    query = "What do we know about Acme lead alex and AI SDR interest?"
    docs = retrieve(query, top_k=3)
    answer = draft_answer(query, docs)
    grounding = grounding_check(answer, [d["body"] for d in docs])
    print("QUERY:", query)
    for d in docs:
        print(f"  {d['score']:.3f} {d['doc_id']} {d['title']}")
    print("ANSWER:", answer)
    print("GROUNDING:", grounding)
    print("API: uvicorn src.api.app:app --port 8090")
    print("MCP: python -m mcp_server.server")


if __name__ == "__main__":
    main()
