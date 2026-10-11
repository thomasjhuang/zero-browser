# Isolated terminal travel demo

This branch adds a travel workflow around the existing browser observer and executor. Its fixed request
is a one-way flight from San Francisco International Airport (SFO) to Boston Logan International Airport
(BOS) on November 16, 2026: one adult, Economy, nonstop, strictly under $400 in United States dollars
(USD), arriving **on November 16 before 18:00 Boston local time**. The terminal shows up to five verified
options, ordered by observed price. Fewer options are valid when fewer inspected flights qualify.
Economy includes basic economy fares when Google groups them under Economy; this request does not
require a particular baggage allowance, seat-selection benefit, or refund policy.

Run these commands from the repository root. Python 3.12 or newer, the locked project dependencies, and
Chrome are required. The fixture run does not require model weights or network access.

```bash
uv sync --frozen
uv run --offline --frozen python -m travel_demo --fixture --headless
```

If `.venv` is already installed, use `.venv/bin/python` instead of `uv run --offline --frozen python`.
Chrome discovery and the isolated profile reuse `scripts/run_cli.py`; if Chrome is absent, the existing
browser installer is `uv run --frozen python scripts/run_cli.py --install-browser`.

The default mode is `workflow`, with **no model calls**. It operates only on currently observed controls
that have an unambiguous semantic label. Airport text must be committed by choosing an observed
autocomplete suggestion. An unfamiliar or ambiguous page stops unless local model fallback was
explicitly enabled. The core browser, shared model adapter, runner, and runtime guards remain unchanged.

The loop configures trip type and cabin, enters each airport query and commits its observed suggestion,
then chooses a departure date with the full year (a calendar on supported live pages; an explicitly
formatted date field in the fixture). It freshly checks the passenger popup when needed, submits only
after every request field is verified, and waits within a bound for results to load. It inspects rows,
checks constraints, sorts qualifying fares, and presents up to five. A fresh final verification,
including passenger composition when a popup is used, precedes success. Chrome then stays open until
Enter for a successful visible run.

## Fixture variations

```bash
.venv/bin/python -m travel_demo --fixture --headless --layout reverse
.venv/bin/python -m travel_demo --fixture --headless --layout renamed
.venv/bin/python -m travel_demo --fixture --headless --layout ambiguous
.venv/bin/python -m travel_demo --fixture --headless --layout empty
.venv/bin/python -m travel_demo --fixture --headless --layout challenge
.venv/bin/python -m travel_demo --fixture --headless --layout passengers
```

`normal` is the default. `reverse` reorders controls. `renamed` uses equivalent semantic labels.
`ambiguous` adds a second Origin field and should stop safely without presenting a shortlist.
`empty` provides an explicit empty-results message after a valid search.
`challenge` requests human verification and should stop before inference.
`passengers` replaces the inline adult selector with a passenger-total button and a popup showing the
adult, child, and both infant counts. A fresh observed popup/read/close transaction proves one adult and
zero children or infants before submission; the total button alone cannot prove adult composition.
The workflow repeats that transaction against the final search context before presenting results.
Any other mutation expires its proof, and unknown popup wording stops instead of guessing.
This variation also lets scrolling hide the search header; the collector must return to the top and
freshly verify the complete search fields and passenger composition before presenting results.

The fixture uses the same snapshot observer and browser executor as a live run. It has native selects,
accessible airport autocomplete, committed request values in the search URL, and realistic flight-row
accessibility labels. Its invented rows mix prices, airlines, connections, late arrivals, and an
overnight arrival. Its standard sticky form preserves visible search context while results scroll;
the `passengers` variation deliberately uses a scrolling header.
The fixture does not establish live Google Flights reliability, model speed, or real airfare availability.

## Live browser and review

Preparation verified the fixture expectations and a headless Google Flights run with three qualifying
flights from twenty inspected rows; six rows could not be parsed. The final visible Google run stopped
at an unsupported transition without a verified shortlist. **Visible live operation remains unreliable.**
The browser hold and Enter-to-close behavior were verified on the synthetic fixture. The
[preparation record](../results/travel-demo-preparation.json) preserves both successes and stopped probes.

