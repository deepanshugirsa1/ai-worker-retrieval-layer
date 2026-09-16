"""Minimal MCP-style stdio JSON tool server for AI workers / Claude Code."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp_server.tools import TOOLS, call_tool


def handle(msg: dict) -> dict:
    method = msg.get("method")
    req_id = msg.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = msg.get("params", {})
        result = call_tool(params["name"], params.get("arguments", {}))
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


def main() -> None:
    print(json.dumps({"jsonrpc": "2.0", "method": "server/ready", "params": {"tools": len(TOOLS)}}))
    sys.stdout.flush()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        resp = handle(msg)
        print(json.dumps(resp))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
