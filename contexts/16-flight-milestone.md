# 16 Flight demonstration milestone

Priority P0. Owner Codex milestone chat.

Current scope: the bounded-worker proof and authorized shared-interface coordinator comparison are delivered. Runtime is idle. Native desktop CUA comparison, multi-step efficiency, and the original flight milestone remain open. The original plan below is historical; the latest Result entries and STATUS banner control current work. The browser worker remains local. The comparison used explicitly authorized Codex CLI coordinators through the existing login, with no hosted model client added to the repository.

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

Five matched pairs authorized through the coordination chat: A/B, B/A, A/B, B/A, A/B. A is direct Codex over the shared observed-action MCP interface. B delegates that field contract to local Qwen. This does not measure the desktop native CUA stack.
Coordinator: installed Codex CLI, gpt-6-astra, high effort, fresh session and identical instructions/tools. Local inference remains pinned Qwen3-4B and sequential.
Timing instrumentation adds imports, model acquisition, prompt preparation, generation, and result handling. No model behavior or cache policy changes.
Required checks before source freeze: lint and 133 tests passed. GitNexus reports shared worker/diagnostic callers; the cached MCP index remains behind the local rebuild.
Measured command: `ZB_RECORD_PATH=artifacts/replay/paired-series.jsonl uv run --offline --frozen --extra local python scripts/paired_browser_benchmark.py --output results/paired-browser-five-pairs.json`.
The harness sets a distinct per-run replay path and records each private journal hash. Deadline: 90 seconds per coordinator after browser startup; local delegation has an external 30-second deadline. Parent cleanup owns the isolated browser and coordinator process group.
The runner includes source commit and full source hashes, and verifies them after each trial. Freeze measured files through the series. Preparation hashes:

- `scripts/paired_browser_benchmark.py`: `a54d53ca84d0c556ce4f39d981a98b5502b89eaf6e6f5667d4e89af45a26c9a6`.
- `scripts/paired_browser_server.py`: `74878b941b7f90477c03e50cd00e5c24a7afe83ed4bcf85abecbb82df436194a`.
- `jev_ultrafast/structured_policy.py`: `0e328645643e9c3476098c86922c2805fcda45568f83a5ff3edb451b76f8b8b2`.

Final freeze hashes after preflight evidence corrections:

- `scripts/paired_browser_benchmark.py`: `17fa29fe6f81cb12d03f1de7641561c05a6c83b46ccd813fc13d20b73cacf229`.
- `scripts/paired_browser_server.py`: `74878b941b7f90477c03e50cd00e5c24a7afe83ed4bcf85abecbb82df436194a`.
- `jev_ultrafast/structured_policy.py`: `0e328645643e9c3476098c86922c2805fcda45568f83a5ff3edb451b76f8b8b2`.
All script imports and the dependency lock are included in the measured manifest. Both pre-coordinator startup and coordinator-dispatch-to-verdict are reported; their sum is the cold goal-dispatch-to-verdict interval.


First series failure at commit 697c633: the CLI did not inherit owned browser environment settings into the MCP server. Observation failed before any mutation. The coordinator returned a blocked verdict. Sampling the already-exited MCP process then caused a conservative supervisor stop; nine remaining trials are explicitly not run.
Evidence: `results/paired-browser-five-pairs.json`. Preserve this failed series and do not include it among successful pairs.
Fix: pass only the owned browser/offline/replay environment explicitly in per-invocation MCP config. If the MCP child has exited, sample the still-owned coordinator wrapper rather than treat normal shutdown as lost memory monitoring.
Rerun command uses `--output results/paired-browser-five-pairs-v2.json`, with the same ten-trial order, goals, and checks. Source will be frozen at the next commit.

The model-free transport preflight passed: an explicit MCP environment reached the isolated browser and observed the empty Wikipedia field, with zero mutations. Evidence: results/paired-transport-preflight.json. Private preflight source SHA256: 2284c5acaab506a28ca7d53a645859f968d8369afe4b11acf8301f4f4fb5ced2.
Normal MCP shutdown is tolerated only for ESRCH plus a failed signal-zero existence check. Permission and other sampling errors still stop the series.
New frozen runner hash: 848807b1c1a5ec4fa394457c098685c89c066ba773e1632c6fcbe5b59d674007. No other measured source changed after series 1.


