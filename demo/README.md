# Live demo site

```
.venv/bin/python demo/server.py   # http://127.0.0.1:8765
```

Two buttons run the paired comparison on the same Wikipedia field task:

- **Codex drives the browser** (`direct`): Codex observes and acts itself.
- **Codex delegates to zero-browser** (`delegated`): Codex observes once, then hands the field to local Qwen3-4B.

**Replay recorded** re-streams a passing run from `artifacts/paired/` at its original timing (1×, 2×, 4×). Safe while other experiments run. Replay places each recorded frontier request in order before the tool call it produced.

**Live** launches `scripts/paired_browser_benchmark.py --order <mode>` with a fresh Chrome and fresh Codex session, and streams `codex.jsonl`, `browser.jsonl` and the Codex session token records as they land. Output goes to `artifacts/demo/`. Live is disabled while another benchmark or local worker holds the browser slot. "Run both" runs live arms sequentially.

The recorded evidence panel reads `results/paired-browser-five-pairs-v3.json` and `results/native-desktop-sequential.json`.

Cost is an estimate from prices you type in. Billing is not observed.
