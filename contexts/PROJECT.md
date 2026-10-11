# Local project context

This file contains detailed setup and operation instructions.
Run all commands from the project root.
Record current work and its evidence in [STATUS.md](STATUS.md).
The numbered files describe planned work.

## CLI setup

Run `bash install.sh` from the project root. The installer preserves the model and dependency locks.
It installs missing dependencies, downloads the pinned Qwen weights, and prepares Chrome.

```bash
./zero-browser --doctor
./zero-browser --url https://YOUR_START_PAGE "Your browser goal"
./zero-browser --fixture --expect-url '#casa-flora' --expect-text 'Casa Flora' "Open Casa Flora."
```

The CLI forces local inference through `JEV_LOCAL=1`. The inherited hosted runner remains separate.
It uses a temporary Chrome profile and closes that browser after the run.
Use `--expect-text` and `--expect-url` for independent final-page assertions.
Without assertions, model completion does not establish outcome success.
The parent process enforces the worker deadline, including model loading and browser calls.
The CLI stops on recognizable human verification and three consecutive rejected decisions.
It monitors the worker memory footprint and refuses startup with insufficient memory headroom.
Prompts above the safety limit fail before inference. See `results/cli-runtime-safety.json` for guard evidence.
These changes lack a new Qwen run. Live speed and crash prevention remain unverified.

Installation and browser outcome evidence lives in `results/install-cli-verification.json`.
The simple fixture goal passes. Multi-step destination and filter goals remain incomplete.

## Local scorer setup


Run these commands from the project root with Metal access:

```bash
uv sync --frozen --extra local
uv run --frozen --extra local python scripts/download_local_model.py
uv run --offline --frozen --extra local python scripts/decision_smoke.py --offline
```

The downloader accepts only `mlx-community/Qwen3-4B-Instruct-2507-4bit` with 4-bit quantization.
It uses the normal Hugging Face shared cache, usually `~/.cache/huggingface/hub`.
`model-lock.json` records the resolved revision, file sizes, and dependency versions.
The downloader reuses that revision. Use `--revision main` only for an explicit model update.
`uv.lock` locks dependencies. `requirements-local.lock.txt` records the installed packages.
Weights, environments, and caches stay outside Git.

## Offline reruns


After setup, use the cached packages and weights:

```bash
uv sync --offline --frozen --extra local
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  uv run --offline --frozen --extra local python scripts/decision_smoke.py \
  --offline --output results/decision-smoke-rerun.json
```

The scorer always enforces offline model loading and requests the pinned revision.
If a required cache file is missing, the command fails.
The JSON results are measurement records, not model-generated output.

## Scorer measurements


`fixtures/decision_cases.json` contains three cases: an empty field, an unchecked filter, and a matching search result.
Each case has four candidates. Each action moves through labels A–D.
The scorer makes 48 forward passes with the default three repeats.
It tests single-token labels, their distinct token IDs, and the actual assistant prompt boundary.
`results/decision-smoke.json` contains correctness, scores, token counts, latency, and peak MLX memory.

Cold latency means the first forward pass after model loading. The measurement does not clear Metal or operating-system caches.
Warm latency includes a complete prompt prefill. The scorer does not reuse a prompt or KV cache.
Latency excludes tokenization. Model load time is separate.
Peak MLX memory excludes other applications and operating-system memory.
Scores are uncalibrated and do not guarantee confidence.
These synthetic cases do not establish browser-task reliability.

The broader quality test adds nine cases and rotates each through four candidate orders:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  uv run --offline --frozen --extra local python scripts/decision_smoke.py \
  --offline --cases fixtures/decision_quality_cases.json --repeats 0 \
  --output results/decision-quality.json
