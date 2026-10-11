# 16 Flight demonstration milestone

Priority P0. Owner Codex milestone chat. First stage: model-free preparation.

## Why

The user selected a dependable flight-search demonstration. Runtime safety precedes local inference.
The reported computer freeze has no established cause.

## Do

- Preserve task 15 safeguards and active ownership of tasks 12 and 13.
- Add a separate milestone runner, durable event records, fixed tasks, and independent outcome tests.
- Primary: San Francisco to Boston, November 16, 2026. Variations: November 17 and Seattle on November 16.
- Use one adult, economy, and one-way travel for every flight task. Stop with matching options visible.
- Permit navigation, scrolling, search fields, autocomplete, filters, and search submission.
- Stop for login, CAPTCHA, flight selection, booking, payment, messages, and account changes.
- Include a local multi-step task, crowded controls, and changed control order.
- Preserve failed and interrupted records. Measure total time, decision time, calls, and memory.
- Remove repeated prompt content before cache work. Coordinate changes to task 13 files.

## Verify

- Run model-free safety and outcome tests before inference.
- Prepare one short local run. Wait for user readiness before starting it.
- Obtain user observations about responsiveness and cancellation before longer runs.
- Test every requested requirement independently. DONE alone never establishes success.
- Seek three consecutive primary successes, then run both variations. Keep comparison conditions fixed.
- Follow the required lint, tests, commit, and push procedure. Keep evidence in results/.

## Do not

Do not load Qwen during preparation. Do not run concurrent benchmarks or hosted models.
Do not add site-specific decision rules, hardcoded field answers, or a separate Markdown report.

## Result

Model-free preparation passed. Evidence: [preparation](../results/milestone-preparation.json).
The user then reported a visible page, a responsive computer, and clean browser closure.

The runner now removes unused startup tabs and shows the task page. It fixes the local starting address.
The local prompt omits duplicate targets and separates current dropdown values from available changes.
The baseline removed failed prompt experiments. Cache reuse appears in the later follow-up below.

[Run evidence](../results/milestone-local-runs.json) preserves the pilots and failed local experiments.
The normal task skipped the origin. The reversed task submitted two adults instead of one.
DONE did not establish success. The crowded run reached its external deadline with an unfinished model call.
Earlier runs used random local ports, so their comparisons are exploratory.

The last pilot cancelled during inference. The worker stopped 36 milliseconds after the cancellation request.
The user reported normal responsiveness and clean browser closure for that cancellation test.
The runner retains partial records under ignored `artifacts/milestone/`. `--report` reads them without inference.

The milestone remains open. No live flight task passed, and the flight variations remain untested.
The measured baseline was pushed as `9a3e60e`. The joint menu, cache reuse, and DONE confirmation now have measured reruns.
The live flight verifier remains untested. The freeze cause remains unknown.

Use `--pilot --ready` only after user readiness. The pilot permits two decisions and cancels after three seconds.
The worker deadline is twenty seconds. Browser startup has a separate twenty-second deadline.
Cleanup adds time after cancellation. The user supplied the required observations.

The latest goal-placement experiment also failed and was removed. The independent tests rejected every full local run.
Baseline delivery checks passed. The user resolved the publication hold and requested the follow-up changes.

### Test scope and publication follow-up

