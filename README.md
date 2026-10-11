# zero-browser

Run browser goals with local Qwen on an Apple Silicon Mac with Metal.
This is a prototype. Live browser reliability and resource use remain unverified.

With Git installed, run:

```bash
git clone https://github.com/thomasjhuang/zero-browser.git
cd zero-browser
bash install.sh
```

If `uv` is absent, the installer installs it. It installs locked Python dependencies and downloads the pinned
[Qwen3-4B 4-bit model](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit).
The model download is about 2.3 GB. The installer reuses cached weights and preserves repository locks.
If Chrome is absent, it downloads Chrome for Testing. Setup tests the model, Metal, and the browser connection.

Give the CLI one goal and a starting page with `--url`.

Each run uses local model calls and an isolated Chrome profile. It needs no API keys.
If you omit the goal, the CLI asks for it.
Use `./zero-browser --doctor` to test setup. Use `bash install.sh --offline` after the required downloads finish.

The local fixture is a fake hotel page. Casa Flora is one of its sample hotels:

```bash
./zero-browser --fixture --expect-url '#casa-flora' --expect-text 'Casa Flora' "Open Casa Flora."
```

The CLI stops on recognizable human-verification text and three consecutive decisions without execution.
A separate worker enforces a deadline and monitors its memory footprint. The CLI permits one run at a time.
Prompt and cache limits reduce inference work. These safeguards do not establish live speed or prevent every system freeze.
[Safety evidence](results/cli-runtime-safety.json) records model-free tests and a local challenge stop.
Bounded local inference now has [measured results](results/milestone-local-runs.json). The multi-step tasks still fail.

The [flight milestone](contexts/16-flight-milestone.md) defines fixed goals and separate outcome tests.
Its [preparation evidence](results/milestone-preparation.json) covers model-free stops and scripted local browser checks.
The pilot showed a visible page, a responsive computer, and clean browser closure, according to the user.
The normal and reversed local tasks failed their outcome tests. The crowded task reached its external deadline.
The user also reported normal responsiveness and clean closure during cancellation. No live flight-search success is established.
[Follow-up tests](results/milestone-followup.json) cover joint choices, cache reuse, and a second DONE choice after a fresh observation.
The observation-metadata follow-up also failed the fixed local task. Correct field descriptions did not prevent incomplete submission.
[Cache parity](results/milestone-cache-parity.json) passed on fixed menus. Multi-step completion and the crowded-page speed target still fail.

The current proof targets bounded subtasks rather than full flight search. The worker accepts one exact field outcome and supplied values.
It narrows candidate actions to that contract. It reads field values after execution and keeps model claims separate from observed evidence.
Missing or ambiguous targets return uncertainty. An uncertain mutation stops the worker without replay.

For a supplied request, use JSON with a starting `url` and a `task` object:

```json
{
  "url": "https://YOUR_START_PAGE",
  "task": {
    "outcome": "Set Departure airport to Zurich Airport (ZRH). Do not submit.",
    "kind": "autocomplete",
    "target": "Departure airport",
    "value": "Zurich Airport (ZRH)",
    "query": "Zurich",
    "permitted_actions": ["fill", "click", "wait"],
    "stopping_conditions": ["outcome_observed", "human_required", "boundary_violation"],
    "deadline_seconds": 45,
    "action_budget": 4
  }
}
```

Use `fill`, `select`, or `autocomplete` for `kind`. Supply the observed field label and the desired value.
Autocomplete requires a unique matching option associated through `aria-controls` or `aria-owns`.
The worker supports at most eight actions and a sixty-second worker deadline. Browser startup has a separate twenty-second limit.
Cleanup can add time. Memory measurements exclude the browser.

```bash
mkdir -p artifacts/replay
ZB_RECORD_PATH=artifacts/replay/request.jsonl uv run --offline --frozen --extra local python scripts/worker_benchmark.py --request request.json --output artifacts/request-result.json
```

The result includes status, observed field evidence, executed actions, unresolved execution, elapsed time, model calls, and sampled worker memory.
The fixture suite uses additional independent tests. A supplied live request has only the worker's field predicate unless a separate site verifier is supplied.
There is no automated coordinator, task-resumption mechanism, or measured time or cost saving in this proof.

The CLI reads the final page independently. Supplied expectations determine `outcome_verified`.
Without expectations, a DONE choice remains unverified. Failed expectations return a nonzero exit code.

[Installation evidence](results/install-cli-verification.json) includes the completed fixture goal and failed multi-step attempts.
Those failures prevent a claim of general browser reliability. Windows, Linux, and Intel Macs are unsupported.

