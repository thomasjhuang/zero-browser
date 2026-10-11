# zero-browser hackathon plan (5 hours)

Agents start with `AGENT-RULES.md`, then `STATUS.md`, then this file. Pull before reading.
`PROJECT.md` holds setup and operation commands. This folder is committed and pushed so every agent and
checkout shares the same plan and state.

Goal of the day. One end-to-end run of the Jev agent loop where every model call is local Qwen on MLX.
No TypeSafe, no OpenRouter. Demo it on the local fixture page first, Google Flights only if time allows.

Not the goal. Calibration, broad reliability, new eval methodology, KV-cache research. Cut anything that
does not move the end-to-end demo forward.

## Rules for the day

- Every task has a timebox. When it expires, ship what works and move on.
- Test against the local fixture page (`fixture.html?scenario=travel`, served by `jev_ultrafast/demo.py`
  on 127.0.0.1:8766). It needs no network and no keys. Google Flights is a stretch target.
- Keep `agent.py` and `browser.py` untouched. All local work plugs in through `model.py` function signatures.
- Preserve existing tests. Follow [Experimental validation](../AGENTS.md#experimental-validation) for new unit tests.
- Reuse `scripts/decision_smoke.py` logic by moving it, not rewriting it.
- Commit at the end of every task. Nothing is pushed unless Thomas says so.

## Ranked tasks (rescoped 12:50 PT after the first live run)

The first live SFO to BOS run happened at 12:3x. Local Qwen got six actions in at 4.16s median per decision
and hit a browser timeout. Both backends typed "Boston Logan (BOS)" and autocomplete found nothing.
The fixture-first plan is retired. The loop is now: fix, rerun the same live task, compare.

| Rank | Task | Priority | Timebox | Owner | Notes |
|---|---|---|---|---|---|
| 0 | 17-experiment-priority | P0 | Instructions only | Codex | Prioritize end-to-end evidence and restrict new unit tests |
| 0 | 16-flight-milestone | P0 | Staged with user readiness | Codex milestone | Safety, fixed goals, independent outcomes, and durable evidence |
| 0 | 15-cli-runtime-safety | P0 | 60 min | Codex | Emergency prompt, memory, shutdown, and CAPTCHA guards |
| 1 | 12-benchmark-loop | P0 | 60 min | Astra | Fixed task, backend switch, per-step records, repeat runs |
| 2 | 13-latency-and-field-text | P0 | 75 min | Sol | Under 1s per decision, plain field values, browser timeout |
| 3 | iterate on the next bench failure | P0 | rest of day | both | One fix per rerun |
| 4 | 09-fix-filter-miss | P3 | 20 min | slack only | |
| 5 | 10-trim-jev-scaffolding | P3 | 40 min | slack only | |
| 6 | 08-hygiene-and-readme | P3 | 20 min | last 20 min | Numbers from results/bench/summary.json only |

Done. 00 (shared model), 01 and 02 (local_policy.py, by Codex). Cut. 03, 05, 06, 07, 04 (into 13), 11
installer (run_cli.py stays).

## Two agents, disjoint files

```
Astra  12  owns scripts/bench.py, scripts/run_cli.py, fixtures/bench_tasks.json, results/bench/, jev_ultrafast/verify.py
Sol    13  owns jev_ultrafast/local_policy.py, local_model.py, questions.py, browser timeout wherever it lives
```

Nobody edits agent.py, browser.py, snapshot.js, model.py dispatch. One benchmark at a time on the machine.
Say so in STATUS.md Coordination before starting a run.

## Timeline from 12:50

```
12:50  Astra starts 12, Sol starts 13 part B (text prompt, 20 min) then part A.
13:20  Astra has baseline 3 runs on current code. Sol has text fix pushed. Astra reruns.
14:00  Sol has latency steps 1 and 2 pushed. Astra reruns. Decide whether step 3 (KV cache) is needed.
14:30  Hard stop on new features. Whatever fails next gets one fix each.
15:30  08. README numbers from summary.json. Done by 16:00.
```

## Cut lines

If the qwen backend has not passed the bench task once by 14:30, stop optimizing and ship the comparison
as is with honest numbers. A clean negative result with latency and failure step beats a half fix.

## Definition of done

- `results/bench/summary.json` has at least 3 qwen runs and 1 jev run on the same task, same verifier.
- Per-decision latency, pass count, and failure step for each backend.
- README states those numbers and nothing more.