The user requested publication of pending evidence and an explicit limit on test expansion.
Keep existing tests. Add tests only for critical safeguards or repeatable bugs until the flight demonstration works.
Follow [the working rules](AGENT-RULES.md#while-working). A passing unit suite does not establish browser completion.
This follow-up changes context and evidence only. Preserve the owner's unfinished runtime and test edits.

Joint-menu rerun: the first failed step was 3, an incomplete search submission. DONE followed at step 6.
One scoring call per decision reduced decision time, but the task still failed.
Evidence: [follow-up experiments](../results/milestone-followup.json).

Cache replay matched all 14 plain choices and scores. The local rerun still failed at step 3 with an incomplete submission.
Evidence: [cache parity](../results/milestone-cache-parity.json) and the follow-up experiments.

Cached crowded rerun: step 6 stopped after three actions without observed progress. No field text was entered.
Decisions still exceeded the two-second target. The follow-up evidence preserves the failed run.

DONE-confirmation rerun: the first failed step remained 3, an incomplete submission.
The model chose DONE at steps 6 and 7 with a fresh observation between them. Independent outcome tests still failed.

The conditional-autocomplete experiment also failed at step 3 and was removed.
All requested follow-up mechanisms are implemented. The local success gate remains unsatisfied.
No live flight run or flight variation started. The root cause of omitted goal requirements remains unresolved.
The joint menu did not establish the proposed explanation that operation splitting caused every earlier failure.

Cache reuse matched the uncached choices on the fixed replay menus, but increased worker memory.
The crowded-page speed target remains unmet. DONE confirmation adds a fresh observation, not independent proof of completion.
Next work must address missing goal requirements before another success sequence or live flight test.

At 13:59 PT, task 16 accepted the coordinated runtime handoff in `5799c81`.
Claude handed observation files, replay, and recording to this task. Claude remains in read-only review mode.
No inference is running. Publish the current implementation and evidence before the next observation experiment.
The recorded follow-up runs predate observer commits `510a2bf` and `9f5b613`.
Delivery checks passed: lint and 124 tests. GitNexus found affected runtime and replay flows, with the recorded index limits.

### Observation metadata experiment

Start: October 11, 14:00 PT. Owner: Codex task 16. One run, no concurrent inference.
Source commit: `100c9da2cad9676a7e6ef55a44d4179f0f9d5771`.
Command: `ZB_RECORD_PATH=artifacts/replay/observer-local.jsonl uv run --offline --frozen --extra local python scripts/milestone.py --task local_search --ready`.
Private evidence: `artifacts/milestone/local_search-<run-id>/` and the replay path above.
The runner records all measured source hashes in `conditions.json`. Dirty file hashes before this run:

- `jev_ultrafast/local_policy.py`: `803e9b1201931697ad8a7cb18176146691367779360fd69b74e03983edcb48bb`.
- `tests/test_local_policy.py`: `23238604cbcf83179680b9bdce8fc63dabfd1ded9d865aca0494e76e8dc3cf02`.

The runtime, fixture, prompts, and environment remain fixed until the process ends.

End: October 11, 14:01 PT. Slot idle. Record: `local_search-1791752434369203000`.
The first failure was step 4: Search with empty origin, two adults, and Business cabin.
The available controls exposed all three requirements. Generated date and destination text were correct.
No execution error or DONE decision occurred. Three unchanged actions stopped the run at step 9.
Total time: 24,483 ms. Nine decisions took 1,835–2,223 ms each. Eleven model calls completed.
Peak worker memory: 3,646,147,344 bytes, excluding the browser. Independent outcome tests failed.
Source hashes remained unchanged through the run. Evidence: `results/milestone-followup.json`.
The saved menu also labels the Search button as empty because buttons can expose an empty value.
This is an incorrect description. Its effect on the incomplete submission remains unknown.

### Editable-field description experiment

Start: October 11, 14:01 PT. Owner: Codex task 16. One run, no concurrent inference.
Source commit: `100c9da2cad9676a7e6ef55a44d4179f0f9d5771`.
Command: `ZB_RECORD_PATH=artifacts/replay/field-description-local.jsonl uv run --offline --frozen --extra local python scripts/milestone.py --task local_search --ready`.
Evidence: `artifacts/milestone/local_search-<run-id>/`, replay above, and `results/milestone-followup.json`.
Only the editable-field description condition changes from the preceding experiment.
Dirty measured source: `jev_ultrafast/local_policy.py`, SHA256 `645e7b1b05c6851de0d8dc0f2ef72cf7670651b0ce691313081309606c7c81b2`.
The runner records all source hashes. Runtime files, prompts, fixture, and environment remain fixed during the run.

End: October 11, 14:02 PT. Slot idle. Record: `local_search-1791752516602899000`.
The first failure was step 1: Search before any requested field or control was set.
Seven decisions took 1,902–2,165 ms each. Nine model calls completed in a total of 19,938 ms.
Peak worker memory: 3,599,715,040 bytes, excluding the browser. The no-progress guard stopped the run at step 7.
No execution error or DONE decision occurred. Independent outcome tests failed.
The field-description error is fixed. It does not explain or fix the model's incomplete submissions.
No further inference is running. The milestone remains open with zero consecutive local successes.
Live Flights and both flight variations remain untested. Initial user responsiveness and cancellation observations remain satisfied.

Final delivery checks passed: lint and 124 tests in 4.60 seconds.
GitNexus impact and change analysis covered the affected policy flows. The MCP still reported stale data after a successful local rebuild.
Source inspection and the measured reruns remain the evidence for this change.

### Accuracy and continuity session

Thomas authorized 150 minutes on October 11, starting at 14:09 PT and ending at 16:39 PT.
This session replaces the earlier hackathon cut times. Speed work is paused.
Task 16 retains sole runtime ownership. No inference is running at session start.
The plan separates first-action accuracy from persistent task progress.
Diagnose saved states, compare two bounded local decision methods, then use the evidence to choose the next change.
Keep the existing goals, action boundary, runtime limits, and independent outcome tests.

Thomas shortened this session to about 20 minutes at 14:11 PT. Deliver evidence by about 14:31 PT.
Compare saved decisions and, if justified, one complete local task. Persistent task state remains pending until the decision method has evidence.

Saved-state diagnosis: all required controls and useful actions exist in the inspected initial, partial, reordered, and crowded states.
The latest first action is wrong with empty history. The policy has no explicit requirement or evidence-backed progress state.
Evidence: `results/decision-saved-diagnosis.json`.

Comparison command, once per method: `ZB_RECORD_PATH=artifacts/replay/diagnostic-<method>.jsonl uv run --offline --frozen --extra local python scripts/decision_diagnostics.py --cases fixtures/decision_saved_states.json --method <method> --output results/decision-diagnostic-<method>.json`.
The methods are `label` and `structured`. Each case has a 90-second external deadline and the existing worker memory limit.
Source commit: `833901e504d92098e0d4f7c121c1564c1f1a26d4`.
New measured source hashes before the comparison:

- `jev_ultrafast/structured_policy.py`: `ef30258d89f78dff28937799b0fc7ff3c1f8ee6209177724d2ac8f903838a684`.
- `scripts/decision_diagnostics.py`: `d225129eeb4cd8450ca8946a0133b7d32d959805ffd832a0449c0488f88234aa`.
- `fixtures/decision_saved_states.json`: `1e28efd2f64438551eba401c424a547f3ad411ffbd04109f2617946db9fa8080`.

The harness records all other source hashes. Freeze these files until both methods finish.

The first diagnostic attempt stopped before model loading: a relative case path failed source hashing.
The harness now resolves that path. Updated harness SHA256: `34933f274d9249ec344718dbcee4d877a097d6e28b3068204c68b1c33bf46924`.

### Bounded local worker scope

At 14:14 PT, Thomas replaced long-task planning with a bounded-worker proof. Preserve the shortened proof window.
The saved comparison completed: label scoring chose useful actions in 0/5 cases, structured responses in 3/5.
Structured responses still failed the partial and reordered cases. No full task or savings claim follows.
Evidence: `results/decision-method-comparison.json` and both detailed diagnostic files.
Build a small contract for one supplied field or option outcome. Stop on ambiguity, missing targets, uncertainty, or boundary violations.
Do not build a coordinator or persistent planning state in this proof.

Bounded-worker suite start: October 11, 14:17 PT. Source commit: `1089dac244aa1afe05ee0969c52d9a8e8c81e104`.
Command: `ZB_RECORD_PATH=artifacts/replay/bounded-structured.jsonl uv run --offline --frozen --extra local python scripts/worker_benchmark.py --method structured --output results/bounded-worker-structured.json`.
Eleven fixed cases: supplied text, dropdown, and autocomplete across normal, reordered, and distracting controls, plus ambiguous and missing targets.
The existing lock, memory monitor, cancellation, isolated browser cleanup, and per-case deadline remain active.
Source hashes before inference:

- `jev_ultrafast/bounded_worker.py`: `b3c5410ecb54f4894ccb90b3ab34eb3489c073717c961d220219683d05e7c958`.
- `jev_ultrafast/structured_policy.py`: `ef30258d89f78dff28937799b0fc7ff3c1f8ee6209177724d2ac8f903838a684`.
- `scripts/worker_benchmark.py`: `8419384699656d132fc0f7a3d8287baf2caac3d06d3ef325d5d95cbfd95b4220`.
- `fixtures/worker.html`: `2cc807af4696892f36530487beed5933693341b6ae01ebc4437ceabe3c70aa20`.
- `fixtures/worker_tasks.json`: `a1614f504490e90492b1e2d5e6d2643f72a1a0ac0880378d8a6ebd5210a52c46`.

The runner records all measured source hashes. No measured file changes until the suite ends.

The initial bounded suite ended: 6/9 actionable cases passed. Both ambiguous/missing cases correctly stopped without a model call or mutation.
Failures: fill-normal selected a forbidden field click, autocomplete-normal repeated field clicks, autocomplete-crowded exceeded the field boundary.
Evidence: `results/bounded-worker-structured.json`. No uncertain mutation was replayed.

One correction: restrict the model menu to the supplied field contract and omit actions that cannot change its current value.
This is deterministic contract enforcement, not an improvement in unrestricted model competence.
Rerun the same eleven cases and starting states with output `results/bounded-worker-constrained.json`.
Command: `ZB_RECORD_PATH=artifacts/replay/bounded-constrained.jsonl uv run --offline --frozen --extra local python scripts/worker_benchmark.py --method structured --output results/bounded-worker-constrained.json`.
Changed measured source: `jev_ultrafast/bounded_worker.py`, SHA256 `1839a4d4b66c1c26f5b07f355a7049bd6e2884c10d5834abc285906c7f0da2a5`.
The runner records all source hashes. Keep all measured source and fixtures fixed during this rerun.

The constrained suite passed all eleven assessments: nine requested outcomes and two safe uncertainty stops.
Evidence: `results/bounded-worker-constrained.json`. This supports the narrow contract, not unrestricted browser decisions.
The runner now accepts a supplied JSON request with `url` and `task`. Results include observed evidence, execution status, model calls, timing, and sampled worker memory.
A small correction reports the actual failed mutation step. The same runtime and fixture tests passed before repeat runs.

Repeat proof: three fresh suites with unchanged code and fixtures, starting at about 14:22 PT.
For trial N, command: `ZB_RECORD_PATH=artifacts/replay/bounded-proof-N.jsonl uv run --offline --frozen --extra local python scripts/worker_benchmark.py --method structured --output results/bounded-worker-proof-N.json`.
Changed source hashes before all three repeats:

- `jev_ultrafast/bounded_worker.py`: `4c05624eca7ff114b50f49cecfec74fa44462aba3b3c0ce770069e6ed37f59db`.
- `scripts/worker_benchmark.py`: `742afe81edcfa88dabca9ba15a5ca973ae401a287f7826e7e58f187e12dc07a7`.

The runner records all remaining source hashes. Freeze measured files through the three sequential suites.


### Bounded-worker delivery, October 11

All three frozen repeat suites passed: 27/27 requested outcomes and 6/6 safe uncertainty stops.
The source hashes are identical across the three suites. No false success, forbidden execution, or unresolved execution occurred in these runs.
Median actionable task time was 5,367 ms, median decision time 1,513 ms, with 36 model calls and a maximum sampled worker footprint of 3,343,338,352 bytes. Browser memory is excluded.
Evidence: `results/bounded-worker-summary.json` and the three linked raw result files.
The initial failed suite remains in `results/bounded-worker-structured.json`; contract filtering is the demonstrated correction.

The existing Codex chat observed Wikipedia's public portal, selected its Search Wikipedia control, and delegated one bounded fill request.
Command: `ZB_RECORD_PATH=artifacts/replay/bounded-wikipedia.jsonl uv run --offline --frozen --extra local python scripts/worker_benchmark.py --request artifacts/live-request.json --output results/bounded-worker-wikipedia.json`.
The request and observed target are reproduced in the public result manifest. Private observations and replay records remain under ignored artifacts.
A fresh observation showed the exact value Ada Lovelace, the same document and URL, and only one fill action.
The coordinator inspected this evidence and stopped. This is one live field subtask, not article retrieval or a complete browser workflow.
Worker time was 6,825 ms, with one 2,079 ms decision, 961 local prompt tokens, and 27 locally tokenized response tokens. These are not coordinator tokens.
Evidence: `results/bounded-worker-live-assessment.json` and `results/bounded-worker-wikipedia.json`.
The worker timing includes browser/model startup and cleanup, but excludes coordinator preparation and assessment.

The context coordinator relayed a request for a direct/delegated real-site comparison near the end of the shortened session.
No valid paired comparison was completed within the existing budget. A direct native-browser attempt also passed the exact field-value and unchanged-URL checks in 9,643 ms from tab opening to verification snapshot. It used an existing Chrome profile and included first-use tool documentation. The worker used an isolated profile and excluded coordinator preparation/assessment. Context was not isolated or equalized. The raw worker-minus-direct difference is -2,818 ms, but this is not a valid time-savings estimate. Full dispatch-to-assessment timing remains missing.
Read-only inspection confirmed per-request coordinator token counters in the existing local session log: input, cached input, cache-write input, output, reasoning output, and total. Exact benchmark attribution remains unproven because engineering and test work share the turn. No whole-chat totals are assigned to either path. Cached input is a subset of input, and reasoning output is a subset of output; do not add them twice. Exact token savings and dollar savings cannot be reported.
The next concrete experiment is the same live field goal through direct native browser control and worker delegation, with equivalent starting conditions and end-to-end timing.
Separate requests currently start separate browser sessions. Multi-subtask integration needs a retained owned session, observed result handoff, and cancellation across that session.

Later acceptance targets remain pending: unseen labels/values with 95/100 actionable trials, separate ambiguous/missing trials, a deterministic-helper baseline, and interruption/continuation with recoverable failure.
The exact supplied-label/value contract may not need an LLM; these tests do not establish a benefit from local inference.
The general agent's saved-state decision errors and failed full flight task remain unresolved. No live Flights run, persistent planning state, or savings claim is included.
Prior responsiveness and cancellation observations remain valid. No new user observation is required for this delivery.
The exclusive run slot is idle. Required delivery checks and publication follow below.

Final required checks passed: lint and 133 tests in 4.43 seconds. GitNexus rebuilt successfully; incomplete graph traces and a cross-language link remain index limits. No general completeness claim follows from the graph.


### Renewed matched comparison

Thomas renewed task 16 through the coordination chat, then explicitly approved sequential isolated Codex sessions as benchmark subjects. These sessions must not implement code or run concurrently. No new numeric budget was specified.
Task 16 retains the runtime slot. At claim time no browser experiment or inference is active.
First fix measurement: separate local imports/model acquisition, prompt preparation, generation, and result handling. Preserve current model decisions and safety.
Use equivalent fresh coordinator context, the same model and reasoning setting, the same public field task, fixed supplied values, and independent final field/URL checks.
Start timing before coordinator dispatch; end after independent assessment and the coordinator verdict. Keep cleanup separate. Preserve raw private events and publish only sanitized counters and outcome evidence.
Exact request usage must be deduplicated by response ID. Do not double-count cached input or reasoning output.