Series 2 at c769e6b stopped through the supervisor cancellation handler after the context coordinator requested a review hold. Evidence remains unchanged in results/paired-browser-five-pairs-v2.json.
Two direct attempts failed on StalePage before browser mutation. The direct wrapper marked that pre-execution rejection uncertain; the local worker could observe again internally. This recovery difference invalidates a fair completion-rate comparison. Two delegated attempts passed. The fifth attempt was interrupted during the stop and recorded an operation-not-permitted error; its exact cause is not yet established. Five later trials are explicitly not run.
The accounting records reconcile for completed turns. Runtime source hashes remained unchanged through each attempted trial. No efficiency claim follows from this incomplete unequal-recovery series.
The task is holding runtime source unchanged while the comparison reviewer checks the recovery contract. The run slot is idle.


The independent comparison review confirmed the StalePage asymmetry. The direct wrapper now removes its pending mutation only for a known rejection before input, records that rejection, and permits a fresh observation and decision. Both paths stop after three rejected decisions. Other exceptions remain uncertain and cannot be replayed.
A small deterministic regression test distinguishes StalePage from a connection failure after possible dispatch. A process check found no owned coordinator, MCP, or isolated-browser processes left after cancellation.
The runner now accepts `--stop-file artifacts/paired-series-v3.stop` to stop after an active trial without interrupting it. The next frozen series uses `results/paired-browser-five-pairs-v3.json` and the same ten-trial order. Prior series remain unchanged and invalid for an efficiency comparison.


### Controlled comparison result

Frozen runtime commit: `9d506df820b9c579c7b7f559da51803a5a3debe8`. All ten planned trials completed with independently correct field values and unchanged URLs: direct 5/5, delegated 5/5. Every trial kept measured source unchanged. Per-response usage IDs are unique and reconcile with turn totals.
Evidence: `results/paired-browser-five-pairs-v3.json` and `results/paired-browser-comparison.json`. Earlier failed/incomplete series remain separate and unchanged.
One measurement error is disclosed: a 3.7-second GitNexus index refresh overlapped pair 4's direct trial and ended at 21:43:05 UTC. Pair 4 remains in the table but is excluded from primary timing conclusions. Automatic approval review rejected a proposed supplemental pair as beyond the authorized five-pair scope. No supplemental run occurred before the later explicit user approval recorded below.
Across the four pairs without that known overlap, median delegated-minus-direct cold-start-to-verdict time was -2,061.30 ms, range -2,776.34 to -404.14 ms. The coordinator-dispatch-only median difference was -2,032.94 ms. Cleanup is separate.
The median coordinator total-token difference for those four pairs was -42,637.5 tokens, including cached input. Median uncached-input difference was -4,951 tokens. All-five descriptive medians were -1,904.54 ms and -43,063 total coordinator tokens. These are token accounting, not dollar billing.
Direct trials needed seven coordinator responses each, including recovery from one known pre-input page change. Delegated trials needed five coordinator responses and one local Qwen call each. The shared guarded executor and live-page changes explain the extra exchanges; this is not a native desktop CUA benchmark.
The median measured local wrapper was 4,168.03 ms. Per-component medians: imports 828.86 ms, model acquisition 1,291.69 ms, prompt preparation 10.22 ms, generation 2,152 ms, result handling 0.50 ms. Component medians need not sum to the median total. No speed optimization was applied.
The maximum sampled MCP worker footprint was 3,411,528,464 bytes for delegation and 63,865,360 bytes for direct execution. Browser and coordinator-client memory are excluded from those peaks.
This is exploratory evidence for one supplied-value field task. It does not prove multi-step workflow efficiency, native browser-tool superiority, general reliability, or that Qwen is needed instead of a deterministic helper. Provider cache state, OS file caching, live content, and network timing were uncontrolled and are disclosed.
No new responsiveness observation is required. The run slot is idle. A deterministic-helper comparison and a meaningful multi-step task remain the next product decisions.

