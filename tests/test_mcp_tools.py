from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_seed_and_retrieve():
    subprocess.check_call([sys.executable, str(ROOT / "data" / "seed_knowledge.py")])
    from mcp_server.tools import call_tool

    out = call_tool("search_customer_knowledge", {"query": "Acme lead", "top_k": 2})
    assert "results" in out
    assert len(out["results"]) >= 1
