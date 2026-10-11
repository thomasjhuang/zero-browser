# 00 Shared local model

Current status: Implemented. Keep the result below as history. Current work is listed in STATUS.md.

Priority P0. Timebox 20 min. Lane A. Blocks 01 and 02.

## Why

Both the chooser and the text helper need the same Qwen weights loaded once per process.
`scripts/decision_smoke.py` loads per invocation and lives in scripts, so it cannot be imported by the package.

## Do

1. Create `jev_ultrafast/local_model.py`.
2. Move `make_prompt`, `score_decision`, the `SYSTEM` prompt, and the model loading block from
   `scripts/decision_smoke.py` into it. Keep the offline env enforcement and the model-lock revision check.
3. Add `get_model()` returning a cached `(model, tokenizer, mx)` tuple. Lazy, loaded on first call.
4. Make `scripts/decision_smoke.py` import from the new module. Behavior unchanged.
5. Guard the `mlx` imports so `pytest` without `--extra local` still passes (import inside functions).

## Verify

- `uv run --offline --frozen --extra local python scripts/decision_smoke.py --offline --repeats 0` still passes 12/12.
- `uv run --offline --frozen --extra local pytest` passes.
- `ruff check .` clean.

## Don't

- Don't change prompt text or scoring math. This is a move.

## Result

Codex claimed task 00 at 2026-10-11 12:27 PT and completed it within the timebox.

`jev_ultrafast/local_model.py` contains the original prompt and scoring functions.
`get_model()` loads one cached `(model, tokenizer, mx)` tuple under a lock.
Local dependency imports remain inside the loader. The smoke script uses the shared implementation
and preserves its exports for the baseline scripts. Offline enforcement, the pinned revision,
checkpoint checks, and 4-bit checks remain intact.

[Smoke evidence](../results/shared-local-model-smoke.json): 12/12 decisions passed.
Model loading took 1188.82 ms. The first forward pass took 370.07 ms.
Warm median latency was 304.04 ms. Peak MLX memory was 2,714,353,572 bytes.

[Additional evidence](../results/shared-local-model-verification.json): source comparisons passed
for the prompts, scoring functions, and loading arguments. Scoring and text generation used one
model load. Lint passed. All 50 tests passed with the local extra and without it.
The import test blocks local dependencies. Cache tests cover concurrent calls and failed loading.

GitNexus query, context, impact, and change detection ran. The index refresh completed, but the MCP
freshness hint remained stale. Flow extraction omitted some paths. Source comparisons and tests
cover the affected baseline imports.

No task 00 work remains. Tasks 01 and 02 must connect the shared model to the agent loop.