Independent read-only audits passed accounting and outcomes: 60 unique response IDs across ten sessions, exact usage reconciliation, all 36 source hashes unchanged, all initial fields empty, and sequential starts after prior cleanup. The reviewers confirmed that pair 4, not pair 2, contains the indexing overlap.
All-five coordinator totals: direct 609,188 tokens versus delegated 395,227 (35.12% fewer). Uncached input: 105,781 versus 78,236; cached input: 502,400 versus 316,288; output: 1,007 versus 703. Qwen added 4,954 prompt tokens and 130 retokenized response tokens, recorded separately. These counts do not establish dollar charges.
The four-pair timing subset has direct/delegated coordinator totals of 485,027 and 317,883. The full summary includes all per-run splits and signed paired differences, including the flagged original pair.

Final delivery checks: lint passed and 135 tests passed in 4.55 seconds. GitNexus impact/context and final comparison analysis covered the changed decision and benchmark flows. The index has truncated flows and an unresolved cross-language link; it is supplementary evidence. Published records passed the private-path and credential scan.

Thomas explicitly authorized one supplemental sequential pair after publication. It uses delegated/direct order and the same 36 measured source hashes as 9d506df, verified before startup. Current documentation-only HEAD: f92b914594f375c7616dbd0dc3e4b73e2deb4cf8. Command: `ZB_RECORD_PATH=artifacts/replay/paired-supplemental.jsonl uv run --offline --frozen --extra local python scripts/paired_browser_benchmark.py --order delegated,direct --output results/paired-browser-supplemental.json --stop-file artifacts/paired-supplemental.stop`. No background tests, indexing, or other analysis work will run during measurement. Preserve the original ten attempts unchanged.


### Authorized supplemental result

The user approved one extra sequential pair after the original delivery. Both trials passed independent field-value, unchanged-URL, and resolved-execution tests. No background indexing or tests ran during measurement. The runtime is idle.
Evidence: `results/paired-browser-supplemental.json`. Delegation took 16,960.24 ms and direct execution took 18,568.92 ms from cold startup to verdict. The signed difference was -1,608.68 ms. Cleanup remained separate. Both paths executed one field mutation. Direct execution recovered from one known pre-input rejection. Delegation used one local model call.
The summary retains the original ten rows, all five original pairs, and the earlier four-pair statistics. It adds the supplemental pair separately. The current comparison set contains original pairs 1, 2, 3, 5 and supplemental pair 6. This is a sensitivity comparison, not one uninterrupted randomized series.
Its median paired time difference is -1,904.54 ms, with a range of -2,776.34 to -404.14 ms. Median paired coordinator usage decreased by 42,212 total tokens and 3,202 uncached input tokens.
Aggregate coordinator usage was 605,218 direct versus 396,644 delegated, a 34.46% reduction. Input totals include cached input. Uncached input was 112,702 versus 78,753. Cached input was 491,520 versus 317,184. Output was 996 versus 707. Local Qwen added 4,997 prompt tokens and 130 retokenized response tokens. These counts do not establish dollar charges.
Independent read-only audits passed outcomes, timing, source integrity, and accounting. All 72 response IDs across twelve completed trials are unique. Supplemental usage matches both complete private sessions. The instruction hash and all 36 runtime hashes match the original frozen source.
No further measurements are authorized or planned in this delivery. Shared-interface behavior, uncontrolled caching, network timing, and the narrow field task limit interpretation. A deterministic helper and a useful multi-step workflow remain untested. No new responsiveness observation is needed.

Supplemental delivery checks passed: lint and all 135 tests in 4.72 seconds. No measured source changed. Public evidence passed the private-path and credential scan.


### Multi-step worker reuse and native comparison

Thomas explicitly authorized the next experiments in the coordination chat after field delivery `bb6c545`. The fixed workflow starts at Wikipedia, searches for Ada Lovelace, follows the article link to the Analytical Engine, and returns its inventor with supporting URLs. The evaluator requires observed navigation and source text. Expected answers stay outside subject prompts.
Experiment 1 contains four attempts: reload, persistent, persistent, reload. Both modes preserve one browser through the workflow. Reload starts a new model process per subtask. Persistent reuses one model process. The main timer includes the initial load. No prompt or KV-cache changes are permitted.
Experiment 2 uses actual native Codex desktop browser tools. A fresh agent exposed `mcp__cua_repl` and the In-app Browser provider. It supports fresh tabs but does not establish isolated cookies. Hosted agent context and tools differ from stripped CLI sessions, so this comparison cannot claim fully controlled conditions.
The native capability probe opened no website. Its session ID is `01a12cf2-bae9-7712-b0af-455d81db0546`. Planned evidence: `results/workflow-reuse.json` and `results/workflow-native-comparison.json`. Task 16 owns the browser and inference slot. Implementation and delivery checks precede source freeze.

