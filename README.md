# zero-browser

A local browser-agent experiment for Apple Silicon.
The current prototype scores actions with Qwen. Local browser execution is in development.

```bash
uv sync --frozen --extra local
uv run --frozen --extra local python scripts/download_local_model.py
uv run --offline --frozen --extra local python scripts/decision_smoke.py --offline
```

Browser components come from [Jev Ultrafast](https://github.com/browser-use/jev-ultrafast).
See `LICENSE.jev-ultrafast` for attribution.
