# 00 Shared local model

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

Codex claimed task 00 at 2026-10-11 12:30 PT. Implementation and task tests are pending.
