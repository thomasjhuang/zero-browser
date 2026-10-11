# 18 Codex through local browser MCP

Owner: Codex MCP chat. Scope: the MCP adapter and one controlled integration experiment.

## Why

Codex must delegate a browser goal to a local MCP server. Local Qwen must choose the browser actions.

## Do

- Expose the existing bounded browser pipeline through one MCP tool.
- Keep the model, browser profile, and inference local.
- Test Codex with native browser tools disabled and only this MCP server available.
- Preserve existing work and runtime safeguards.

## Verify

- Use one fixed local fixture goal and independent final-page assertions.
- Record the actual MCP call, outcome, elapsed time, and sampled worker memory in results/.
- Run the required lint and tests before each commit.

## Do not

Do not add site-specific policies or change the decision model. Do not claim general browser reliability from one test.

## Result

The local stdio MCP server and Codex registration work. Codex made one `run_browser_goal` call with native browser tools disabled.
Local Qwen opened Casa Flora. Independent URL and page-text assertions passed.
The browser supervisor recorded 8591 ms and a peak sampled inference footprint of 3600517856 bytes.
Evidence: [successful run](../results/codex-mcp.json). An earlier attempt stopped before execution because Codex required tool approval.
That failed attempt remains in [its record](../results/codex-mcp-approval.json).

The integration runner now rejects failed calls and unverified outcomes. It preserves the existing runtime limits.
The MCP server loads the model for each goal. Persistent browser sessions, field entry, multi-step goals, and Claude remain untested through MCP.
GitNexus query, context, impact, index refresh, and change analysis ran. The graph reports omitted dynamic callers and truncated execution flows.
Source inspection and the actual browser outcome support this result. Other chats own the existing local model and runtime edits.