Browser components come from [Jev Ultrafast](https://github.com/browser-use/jev-ultrafast).
See `LICENSE.jev-ultrafast` for attribution.


The bounded-worker [repeat evidence](results/bounded-worker-summary.json) contains three unchanged suites: 27 requested outcomes and six safe stops passed. Median task time was 5.37 seconds; median decision time was 1.51 seconds. Peak sampled worker memory was 3.34 GB, excluding the browser.
A [live Wikipedia field test](results/bounded-worker-live-assessment.json) entered supplied text without submission in 6.83 seconds of worker time. These narrow results do not prove general browser reliability, full flight-search completion, or savings. A direct native-browser attempt also passed, but its timing and browser conditions differ. A matched native-desktop comparison, unseen-case assessment, deterministic-helper baseline, and interruption/continuation remain untested.


A later [controlled comparison](results/paired-browser-comparison.json) used fresh `gpt-6-astra` coordinators over the same observed-action MCP browser interface. All ten original trials and two authorized supplemental trials passed. One original pair overlapped background indexing. The five-pair comparison set excludes that pair and includes the later supplemental pair. Delegation was a median 1.90 seconds faster and used 42,212 fewer total coordinator tokens, including cached input. Median uncached input was 3,202 tokens lower. Aggregate coordinator totals were 605,218 direct and 396,644 delegated, a 34.46% reduction. The local model added 4,997 prompt tokens and 130 retokenized response tokens. Every direct trial required extra exchanges after a page change. This exploratory comparison does not measure native desktop CUA tools or establish billing savings. A deterministic-helper comparison remains pending.


The [focused workflow attempt](results/workflow-focused-summary.json) used a dedicated bounded prompt, deterministic exact actions, and returned page evidence across one browser session. Search-and-open succeeded. The next link disappeared from visible controls after a donation banner appeared, so the worker stopped before input. The full workflow failed in 29.29 seconds. It used six coordinator responses, two local calls, and one model load. Exactly one attempt ran, with no replacement. Reliable recovery from these page changes remains unresolved. Native desktop workflow comparison did not run after the user changed scope.


The authorized [additional workflow attempt](results/workflow-recovery-summary.json) passed all route and answer checks in 29.90 seconds, including startup. It used three browser actions, six coordinator responses, two local calls, and one model load. **Recovery was not invoked.** The new one-action recovery passed model-free regression checks, but this live success does not prove its effectiveness. The prior failed result remains unchanged. A controlled disappearing-target case is the next proposed test.

The [native desktop baseline](results/native-desktop-comparison.json) reached the correct article and answer. A coordination race created two overlapping attempts despite authorization for one. The retained attempt recorded 38.51 seconds, but the overlap invalidates a clean comparison with the 29.90-second system run. Both traces and separate usage counts are preserved. No speed or cost advantage is established.

A [separately authorized sequential native attempt](results/native-desktop-sequential.json) passed in 33.05 seconds with one launch owner. It used 516,054 coordinator tokens, including cached input. The saved system run passed in 29.90 seconds with 133,272 coordinator tokens plus two local calls. These are single product measurements with different browser state, context, tools, and final-verdict timing. They do not establish general speed or billed-cost savings.

The [one-off live Flights attempt](results/flights-demo-once.json) failed before destination selection or date entry. The general local Qwen runner received “No matching locations found,” then failed to recover within 20 decisions. It took 39.50 seconds including startup and cleanup, with 23 local calls and one model load. No flight options or prices were observed. This run does not measure the demonstrated bounded coordinator workflow.

A [JFK-only attempt with one coordinator correction](results/flights-handoff-once.json) also failed. The worker retained its browser and loaded model across the handoff. It then chose an unrelated multiple-airport control, which the boundary guard stopped before execution. The attempt took 22.70 seconds with two decisions, four local calls, and one model load. No airport selection occurred. Successful live recovery remains unproven.

The [single-action demonstration](results/flights-single-action-once.json) returned control after entering JFK and showed the matching suggestion. The next exact click request stopped because the observation was stale. JFK was not selected. The attempt took 22.54 seconds with one executed fill, zero local inference calls, and one model load. The control boundary is implemented, but this attempt proves neither completed destination selection nor Qwen selection through that path.

After the minimal freshness fix, [one attempt selected JFK by independent assessment](results/flights-target-freshness-once.json). A pre-input rejection returned fresh evidence, and a new coordinator request clicked the matching airport. The automatic assessor missed the changed destination label. The coordinator saved its separate verdict and cancelled, with exit 130 and completed cleanup. Independent assessment took 50.90 seconds from dispatch; total time was 51.49 seconds. Three requests produced two deterministic actions, one stale return, zero inference calls, and one model load. This does not establish Qwen value or reliable automatic completion.
