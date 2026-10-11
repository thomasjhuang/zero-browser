# 01 Local choose adapter

Priority P0. Timebox 90 min. Lane A. Blocks 06. This is the critical path.

## Why

`model.choose()` is the only place TypeSafe is called. Replacing it with local scoring makes the agent loop
run without a hosted decision model. `agent.py` consumes the returned dict, so the shape must match.

## Design (decided, don't re-litigate)

Two-stage scoring, mirroring Jev's operation head plus target head.

1. Operation stage. Candidates are the keys of `operations` in `choose()` (CLICK, TYPE_TEXT, SELECT, any
   control actions like scroll/wait, DONE, BLOCKED). Always under 26, so letter labels work as is.
2. Target stage. Only for the chosen operation. Candidates are that operation's targets from `action_space()`.
   Use the element index as the label text (`1`, `2`, ... `12`). Qwen tokenizes small integers as single
   tokens up to at least two digits; verify with the existing boundary check in `make_prompt`.
   If a target group exceeds the single-token limit, chunk into groups of 20, score each chunk, take the
   best chunk winner by raw logit. Crude but fine for today.

Observation text for the prompt. Reuse what TypeSafe got, the page title, trimmed page text (cap ~3000 chars),
and the `elements` list rendered as `[index] role label value=... checked=...`. Keep `NEXT_ACTION` and
`TARGET` rules from `questions.py` in the prompt so behavior matches the synthetic fixtures.

## Do

1. Add `local_choose(state, goal, history)` in `jev_ultrafast/local_model.py` (or `local_policy.py`).
2. Return exactly the dict `choose()` returns. `probabilities` keyed by action id, `operation`, `target`,
   `confidence` (use the restricted softmax max), `latency_ms`, `usage` (token counts), `model`, `request`.
3. In `model.py`, make `choose()` dispatch to `local_choose` when `TYPESAFE_API_KEY` is unset or
   `JEV_LOCAL=1`. Keep the TypeSafe path intact.
4. Write one unit test that monkeypatches `score_decision` and checks the dict shape and that a
   TYPE_TEXT target never resolves to a click-only element. Mirror `test_click_cannot_consume_a_text_target`.

## Verify

- Run `local_choose` against a fixture observation from 05 (or the synthetic cases) and print the decision.
- Per-decision latency printed. Expect two forward passes, roughly 600ms to 1s warm. Report to Lane B.

## Don't

- Don't add a KV cache here. That is 04.
- Don't tune prompts beyond what is needed to get sensible picks on the travel fixture.
- Don't touch `agent.py`.