```bash
.venv/bin/python -m travel_demo --headless
.venv/bin/python -m travel_demo --headless --airline JetBlue
.venv/bin/python -m travel_demo --headless --airline JetBlue --airline United
```

Omit `--headless` for a visible attempt. For a verified synthetic review demonstration, use
`.venv/bin/python -m travel_demo --fixture`.

Omitting `--airline`, or supplying a blank name, considers every airline. Supplying a name is a
**strict airline restriction** using the airline name displayed by Google,
not a soft preference: only exact normalized airline names qualify. Repeating it allows any listed
airline. There are no sponsor, hotel, export, booking, login, or payment steps.
The airline restriction is applied to inspected shortlist rows; it does not require an airline filter
in the website's interface.

A successful visible run leaves the owned Chrome tab open at the observed search results. Press Enter
in the terminal to close that isolated browser. Review occurs after the timed worker finishes and is
excluded from its measurements. `--headless` always cleans up, and `--no-review` closes visible runs
immediately. A terminal without interactive input also closes the browser. Failed runs close their
owned browser.

The live adapter accepts only supported English Google Flights search context and row wording. A
verified request does not mean every displayed row is parsable; unparsed-row counts are reported.
Unknown dates, routes, currencies, years, or changed result wording cannot supply shortlist entries.
“Cheapest” means cheapest among inspected qualifying rows, with bounded scrolling. The demo does not
claim an exhaustive search or globally cheapest airfare. Fares can change and additional fees may apply.

## Optional local model comparison

The repository's existing local model setup is documented in `contexts/PROJECT.md`. After the user is
ready for bounded local inference, these commands opt in explicitly:

```bash
.venv/bin/python -m travel_demo --fixture --headless --mode workflow --allow-model
.venv/bin/python -m travel_demo --fixture --headless --mode local --allow-model
```

`--ready-model` is an alias for `--allow-model`. Workflow mode uses local Qwen only when deterministic
rules cannot proceed. Local mode lets Qwen choose every search action; verified result collection and
outcome checking are shared between modes. The worker lazily imports the inference modules only if a
model callback is invoked. The model loads pinned cached weights; this demo adds no hosted model calls.
No Qwen run is included in model-free preparation, and the reported freeze remains an upstream reason
to obtain readiness before an actual inference experiment.

`run_session` accepts injected `decide(page, goal, history)` and `write_text(context)` callbacks. This is
the reuse point for a future frontier-model adapter in Thomas's benchmark harness. **No frontier runner
or hosted comparison arm is implemented.** Compare arms using the identical `request.json`, fixture
layout, browser viewport, action budgets, outcome checker, and timed-worker boundary. The request and
source hash are recorded for each invocation. Do not compare fixture success with a live-browser result
as if the environments were equivalent.

## Evidence and bounds

Each run writes ignored local evidence to a fresh directory under `artifacts/travel-demo/`: `request.json`,
`conditions.json`, `events.jsonl`, and a completed worker's `result.json`. Override the root with
`--artifacts PATH`. A worker interrupted before completion can leave only its durable journal and
conditions; absence of `result.json` is not success. The journal records observations, decisions, and
mutations before the next browser read. Its raw browser contents can be private; keep artifacts out of Git.

The terminal reports executed actions, model decisions, field-text requests, and actual low-level model
calls started and finished. A decision may score more than one menu, so decision count and inference
call count are distinct. A call that starts but does not finish remains recorded. Timings, sampled
worker peak memory, and stop causes are saved rather than inferred from a model's DONE choice.

Every run uses the existing single-run lock, an isolated Chrome profile, a supervised worker deadline,
worker memory monitoring, and cancellation cleanup. Model-free workers have a 512 MiB worker limit;
model-enabled runs use the existing dynamic memory-headroom guard. Chrome is outside that worker memory
sample. Defaults are 40 browser steps, 12 model decisions, and 90 seconds including startup and any
model loading; `--max-steps`, `--max-model-decisions`, and `--timeout` adjust them. `Ctrl-C` cancels owned
processes. A recognizable human-verification challenge stops the workflow.

The [preparation evidence](../results/travel-demo-preparation.json) records ten fixture expectations,
the bounded live observations, synthetic review-hold verification, and passing lint and tests. These
checks do not establish general live reliability or a local-model/frontier performance comparison.