The minimum implementation separates the browser from a JSON decision subprocess. Both modes retain the browser. Actual first loads and process IDs accompany each local call. The shared session stops after uncertain execution or a failed subtask. Navigation is restricted by caller-supplied hosts. The benchmark evaluator separately requires search submission, both articles, the observed article link, supporting text, and the returned answer and URLs.
Model-free tests cover ambiguous controls, uncertain mutation handling, and each route requirement. Lint and 143 tests passed before the initial measurement freeze. GitNexus reports low runner impact. Its index has truncated flows and a cross-language link gap.

Frozen runtime: `3fd39363790f3927af9bd186eca920a05230348f`. Command: `ZB_RECORD_PATH=artifacts/replay/workflow-reuse.jsonl uv run --offline --frozen --extra local python scripts/paired_browser_benchmark.py --workflow --order reload,persistent,persistent,reload --output results/workflow-reuse.json --stop-file artifacts/workflow-reuse.stop`. The runner records all measured source hashes. Initial model load stays inside the full timer. `model_load_ms` is nested within acquisition time and must not be added twice. Generation timing currently combines prompt processing and token generation. Exact per-subtask coordinator token allocation is unavailable. Full-attempt response-ID totals remain exact.

The four reuse attempts ended before Thomas changed scope. All raw outcome flags are false under the defective frozen oracle. Saved evidence supports separate reassessment. No native workflow trial started. Thomas replaced the remaining paired/native experiments with a focused bounded-task improvement and exactly one live workflow attempt. The new candidate requires model-free tests and two focused read-only reviews before measurement. No additional trial is authorized after failure.


### Focused bounded-delegation candidate

The candidate gives Qwen a dedicated bounded prompt without the general NEXT_ACTION instructions. `search_open` fills a supplied field deterministically, chooses observed controls locally, and stops at its explicit page-title/text predicate. Exact fill, observed-link navigation, and scroll operations execute without model approval. Returned results distinguish execution, page change, and predicate success. Each successful subtask returns its fresh observation for the coordinator's next decision. Freshness guards still run before input.
The corrected evaluator uses the exact observed article URL and ordered query, result, article-link, destination, and supporting-passage evidence. All four previous attempts pass separate retrospective assessment in `results/workflow-reassessment.json`. Original raw failures in `results/workflow-reuse.json` remain unchanged. One reload attempt used an additional scroll, so its total-time difference does not isolate model lifetime. Native pairs remain unrun under the user's scope change.
The next run is exactly one attempt: `ZB_RECORD_PATH=artifacts/replay/workflow-focused.jsonl uv run --offline --frozen --extra local python scripts/paired_browser_benchmark.py --workflow --order persistent --output results/workflow-focused.json --stop-file artifacts/workflow-focused.stop`. Initial local model startup is inside the timer. No retry, replacement, or extra trial follows a failed attempt. Focused source and protocol reviews must approve the frozen candidate first.

Thomas separately assigned an optional deterministic observation compactor in another worktree from `3fd3936`. Reserved supporting files: `jev_ultrafast/observation_compactor.py`, `tests/test_observation_compactor.py`, `scripts/assess_observation_compactor.py`, and `results/observation-compactor.json`. No active-runtime integration or browser/model run is permitted. Its owner received an idle slot for required checks and must report completion before the one live trial.

Focused review corrections are complete. The worker requires an exact observed main heading for search result identity. Redirects require observed article identity and canonical destination evidence. Missing controls remain known no-input failures. Failed subtasks preserve earlier execution and page-change facts. The independent evaluator ties each search action to observed controls, preserves ordered route evidence, accepts affirmative inventor answers, and rejects negation. Lint and 151 tests passed in 4.64 seconds. The compactor owner confirmed idle and holds all resource-intensive work. The single attempt starts only after the final narrow assessment review, with no broader review gate.
