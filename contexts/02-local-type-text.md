# 02 Local TYPE_TEXT

Priority P0. Timebox 60 min. Lane B. Blocks 06.

## Why

`field_text()` is the second hosted call. Without it, every fill action fails with a missing credential error.
This is the only place the local model generates tokens, so it is the only place generation latency matters.

## Do

1. Add `local_field_text(context)` in `jev_ultrafast/local_model.py`.
2. Prompt. System is `TEXT_VALUE` from `questions.py`. User is `json.dumps(context)`, same as today.
   Use `apply_chat_template` with `enable_thinking=False`.
3. Generate with `mlx_lm.generate`, `max_tokens=128`, temperature 0. Parse the first JSON object in the output.
   Apply the exact same validation `field_text()` already does (single `text` key, nonempty string, under 2000).
4. If parsing fails once, retry once with a stricter suffix on the user message. Then raise the same ValueError.
5. Return `(value, {"model": ..., "latency_ms": ..., "usage": {prompt_tokens, completion_tokens}})`.
6. Dispatch in `model.field_text()` when `TEXT_MODEL_API_KEY` is unset or `JEV_LOCAL=1`.
7. Reuse the existing parametrized test `test_text_helper_rejects_invalid_values` by monkeypatching the
   generate call.

## Verify

- Call it with a hand-built context. Goal "find Design stays in Lisbon", field "Destination". Expect "Lisbon".
- Print latency. Expect under 1.5s for short values on M-series.
- Confirm `get_model()` is shared with 01, model loads once.

## Don't

- Don't build grammar-constrained decoding. JSON parse plus one retry is enough today.
- Don't try to also generate the operation. Scoring handles that.

## Result

Done by Codex in `jev_ultrafast/local_policy.py` (local_choose and local_field_text) under task 11, dispatched from `model.py` when `JEV_LOCAL=1`. Landed with the 12:4x commit. Quality and latency follow-ups are in 13.
