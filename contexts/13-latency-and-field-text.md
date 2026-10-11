# 13 Latency and field text

Priority P0. Timebox 75 min. Owner Sol. Runs in parallel with 12. Absorbs old tasks 04 and 14.

## Why

Live SFO to BOS run, local Qwen backend. Median decision 4.16s, six actions, then a browser input timeout.
Each forward pass measures ~300 to 450ms warm, so the step cost is prompt size times pass count, not the
model. Separately both backends typed "Boston Logan (BOS)" into the destination and Google returned
"No matching locations found". That is the text helper, not the decision model.

## Part A, latency. Target under 1s median per decision on the bench task.

Read `jev_ultrafast/local_policy.py` first. The cost today:
- Operation stage prompt embeds every target as JSON inside the operation descriptions, and the element
  list is also in the observation. Same information twice.
- Page text capped at 3000 chars. Google Flights fills that.
- Target stage chunks into 20, scores each chunk, then rescores winners. With ~74 actions that is 4 chunk
  passes plus 1 rescore, plus the operation pass. Six prefills of a large prompt.

Do, in this order, measuring after each with `scripts/bench.py --backend qwen --runs 1` (or `run_cli.py`
on the same goal if 12 has not landed):
1. Remove the targets JSON from the operation stage descriptions. The element list already carries it.
2. Cap page text at 1200 chars. If elements exceed 40, cap at 600. Record what the cap costs in decisions
   on the bench task. If it starts picking wrong, back off to 2000 and stop there.
3. Prefix KV cache. Operation stage, every target chunk, and the rescore share an identical prefix up to
   the candidate menu. Prefill the prefix once per decision with `mlx_lm.models.cache.make_prompt_cache`,
   then score each menu suffix from a copy of that cache. Verify picks are identical to uncached on the
   synthetic fixtures before trusting it. If cache copy is awkward in mlx-lm 0.32, timebox this to 25
   min and move on; steps 1 and 2 may already be enough.
4. Browser timeout. Find where the input timeout fired (likely `browser_harness` IPC response timeout or
   `run_cli.py --timeout`). Make sure model time is not counted against a browser deadline, or raise the
   deadline. Record which it was.

## Part B, field text. 20 min.

1. In `questions.py` `TEXT_VALUE`, add: type what a person would type into this field, the shortest plain
   value that identifies it, no airport or stock codes, no parentheticals, no trailing qualifiers, unless
   the goal states the exact string. This is generic, not site-specific.
2. Test offline with the SFO to BOS destination context. Expect "Boston". Also check a date field and a
   search box so the rule does not break them.
3. Keep the single retry and validation already in `local_field_text`.

## Verify

- `results/bench/summary.json` shows a qwen run after your changes with median decision latency and the
  pass/fail. Record both numbers in this file under Result, including the before number from 12's
  baseline.
- `scripts/decision_smoke.py --repeats 0` still 12/12.
- ruff and pytest pass. Add or adjust a unit test only for the observation builder (text cap, no target
  JSON duplication). No model in tests.

## Don't

- Don't touch `scripts/bench.py`, `run_cli.py`, `fixtures/bench_tasks.json`. Those are 12's.
- Don't add site-specific rules. "Type what a person would type" is the whole fix.
- Don't batch across decisions or change the agent loop.
- Don't run your benchmark while Astra is running one. Coordinate in STATUS.md with a one-line note.

## Step 0 landed 13:20 PT (Claude): replay harness and small-model test

- `ZB_RECORD_PATH=/path.jsonl` makes `score_decision` append every scored menu (goal, observation,
  candidates, pick, scores, tokens, latency). `local_choose` tags menus with a decision group id so replay
  can share a KV prefix per decision. No behavior change when the env var is unset.
- `scripts/replay.py --model <id> --records a.jsonl --cases b.json --variant plain|prefix --repeats N`.
  One model per process. Sets the same 6GB MLX memory limit and 256MB cache limit as `local_model`.
  Reports median/p90 latency, per-decision latency, agreement with the recorded pick, accuracy vs expected.
- Prefill scaling on M4 Pro 24GB, 4B 4-bit: 1.6ms per token, ~670 tok/s, linear 250 to 2000 tokens.
  `mx.compile` gave nothing. Last-token-only head saved 7 to 9% (Codex's bounded_prefill already does this).
  A 60-token menu on a cached 1000-token prefix: 117ms. That is the prefix-cache win, ~13x per extra pass.
- Smaller models on the 12 synthetic cases (quality 9 + smoke 3), `results/replay/quality-*.json`:

  | Model | Median per menu | Accuracy | Failure mode |
  |---|---|---|---|
  | Qwen3-4B-Instruct-2507-4bit | 283ms | 11/12 | known filter miss |
  | Qwen3-1.7B-4bit | 113ms | 5/12 | picks DONE (label D) on half the cases |
  | Qwen3-0.6B-4bit | 41ms | 5/12 | picks A on most cases, pure position bias |

  Verdict. Stay on 4B. The small checkpoints are not drop-in replacements for menu scoring. Latency comes
  from prefix cache and prompt trimming, not from a smaller model or a custom kernel (prefill is already at
  ~60% of the GPU's fp16 peak).
- Not yet done: a live SFO to BOS recording with `ZB_RECORD_PATH` set, then `--variant prefix` on it.
  Blocked at 13:20 by machine memory. Swap was 9.3 of 10GB with Codex's Chrome and MCP work running.
  Run it when the machine has one job on it.