```

## Browser scaffolding


The observer, indexed action space, executor, agent loop, and inspector come from
[Browser Use's Jev Ultrafast](https://github.com/browser-use/jev-ultrafast).
`upstream-lock.json` records its revision and retained source hashes.
The original README is in `docs/upstream/README.md`.
`LICENSE.jev-ultrafast` preserves its MIT license and Browser Use attribution.
The import omits demonstration images and videos.

The CLI uses local decisions and field text. Jev's inherited demo still requires hosted services.
The CLI does not load API credentials. Hosted examples need separate authorization and credentials.

## Browser baselines


`scripts/baselines.py` measures Codex, Claude Code, and Jev on three shared local browser tasks.
The tasks cover filters, a hotel search, and an article.
`fixtures/browser_baselines.json` fixes each goal and its outcome criteria.
These tasks measure the agent applications with their browser tools, not isolated model inference.
The local Qwen scorer is not a browser baseline yet.

Start the fixture server in a separate terminal:

```bash
uv run --offline --frozen python scripts/baselines.py serve
uv run --offline --frozen python scripts/baselines.py tasks
```

Use a fresh conversation and tab for each run.
Keep the browser profile, viewport, permissions, and initial page constant.
Record exact model and application versions, browser tools, and permission settings in `--environment`.
Use three repeats per task. Rotate agent order between repeats.
Keep manual desktop sessions and CLI sessions in separate comparisons.

For a desktop session, start the timer immediately before you give the printed prompt to the agent:

```bash
uv run --offline --frozen python scripts/baselines.py start \
  --task filter-stays --agent codex --model MODEL \
  --environment 'VERSION; BROWSER TOOLS; CLEAN PROFILE; VIEWPORT; PERMISSIONS' \
  --billing-mode subscription
uv run --offline --frozen python scripts/baselines.py finish RUN_FILE --status completed
uv run --offline --frozen python scripts/baselines.py verify RUN_FILE --target-id CHROME_TARGET_ID
uv run --offline --frozen python scripts/baselines.py import-usage RUN_FILE EXPORTED_TRACE
uv run --offline --frozen python scripts/baselines.py report artifacts/baselines
```

Replace the uppercase arguments with actual values.
Stop the timer as soon as the agent stops. Outcome verification has a separate timer.
The verifier uses Browser Harness to read the agent's existing Chrome target.
It does not accept the agent's success claim.
A completed run remains unverified until the browser read passes every criterion.
Get the target ID from Browser Harness's `cdp("Target.getTargets")` helper.
Keep the tab open until verification finishes.

`run` wraps a fresh Codex or Claude CLI invocation and captures its output.
For Jev, it captures decisions and text calls, then reads the outcome before the tab closes.
Live invocation requires `--live`. Browser tools and credentials must already be configured.
No live run or spending is part of the offline setup.

```bash
uv run --offline --frozen python scripts/baselines.py run --live \
  --task filter-stays --agent claude --model MODEL \
  --environment 'VERSION; BROWSER TOOLS; CLEAN PROFILE; VIEWPORT; PERMISSIONS' \
  --billing-mode subscription --timeout 120
```

The CLI timeout stops the owned Codex or Claude process group on Unix systems. Jev tests its deadline between agent steps.
A slow Jev model call can exceed that deadline.
For Codex and Claude CLI runs, perform the separate browser verification after the agent stops.
CLI time includes application startup. Manual time includes the operator's handoff.
Browser setup before `start` is outside the timer.
Elapsed time uses the monotonic clock. Records also show system-clock disagreement.
The reports show success rate, criterion scores, median elapsed time, tokens, and cost coverage.
Missing usage stays unavailable. Failed and unverified runs remain in the success-rate denominator.

Codex imports `turn.completed` JSONL usage. Claude imports one fresh-session `result` record.
Do not import a resumed Claude conversation: its cost can include previous turns.
Jev imports `decisions` and `text_calls`. These records include stale and terminal decisions.
It ignores duplicated usage in action history.
Interrupted runs preserve known subtotals but leave total coverage unavailable.
Jev counts recorded model calls. Provider transport retries are not visible in its trace.
Input totals include cached tokens once. Output totals do not add reasoning tokens twice.
Provider-reported cost is separate from a price estimate and actual subscription charges.
For an estimate, add `--prices PRICE_FILE` to `import-usage`.
The JSON file must contain `as_of`, `currency: "USD"`, and `models` keyed by exact model names.
Rates use `input_per_million`, `cached_input_per_million`, `cache_write_per_million`, and `output_per_million`.
Missing model prices or cache data leave the estimate unavailable.
Run records preserve dated prices and source hashes. Private traces stay in ignored `artifacts/baselines/`.

## Tests and delivery

Follow `AGENTS.md` and `contexts/AGENT-RULES.md` for delivery.
Run the required lint and tests before each commit. Commit and push intended files to `main`.
Keep model weights, environments, private traces, and credentials outside Git.
