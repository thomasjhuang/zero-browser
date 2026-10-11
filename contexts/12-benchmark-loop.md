# 12 Benchmark loop

Priority P0. Timebox 60 min. Owner Astra. Runs in parallel with 13.

## Why

The live SFO to BOS run is the only test that matters now. Every fix in 13 needs to be rerun against the
same task with the same measurements, or we cannot tell whether it helped. `scripts/run_cli.py` already
starts an isolated Chrome, runs the agent loop, and asserts on the final page. It is missing a backend
switch, a fixed task definition, per-step records, and repeat runs. This task turns it into that harness.

## The task under test (fixed, do not change during the day)

Start URL `https://www.google.com/travel/flights?hl=en`. Goal: "Find one-way flights from San Francisco
to Boston on November 16, 2026, for one adult in economy. Stop when matching flight options are visible.
Do not select or book a flight." Verification reuses `examples/flights.py::verify()` with SFO/BOS/Nov 16
substituted. The model never sees the verifier.

## Do

1. Add `fixtures/bench_tasks.json`. One entry, `sfo_bos`, with url, goal, and the verify parameters
   (origin label, destination label, date label, URL date). Structure allows more tasks later.
2. Add `scripts/bench.py` (or extend `run_cli.py`, your call, but keep `run_cli.py` working).
   `--task sfo_bos --backend qwen|jev --runs N --output results/bench/`.
   - `qwen` sets `JEV_LOCAL=1`. `jev` unsets it and requires `TYPESAFE_API_KEY` in env; text helper stays
     local for both so the comparison isolates the decision model. Fail fast if the key is missing.
   - Per run, record: every decision (operation, target, operation scores, target scores, candidate count
     per stage, forward passes, prompt tokens, latency_ms), every text call (value, latency), every executed
     action with page_changed, final verify() result, total elapsed, status.
   - Per run file `results/bench/sfo_bos-<backend>-<timestamp>.json`. Plus `results/bench/summary.json`
     that aggregates pass count, median and p90 decision latency, median text latency, actions per run,
     and the step where each failed run stopped.
3. Make `verify()` reusable: move the parametrized version into `jev_ultrafast/verify.py` or a function
   in `bench.py`. `examples/flights.py` keeps working.
4. Run `--backend qwen --runs 3` once on the current code before 13 lands. That is the baseline. Commit
   the summary. Then run again whenever 13 pushes a change and append to the summary.
5. Print a one-line table per run to stdout so a human can watch it.

## Verify

- `results/bench/summary.json` has at least one qwen baseline with 3 runs.
- `uv run --offline --frozen --extra local ruff check .` and pytest pass. Add one test for the summary
  aggregation with fake run records. No test calls the model.

## Don't

- Don't edit `local_policy.py`, `local_model.py`, `questions.py`, or `browser.py`. Those are 13's.
- Don't change the task text or verifier mid-day. Add a second task if you want variety.
- Don't commit raw final page dumps that include personal data. The summary and decision records are fine.
- Don't run two benchmarks at once on the same machine. Latency numbers would be meaningless.
