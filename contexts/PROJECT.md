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
Task 16 records subsequent local pilots and completion experiments. Live speed and prevention of the reported freeze remain unproven.

Installation and browser outcome evidence lives in `results/install-cli-verification.json`.
The simple fixture goal passes. Multi-step destination and filter goals remain incomplete.

## Local MCP server

Codex can delegate browser goals to the local Qwen pipeline through `run_browser_goal`.
The server uses stdio and starts an isolated browser for each goal. The model loads for each goal.
It preserves the CLI memory, deadline, and single-run limits. It returns final-page assertions and sampled inference memory.

```bash
codex mcp add zero_browser -- "$PWD/.venv/bin/python" "$PWD/scripts/mcp_server.py"
```

Start a new Codex session after registration. Ask it to use `zero_browser.run_browser_goal` for browser work.
The registration does not disable other browser tools globally.
Run the fixed integration experiment with `.venv/bin/python scripts/codex_mcp_smoke.py`.
This experiment disables native browser tools and permits only the browser MCP tool for that invocation.
The first local fixture experiment passed. See [the record](../results/codex-mcp.json).
Field entry, multi-step goals, and Claude integration remain untested through MCP.

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

## Current benchmark

Task 16 uses `scripts/milestone.py`, `fixtures/milestone_tasks.json`, and `scripts/milestone_verify.py`.
The runner preserves event records in ignored `artifacts/milestone/`.
Read existing records without inference:

```bash
uv run --offline --frozen --extra local python scripts/milestone.py --report
```

Read task 16 and STATUS before any experiment. Preserve the single-run guard and the user's action boundaries.
Keep task conditions and source versions with each result. Never infer completion from DONE alone.
The user supplied the initial pilot observations. A new owner must read the current handoff before further runs.

The earlier commands for `scripts/baselines.py` were stale. That file is absent from this checkout.
Task 21 defines the future native Codex comparison. No working native baseline is established.
`scripts/decision_baselines.py` compares synthetic decisions only. It does not measure browser completion.

## Experiment scoreboard

Run records, scores, and proposals stay outside git. The recorder writes under ignored `artifacts/experiment-loop/`.
The record schema is `zero-browser.experiment-run.v1`. The scoreboard rejects a batch when evidence is missing,
token fields disagree, or the `local-coordinator` arm records a hosted call. Passing requires every
`independent_checks` value to be true. A DONE choice is stored and ignored.

```bash
uv run --offline --frozen --extra local python scripts/experiment_record.py \
  --arm local-coordinator --hosted-model-calls 0 --run-dir artifacts/milestone/<run>
uv run --offline --frozen --extra local python scripts/experiment_scoreboard.py \
  --runs artifacts/experiment-loop --output artifacts/experiment-loop-summary.json
```

`experiment_record.py` copies `verification.checks` from a finished milestone directory. It does not
treat `outcome_verified` or a DONE choice as the result. Pilot runs are refused. Absolute paths in the
copied evidence are redacted. A blocked arm uses `--blocked --reason "..."` instead of a run directory.

Do not commit the summary or a proposal. An unmeasured batch leaves `combined_score` null.
`experiments/local-coordinator/evaluate.py` can write `metrics.json` and `correct.json` for a local
AI-Scientist v3 task. It does not launch a browser or a model.

MLflow is a dev dependency. Tracking uses a sqlite store under ignored `artifacts/mlflow`. The track and
propose commands exit without writing when the run directory is missing.

## Tests and delivery

Follow `AGENTS.md` and `contexts/AGENT-RULES.md` for delivery.
Run the required lint and tests before each commit. Commit and push intended files to `main`.
Keep model weights, environments, private traces, and credentials outside Git.
