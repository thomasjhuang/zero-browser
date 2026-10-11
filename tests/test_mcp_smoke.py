"""Do not confuse MCP transport success with a successful browser goal."""

import json

from scripts.codex_mcp_smoke import smoke_succeeded


def test_failed_or_unverified_mcp_call_cannot_pass():
    assert not smoke_succeeded([{"status": "failed", "error": {"message": "Approval required"}}])
    call = {"status": "completed", "server": "zero_browser", "tool": "run_browser_goal",
            "result": {"content": [{"type": "text", "text": '{"successful_run": false}'}]}}
    assert not smoke_succeeded([call])
    call["result"]["content"][0]["text"] = json.dumps({
        "successful_run": True, "outcome_verified": True,
        "final_page": {"url": "http://localhost/#casa-flora", "text": "Casa Flora"},
    })
    assert smoke_succeeded([call])
    assert not smoke_succeeded([call, call])
