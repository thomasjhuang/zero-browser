# 16 Flight demonstration milestone

Priority P0. Owner Codex milestone chat.

Current scope: deliver the callable action adapter and preserved comparison evidence. All measured attempts ended. The worker and browser closed. No further runtime work is active. General reliability and savings remain unproven.

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

Both focused reviewers passed the exact final candidate. Frozen source: `9a47df995003c16ac5cedcc9aec7562f2e84e6bf`. The previously recorded one-attempt command starts now. All reviewed runtime hashes match. No background indexing, tests, compactor work, or other inference runs during measurement.


### Single focused workflow result

Exactly one attempt ran at `9a47df995003c16ac5cedcc9aec7562f2e84e6bf`. Evidence: `results/workflow-focused.json` and `results/workflow-focused-summary.json`. The independent outcome failed. The worker searched and opened Ada Lovelace in one 10,256.51 ms subtask. It returned the actual page and the analytical engine link. The coordinator used that observation without an extra observe call.
The next subtask requested the observed link. Its fresh observation contained donation controls and omitted that link from the visible action list. Two common controls moved down 549 pixels. This supports viewport displacement, but the target rectangle after the change was not recorded. The worker returned `missing_target` in 22.59 ms, with no input and no unresolved execution. The coordinator stopped without asserting an inventor.
The earliest guard rejection occurred during search: the first Qwen decision failed a pre-input freshness check. A fresh local observation and decision then opened the correct article. The saved rejection does not identify the exact changed marker component. This differs from the terminal missing-control failure.
Full startup-to-verdict time was 29,287.12 ms, with 1,231.87 ms cleanup separately. Six coordinator responses used 129,796 input tokens, including 73,856 cached tokens, plus 286 output tokens. Total: 130,082. Uncached input: 55,940. Two local calls used 4,219 prompt tokens and 55 retokenized response tokens. One model process loaded once. The actual weight load took 1,432.005 ms inside the larger acquisition interval.
The run executed two mutations: deterministic query entry and a Qwen-selected search result click. Sampled combined MCP/model memory peaked at 3,808,529,624 bytes. Browser and coordinator-client memory are excluded. Model timing combines prompt processing and token generation. No phase medians or nested durations are added together.
Independent audits passed exact token reconciliation, all 39 unchanged source hashes, action accounting, and correct failed-outcome reporting. Earlier raw runs remain unchanged. Their different prompts, action counts, and verdicts prevent a direct savings claim. Native desktop workflow comparison remains unrun.
The next proposed build is bounded recovery for a previously observed control that leaves the visible action set. Use observed scrolling and unchanged freshness safeguards. This delivery does not implement or test that recovery. No additional trial ran. No new user responsiveness observation is required.

Final delivery checks passed: lint and 151 tests in 4.45 seconds. Public evidence passed the private-path and credential scan. Prior raw result hashes remain unchanged. The runtime is idle.


### One bounded recovery and additional attempt

Thomas explicitly authorized minimal recovery and exactly one additional live attempt. Recovery is allowed only after confirmed non-execution with a missing target. The coordinator receives the fresh observation and chooses one permitted observed action. After that action, the worker observes again. It continues the original operation only if the original target is uniquely available. Unknown execution stops without replay. The prior failed result remains unchanged. No banner, site, selector, or answer rule is added.
The optional compactor is complete in detached candidate `1f1ccd400e8ad3c11d5763ce932c89aca946e11a`, with independent review. Runtime integration remains pending and is excluded from this trial.

The recovery implementation permits one coordinator-selected observed click or scroll after a known missing-target stop. It checks that the selected recovery control still matches its observed node and semantics. Existing freshness and action guards run before input. After one recovery action, the original operation continues only if its target is uniquely observed. A second recovery request is rejected. Unknown input results never reach continuation.
Command: `ZB_RECORD_PATH=artifacts/replay/workflow-recovery.jsonl uv run --offline --frozen --extra local python scripts/paired_browser_benchmark.py --workflow --order persistent --output results/workflow-recovery.json --stop-file artifacts/workflow-recovery.stop`. Exactly one additional attempt is authorized. The previous focused raw result and summary remain unchanged. No compactor changes are included.

Model-free checks passed: lint and 159 tests in 4.45 seconds. Focused regressions cover confirmed non-execution, unknown-result stops, one recovery action, unique-target continuation, and rejection of a second recovery. GitNexus found the shared workflow paths affected and reports high aggregate impact. Source inspection and tests cover those paths. The MCP index retains stale metadata and truncated flows, so it does not establish completeness. The compactor owner explicitly confirmed idle.

Recovery trial source freeze: `e45aa7e761192c4e6a7983f075b9843d9bd6a9cb`. The recorded recovery command starts now. No other browser, local inference, indexing, or tests are active.


### Additional recovery-enabled attempt result

Exactly one additional attempt ran at `e45aa7e761192c4e6a7983f075b9843d9bd6a9cb`. Evidence: `results/workflow-recovery.json` and `results/workflow-recovery-summary.json`. All independent route and answer checks passed. The worker opened Ada Lovelace, followed the observed analytical engine link, and returned Charles Babbage with the supporting article passage and URLs.
Recovery was not invoked. This result demonstrates one complete workflow, not live recovery effectiveness or general reliability. The previous failed raw result and summary are unchanged. No extra trial or replacement ran.
Full startup-to-verdict time was 29,904.54 ms. Cleanup took 1,035.17 ms separately. Search-and-open took 10,061.98 ms. The exact link subtask took 109.89 ms. The run executed three mutations: deterministic query entry, a Qwen-selected result click, and deterministic article-link navigation. One earlier Qwen decision encountered a known pre-input freshness rejection. A fresh decision succeeded. There was no terminal failure or uncertain mutation.
Six coordinator responses used 132,957 input tokens, including 103,424 cached tokens, plus 315 output tokens. Total: 133,272. Uncached input: 29,533. Two local calls used 4,219 prompt tokens and 55 retokenized response tokens. One local process loaded once. Sampled MCP/model memory peaked at 3,815,345,368 bytes, excluding browser and coordinator-client memory. Initial load is inside total time. Local generation timing still combines prompt processing and token generation.
All 39 measured source hashes remained unchanged. The previous incomplete task is not a comparable speed baseline. Compactor integration and native desktop workflow comparison remain untested. The one recommendation is a controlled browser fixture that reliably removes and restores a target, to exercise the bounded recovery end to end. That proposed work is not started here. No new responsiveness observation is needed.

Final evidence delivery checks passed: lint and 159 tests in 4.20 seconds. The public evidence contains no detected private paths or credentials. Previous focused result files remain unchanged.


### Native desktop baseline and coordination error

Thomas authorized one fresh desktop task and one native-browser attempt after the recovery result was published in `17e7cc5`. Automatic approval review rejected the first task16 creation because it did not accept cross-chat authorization. That rejection started no task. Thomas then approved creation directly in task16. The coordination chat also created a task before it received task16's success notice. This race created two overlapping browser attempts. The later task received STOP after its three browser mutations finished. Both tasks stopped. No replacement ran.

Evidence: `results/native-desktop-comparison.json`. Both fresh projectless tasks used gpt-6-astra with high reasoning and normal desktop CUA tools. Independent saved observations establish the portal, query entry, Ada Lovelace article, observed analytical engine link, destination article, supporting passage, and answer URLs. Both routes and answers passed. This is a preliminary product comparison with a protocol violation. It is not a controlled architecture experiment or a valid sequential timing comparison.

The retained attempt took 38,505.201 ms from pre-creation dispatch to final-answer emission. It used seven coordinator responses and 515,187 total tokens: 514,692 input, including 417,792 cached, and 495 output. Uncached input was 96,900. The accidental duplicate took 32,027.126 ms. It used six responses and 370,897 total tokens: 370,440 input, including 299,904 cached, and 457 output. Uncached input was 70,536. Each original turn's usage reconciles independently. These counts exclude approval-review sessions, parent coordination, and later cleanup. They do not establish billed cost.

Native timing includes task and browser startup, tool initialization, skill loading, and final response generation. It excludes polling delay and later cleanup. Local wall-clock dispatch and raw millisecond log timestamps limit precision. Both native browser/model sessions overlapped. Browser profile, cookies, caching, provider, desktop tool context, and live page state differ from the system run. Native Search submission also differs from the system autocomplete choice. The saved system run took 29,904.535 ms, but these samples do not establish a speed advantage. Native memory was not sampled. All 39 system source hashes remain unchanged.

The overlapping comparison is excluded. The separately authorized sequential result follows below.


### Separately authorized sequential native baseline

Thomas authorized exactly one new native attempt after the overlap. The coordination chat was the sole launcher. Task16 and the compactor stopped all resource-intensive work. Both old tabs closed and their tasks became idle before the new dispatch. Task16 read saved evidence only after END. No implementation changed.

Evidence: `results/native-desktop-sequential.json`. The fresh gpt-6-astra/high task used normal desktop CUA tools and a new IAB tab. Independent saved observations passed all eleven route and answer conditions. The task entered the supplied query, submitted with Return, opened Ada Lovelace, clicked its observed analytical engine link, and returned the supported inventor and URLs. It executed three browser mutations plus tab creation. No local model ran.

Dispatch was 22:25:41.870258 UTC. The raw final answer emission was 22:26:14.922 UTC. Total time was 33,051.742 ms. Seven unique response-item records reconcile to 516,054 coordinator tokens: 515,594 input, including 418,688 cached, and 460 output. Uncached input was 96,906. These original-turn counts exclude separate approval-review sessions, parent coordination, and cleanup. Native memory was not sampled. The initial raw session was preserved before cleanup.

The successful system reference took 29,904.535 ms and used 133,272 coordinator tokens plus two local calls. The observed time difference was 3,147.207 ms. Both totals include startup and the final verdict. Native ends at raw final-answer emission, while the system ends at verdict receipt. Clock precision and transport therefore differ. Browser caches, profile, tool interface, model context, and website state were not controlled. The native task submitted search, while the system selected autocomplete. This single preliminary product comparison does not establish a general speed, architecture, reliability, or billed-cost advantage. The earlier overlapping attempts remain preserved and excluded. All 39 system source hashes remain unchanged.

The recommendation is to demonstrate the current Wikipedia workflow with its observed route and source evidence. Present feasibility, not general speed or live recovery effectiveness. No further experiment or implementation is included. No new user responsiveness observation is needed.

All three native benchmark tabs closed after their measured verdicts. The sequential close operation took 1,668.3 ms, outside benchmark timing. Its cleanup turn used 238,427 tokens, recorded separately. Lint and 159 tests passed in 4.65 seconds. Earlier system evidence remains unchanged. Public evidence passed the private-path and credential scan.


### One-off Google Flights demo handoff

Thomas authorized one visible live attempt through the existing local system. The request is round-trip SFO to JFK, November 12–16, 2026, one adult, Economy. This explicit one-off authorization replaces the old local-readiness sequence for this attempt only. No local-flight success claim follows. Sol comparison is deferred.

Task16 prepared ignored `artifacts/flights-demo-once/launch.py`, `request.json`, and `prepared.json`. The launcher calls the existing milestone worker under cancellation, single-run, isolated-browser, memory, and external-deadline guards. It does not change the policy, browser, model, or executor. The limit is 90 seconds for the worker and 20 decisions. Existing browser startup can add up to 20 seconds. Cleanup is separate. An exclusive attempt marker prevents a second launch, including after a failure or interruption.

Only the root coordination chat, Define agent success targets, can execute this command after acknowledging the idle handoff:

```sh
ZB_RECORD_PATH=artifacts/replay/flights-demo-once.jsonl uv run --offline --frozen --extra local python artifacts/flights-demo-once/launch.py > artifacts/flights-demo-once/console.log 2>&1
```

Frozen runtime source is `0323faea501b5128e815ed4d32b39746e76cfb02`. Launcher SHA-256: `ac24db89b214141606e8492680fde067645404d8f45cb21e143fbdd0ace1c71a`. Request SHA-256: `9bcf9d2294a1bc105c9c6245e349ae418ff2e51050820558fbb7305370676430`. The prepared record contains each runtime source hash. The launcher compares them before any browser startup and after cleanup. Conditions also record the actual launch commit. No measured runtime file can change until END.

The legacy one-way verifier remains unchanged and is explicitly NOT_APPLICABLE to the complete round-trip outcome. Preserve its raw result. Independently assess saved observations for round-trip mode, exact SFO/JFK airports, both dates and year, one adult, Economy, and visible results. Report up to three observed options with currency, price basis, carrier, times, and stops. Mark missing facts unavailable. Do not infer a booking quote or success from DONE.

The runner stops for human verification, forbidden search actions, uncertain execution, repeated stale decisions, memory pressure, or exhausted budgets. The first event failure and any unresolved mutation remain in the saved records. Runtime summaries separate full elapsed time, browser startup, worker/supervisor duration, and browser cleanup. The worker interval includes its process cleanup. No replacement run is authorized.

Preparation syntax passed without importing the model or browser. The compactor confirmed idle. Task16 remains idle and transfers only the single execution slot to root upon acknowledgment. Source editing remains frozen.

Handoff delivery checks passed: lint and 159 tests in 4.72 seconds. Only the existing task and status records are committed. Launcher, request, and private records remain ignored. No demo started during preparation.


### One-off Google Flights result

The root coordination chat launched exactly one attempt at `074db4c0708fa8ba49f8b3023ad52d5948ba9c79`. Evidence: `results/flights-demo-once.json`. The general autonomous local Qwen runner failed before selecting JFK or entering either date. No Codex coordinator operated inside this run. This does not test one-call delegation, the successful Wikipedia hybrid workflow, or unintegrated optimization proposals.

Step1 chose the correct destination field and entered the supplied full airport name. The page then showed “No matching locations found.” That feedback persisted. The trace does not establish why the provider returned no match or whether a shorter query would work. Step2 selected “Destination, Select multiple airports” despite the single-destination request. The editable field and no-match feedback were present in the model input. The subsequent decisions did not recover. The model waited thirteen times, entered the identical query again, reopened the field, and scrolled twice.

One stale decision at step3 stopped before input. Two layers logged that single rejection. No uncertain mutation remained, and the model never chose DONE. The twentieth decision exhausted the fixed budget. This was not a 90-second timeout or a false completion.

Independent requirement assessment found no selected JFK destination, no departure or return date, no verified year, and no flight results. The initial origin showed San Francisco without an exact SFO identifier. Initial Round trip and Economy controls were visible, but the final view did not expose the form. The passenger control showed one passenger without an adult breakdown. The final page text was blank after scrolling. No result options, prices, carriers, times, or stops are reported. The unchanged one-way verifier remains explicitly NOT_APPLICABLE to the full round-trip request.

Total startup-through-cleanup time was 39,497.65 ms. Browser startup took 580.25 ms. The worker and its process cleanup took 38,530.49 ms. Browser cleanup took 365.60 ms. Twenty decisions used 23 local model calls: 21 menu scoring calls and two field-text calls. One physical model load took 1,901.81 ms. Nineteen executed operations comprise six browser mutations and thirteen waits. Median decision time was 1,306.5 ms. Peak sampled worker memory was 3,759,278,816 bytes. Browser and parent memory are excluded. Field-text token totals were not recorded. Parent engineering chat usage is not attributable to a benchmark coordinator.

All nineteen recorded source hashes remained unchanged before and after the attempt and during assessment. The existing cancellation, memory, single-run, action-boundary, and decision-limit guards stayed in place. Private events, conditions, launcher, and request are preserved with hashes in the public assessment. The browser context returned through owned cleanup. No new user responsiveness report was requested. The earlier computer freeze remains unexplained.

Runtime is idle. No replacement, comparison, or optimization follows this attempt. The demonstrated problem is failure to respond effectively to observed no-match feedback. Resolve that behavior before presenting a complete flight-search demonstration. This record does not authorize that future work.

Final delivery checks passed: lint and 159 tests in 4.92 seconds. Public evidence passed the private-path and credential scan. Earlier comparison results and all nineteen runtime source hashes remain unchanged.


### JFK-only coordinator handoff candidate

Thomas authorized one correction and then narrowed the pending attempt to selecting JFK as destination. Root coordination is the sole launcher. The candidate adds an optional error/nonprogress handoff to the existing guarded runner. It returns current observations and remaining budgets through `handoff.json`. Root supplies one natural-language `correction.json` with the matching `handoff_id`. No correction is preloaded. The worker reobserves, retains its original goal and boundaries, clears old text-helper reuse, and resumes the same Agent, browser, and loaded model. Further error or nonprogress stops. Human verification and unknown input never reach this handoff.

Both segments and coordinator wait share a 90-second external deadline and twenty local decisions. A generic field-selection guard prevents unrelated field changes, search submission, and nonmatching option clicks. Independent success requires a matching observed option click followed by a unique closed populated destination field. Typed text and DONE are insufficient. Unknown option semantics fail closed.

Prepared command, for root only after source freeze and acknowledgment:

```sh
ZB_RECORD_PATH=artifacts/replay/flights-handoff-once.jsonl uv run --offline --frozen --extra local python artifacts/flights-handoff-once/launch.py > artifacts/flights-handoff-once/console.log 2>&1
```

The ignored folder contains launcher, request, prepared hashes, live handoff/reply, and durable evidence. The launcher refuses a second attempt. It verifies source hashes and computes one shared deadline before browser startup. The full-flight failed evidence remains unchanged. No browser or model ran in preparation. GitNexus refreshed the main index and found low direct impact for run_task; aggregate shared-runner impact is high. Truncated flows limit graph completeness. Source inspection and focused model-free regressions cover the changed path.


### JFK-only handoff result

[Saved evidence](../results/flights-handoff-once.json) records one failed attempt on `2f1b5234294aa9cef5f04e87502a286c30353930`. Root launched the prepared command once. No runtime source changed during the attempt.

Step 1 filled the destination field with `John F. Kennedy International Airport (JFK)`. The page returned “No matching locations found.” The trace does not establish why that query produced no matches. The worker returned early with the observed field and error. Codex supplied one correction: replace the observed destination query with JFK, then select the matching airport suggestion.

The worker reobserved before resumption. Step 2 selected `Destination, Select multiple airports` instead of typing into the available `Where else?` field. The field-selection guard stopped that click before execution. This was an incorrect decision with sufficient observed controls for the correction. It was not a missing-control problem, an execution failure, or premature DONE. The model's internal cause remains unknown.

Independent assessment of the saved observations and actions found no selected JFK airport. Only the first field fill executed. No matching suggestion was clicked, and the corrective JFK query did not execute. The boundary stop preceded the automatic final verifier, so its result is absent. There were no uncertain mutations or DONE choices. The parent returned exit code 1 and completed browser cleanup.

Total startup-through-cleanup time was 22,699.69 ms. Browser startup took 439.10 ms, worker plus process cleanup took 21,867.60 ms, and browser cleanup took 364.10 ms. Two decisions took 4,486 and 1,109 ms. Four local calls comprised three menu calls and one field-text call. One physical model load took 1,320.05 ms. Peak sampled worker memory was 3,825,847,032 bytes, excluding the browser and parent.

The handoff began 5.61 seconds after model loading finished. The correction arrived after 10,015.28 ms, and resumption followed after 10,019.57 ms. The worker PID and browser target stayed identical. The record contains one model load. Nineteen decisions remained at both handoff and resumption. The shared deadline decreased from 79.01 to 68.99 seconds remaining. The budgets did not reset.

All twenty runtime source hashes remained unchanged before and after the attempt and during assessment. Private events, replay, request, and correction remain preserved with public hashes. Root reported unrelated user applications active during preflight. This is one functional demonstration, not an isolated timing comparison. Coordinator tokens are not separately attributable to this attempt. Field-text token totals are unavailable. No new user observation was requested. The earlier computer freeze remains unexplained.

The handoff mechanism worked, but live airport selection and recovery failed. No retry, optimization, or implementation change followed. Existing earlier evidence remains unchanged. Runtime is idle.

Delivery checks passed: lint and all 184 tests in 4.59 seconds. Public evidence passed the private-path and credential scan.


### Single-action candidate

Thomas authorized one new JFK-only attempt with Codex control between individual actions. Root is the sole launcher. `scripts/single_action_worker.py` exposes one observation and waits for a matching request. Exact requests use supplied values and uniquely observed targets. Local selection requests contain at most twenty permitted observed clicks. The existing selection boundary filters every candidate before inference.

`dispatch_one` calls the guarded executor at most once. It observes and returns without a retry or another decision. The outer transport loop requires a new request ID before each action. Stale or ambiguous targets, uncertain execution, observed errors, and unchanged visible state stop the run. Typed airport text does not establish selection. The existing independent selection assessment remains unchanged.

The parent retains the exclusive lock, memory limit, cancellation, one-use marker, and shared 90-second deadline. Startup, model loading, coordinator waits, and actions consume the same deadline. One browser and model persist. No model or browser ran during preparation. No new tests were added.

Root launch command after the frozen handoff:

```sh
ZB_RECORD_PATH=artifacts/replay/flights-single-action-once.jsonl uv run --offline --frozen --extra local python artifacts/flights-single-action-once/launch.py > artifacts/flights-single-action-once/console.log 2>&1
```

The private folder exposes `ready.json` with a random request ID, sequence, observation, and remaining budgets. Root writes `action-N.json` atomically. Exact requests contain `request_id`, `fingerprint`, `mode="exact"`, `target={id,node,kind,label}`, and `value`. Selection requests contain `request_id`, `fingerprint`, `mode="choose"`, `instruction`, and a `permitted` list of those target objects. The worker writes `result-N.json` after one action. Errors produce `stopped.json`. A fresh `ready.json` permits the next request only after the previous result.

GitNexus query, context, and impact calls examined the reused executor. The index refresh succeeded, but MCP symbol responses retained a stale warning. Truncated flows also limit graph coverage. Existing execution code remains unchanged. Source inspection covers the new request boundary. Live outcome and timing remain pending.

Required lint and 184 existing tests passed in 4.57 seconds. Change detection reported low impact but did not map the new unindexed worker. No passing graph result proves that new path. Static inspection found one executor call in `dispatch_one`, no recursive dispatch, and no full-goal Agent command.


### Single-action demonstration result

[Saved evidence](../results/flights-single-action-once.json) records one failed attempt on `3eeb8ed94a4ae4090aae258b7eb6bcdac5154a9f`. Root supplied an exact fill request for the unique observed destination field. The executor entered `JFK` and returned a fresh matching airport suggestion. Root then supplied a separate exact click request for that unique observed option. Both requests used deterministic execution because their targets were already known.

The second request stopped before execution with `StalePage: The request observation is stale`. Its fingerprint matched the supplied observation, but the current browser freshness check failed. No later observation identifies the exact page change. This was not a model decision failure, missing control, incorrect field value, uncertain execution, or false completion. No retry occurred.

Independent assessment found a suggestion but no completed option click or selected destination field. The first action returned its failed selection assessment. The second request stopped before another outcome assessment. The parent returned exit code 1 and completed browser cleanup. The single-action control boundary is implemented, but the end-to-end destination task failed. Qwen selection through this path remains untested.

Total startup-through-cleanup time was 22,541.15 ms. Browser startup took 326.03 ms. Worker plus process cleanup took 21,835.08 ms, and browser cleanup took 363.53 ms. Two coordinator requests caused one executed fill. There were zero local inference calls and one model load of 1,626.82 ms. Peak sampled worker memory was 2,594,146,752 bytes, excluding browser and parent. The same browser target and worker PID persisted between requests. All twenty-one runtime source hashes remained unchanged.

The elapsed time includes startup, model loading, coordinator waits, and cleanup. Separate coordinator token accounting is unavailable in the mixed engineering chat. The replay path was configured, but no model call produced a decision record. Private action requests, observations, events, and failed-run evidence remain preserved. No new responsiveness observation was requested. The earlier freeze remains unexplained.

No further implementation change or trial followed. Earlier evidence remains unchanged. Runtime is idle.

Delivery checks passed: lint and all 184 existing tests in 4.52 seconds. Public evidence passed the private-path and credential scan.


### Minimal target freshness candidate

Thomas authorized the minimal freshness fix and exactly one new JFK-only attempt. Root remains the sole launcher. Requests still require the current random request ID and the fingerprint of the issued observation. Exact targets resolve only within that observation. No indexed target is rebound to a later page.

Exact clicks and selects no longer receive an additional whole-page freshness veto. `Browser.act` still enforces the original page key and target guard. The unchanged executor checks visibility, occlusion, disabled state, and field boundaries. Other requests retain their whole-page freshness check.

Only `PreInputStale` enters the new return path. Explicit pre-input freshness rejection raises that type. The narrow catch around `Browser.act` converts its pre-input `StalePage`. The unchanged executor uses `RuntimeError` for uncertain select execution. Observation after completed input is outside that catch. An observation failure after input cannot cause continuation.

A conclusive rejection consumes one request slot, returns `stale_not_executed` with fresh observation, and waits for a new request ID. The original browser, loaded model, deadline, and request budget remain. No action is replayed automatically. Errors and unknown execution still stop.

Root launches once after the frozen handoff:

```sh
ZB_RECORD_PATH=artifacts/replay/flights-target-freshness-once.jsonl uv run --offline --frozen --extra local python artifacts/flights-target-freshness-once/launch.py > artifacts/flights-target-freshness-once/console.log 2>&1
```

The request format is unchanged. After `result-N.json` reports `stale_not_executed`, root must read the new `ready.json` before issuing another request. The new sequence and request ID prevent automatic reuse. Previous attempt folders and published results remain unchanged. No live attempt ran during preparation.

GitNexus refreshed the index and examined the changed symbols. Direct impact was low. Cached MCP responses retained stale warnings, and truncated graph flows limit coverage. Source inspection establishes the narrow catch boundary. No new tests were added.

Required lint and all 184 existing tests passed in 4.67 seconds. Change detection reported medium aggregate impact across four flows. No shared executor implementation changed.


### Target freshness attempt result

[Saved evidence](../results/flights-target-freshness-once.json) records one attempt on `919395662dbc0bfe8ad77b5e644fd40330d5cc89`. Independent coordinator assessment passed JFK destination selection. The automatic assessor returned false, and the parent ended with exit 130 after coordinator cancellation. These are separate outcomes.

Request 1 filled the observed destination with JFK. Request 2 attempted the observed matching option, but the target freshness guard rejected it before input. The worker returned `stale_not_executed` with a fresh observation. Root issued request 3 with the new request ID. That request clicked the matching JFK airport option. The worker did not replay an action automatically.

The saved option guard stayed identical across the stale return. The page key changed destination node 16 from `JFK` to an empty value while the active popup field retained JFK. This transition is consistent with the pre-input freshness rejection. No uncertain input occurred. The same browser and loaded model persisted under the original deadline and request budget.

After request 3, the fresh observation showed original destination node 16 with label `Where to? New York JFK`, value `New York`, and `expanded=false`. The executed option identified `John F. Kennedy International Airport (JFK)`. Together these records support completed airport selection. No other field change, search submission, booking, payment, or login occurred.

The unchanged automatic assessor required the earlier exact field label and failed to resolve the renamed destination. It recognized the matching option click but returned false for field and dialog requirements. Root saved a separate independent verdict, then cancelled only the parent through its existing cancellation handler. No fourth action request was sent. Worker and browser cleanup completed. The raw automatic verdict and cancelled terminal status remain unchanged.

Independent assessment occurred 50,895.54 ms after dispatch. The worker stopped at 51,113.55 ms. Browser cleanup took 380.83 ms, and total elapsed time was 51,494.38 ms. Three coordinator requests produced two deterministic actions and one pre-input stale return. The worker loaded the model once in 2,752.01 ms but made zero inference calls. Peak sampled worker memory was 2,616,019,344 bytes, excluding browser and parent.

All twenty-one runtime source hashes remained unchanged. Private requests, observations, verdict, and raw evidence remain preserved with public hashes. The configured replay path produced no model records because no inference occurred. Coordinator tokens are not separately attributable within the engineering chat. Elapsed time includes coordinator waits, assessment, cancellation, and cleanup. No new user observation was requested.

This attempt demonstrates one safe stale-return continuation and independently evidenced JFK selection. It does not prove automatic assessment, Qwen value, general reliability, or speed superiority. Dates and the full itinerary remain untested. No code change or further trial followed. Runtime is idle.

Preservation checks passed: lint and 184 existing tests in 4.49 seconds. Public evidence passed the private-path and credential scan.


### Full round-trip development

Thomas authorized iterative fixes and reruns until matching SFO–JFK round-trip results appear for November 12–16, 2026, one adult, economy. Root remains sole launcher and controls each action. Task 16 prepares code and frozen launchers. Each attempt preserves a fresh evidence directory and exclusive marker. Runtime code remains frozen during attempts. Comparisons follow full success and require the same fixed task.

The existing single-action worker now accepts a `round_trip` task. Each request includes one purpose: `origin`, `destination`, `departure`, `return`, `trip_type`, `passengers`, `cabin`, or `search`. Codex supplies the exact observed target for that purpose. The executor permits observed form-control roles and rejects links. Existing forbidden-action, target, ambiguity, freshness, and no-replay safeguards remain. Search requires an observed search button. No policy action sequence or field answer was added.

The provider assessment reads controls, encoded date evidence, passenger observations, and actual flight options. Every requested condition has a separate result. Unknown output fails closed. Selection assessment now accepts a changed airport label only with the original field node, document identity, and matching airport token. Previous raw assessments remain unchanged.

Development attempts share a 300-second deadline and sixty request slots, including coordinator waits and model startup. The first prepared folder is `artifacts/flights-round-trip-01`. Exact and local selection requests retain their existing schemas plus `purpose`. The worker returns each fresh result before another request. No new unit tests, indexing, or broad review occurred. Lint and all 184 existing tests passed in 4.30 seconds. No browser or inference ran during preparation.

Root launch command after source freeze:

```sh
ZB_RECORD_PATH=artifacts/replay/flights-round-trip-01.jsonl uv run --offline --frozen --extra local python artifacts/flights-round-trip-01/launch.py > artifacts/flights-round-trip-01/console.log 2>&1
```


Full-task development attempt 01 stopped after request 15 executed calendar Done. Its immediate observation remained unchanged. Raw evidence remains in `artifacts/flights-round-trip-01`. The next candidate adds coordinator-requested read-only observation, with no automatic repeated mutation. An unchanged result requires observation before further input. Three consecutive unchanged read-only observations stop under the existing shared limits. The independent assessor accepts the observed `Economy (include Basic)` variant only for the Economy requirement. Attempt 02 uses a fresh folder and marker. Raw prior assessments remain unchanged. Public results will be delivered together at the next meaningful milestone.


### Full round-trip development outcome

[Development evidence](../results/flights-round-trip-development.json) preserves both fixed-task attempts. Attempt 01 used `1b65d584bfbbb39398be6ccf3e9ece6876e46afe` and failed after an executed calendar Done action showed no immediate change. It took 92,157.00 ms, with fifteen requests, ten executed actions, five pre-input stale returns, and one local call. The call used 239 prompt tokens. Its raw failure and source hashes remain unchanged.

Attempt 02 used `c88b4d5561ab9e2330c8ac96a4261171fa783df7` and passed all nine independent outcome checks at result 17. Evidence shows SFO–JFK, round trip, November 12–16, 2026, one adult, economy, and actual flight options. The page reported 27 results. Three options were directly visible. No flight was selected. The parent exited 0 and completed cleanup.

Total startup-through-cleanup time was 54,759.10 ms. Browser startup took 323.66 ms, worker plus process cleanup took 54,039.65 ms, and browser cleanup took 374.06 ms. Seventeen coordinator requests produced eleven executed actions and two explicit read-only observations. Four pre-input stale returns required new coordinator requests. Ten actions used deterministic execution. Qwen selected one airport suggestion from two permitted observed choices.

The one local call took 471 ms, with a 472 ms decision record and 230 prompt tokens. Menu scoring generated no output tokens. One model load took 1,666.83 ms. Peak sampled worker memory was 3,167,439,632 bytes, excluding browser and parent. Coordinator token usage cannot be separated from the engineering chat. All twenty-one runtime source hashes remained unchanged during each attempt.

Both attempts retain durable events, requests, results, replay records, and failed-run evidence. The runtime change addressed delayed observation and an observed economy-label variant. The two different code versions prevent a controlled speed comparison. The successful outcome proves one full-task completion with a coordinator, not general local-agent reliability or savings.

The next comparison uses the same full task and frozen successful runtime. Root launches native Desktop, then system, then JEV sequentially. Task 16 prepares a fresh system folder only. No comparison ran during this preservation step.

Preservation checks passed: lint and all 184 existing tests in 4.52 seconds. Public evidence passed the private-path and credential scan. Earlier public results and private run evidence remain unchanged.


### Sequential comparison and separate recovery

[Sanitized evidence](../results/flights-sequential-comparison.json) preserves each attempt. Runtime sources stayed unchanged. The full task remained SFO–JFK, November 12–16, 2026, round trip, one adult, economy, with a stop before flight selection.

| Attempt | Outcome | Recorded time and boundary |
| --- | --- | --- |
| Native Codex Desktop | PASS | 58.68 seconds from dispatch to original final verdict, excluding cleanup |
| Codex + custom browser baseline | PASS, zero Qwen calls | 62.06 seconds to successful result, 62.73 seconds through cleanup |
| Qwen comparison 01 | FAIL | Timing excluded because of a coordinator compaction pause |
| Qwen comparison 02 | FAIL, website error | 72.45 seconds to the failed observation, 73.10 seconds through cleanup |
| Qwen development recovery 03 | PASS, separate recovery | 83.04 seconds to successful result, 83.67 seconds through cleanup |
| Pinned upstream JEV | FAIL, provider blocked | 2.11 seconds to failure verdict, 2.61 seconds through cleanup |

Native used `gpt-6-astra` with high reasoning in a fresh task. Exact original-session usage was 1,199,260 input tokens, including 1,118,080 cached input, and 1,046 output tokens. Total usage was 1,200,306 tokens. Its 107 reasoning tokens are included in output. Totals match seventeen per-response usage records. Cleanup usage is excluded. The other coordinator runs share a mixed engineering chat, so their exact coordinator usage is unavailable. No coordinator-token or billing comparison follows.

The zero-Qwen baseline used eleven deterministic inputs and made no local model call. It proves the custom browser path, not delegation. Qwen comparison 01 made ten calls with 6,021 prompt tokens and 9,504 ms of model-call time. Its first choice opened dates despite an origin-selector instruction. At request 19, the coordinator supplied non-search candidates under the search purpose. The guard rejected that request before inference or input. Its largest coordinator wait was 88,477.06 ms during the reported compaction pause.

Qwen comparison 02 made ten calls with 7,164 prompt tokens and 11,273 ms of model-call time. Twenty-one requests produced twelve inputs, six read-only observations, and three pre-input stale returns. All itinerary settings passed. Search executed once, but the website reported “No results returned. Oops, something went wrong.” The underlying website error remains unknown. Its journal failure event, returned observation, worker stop, and cleanup retain separate timing boundaries.

Development recovery 03 used a fresh browser and the same runtime, with explicit observations before dependent actions. It passed all nine requirements and showed 27 reported results with three directly visible options. Twenty-one requests produced twelve inputs and nine read-only observations, with no stale returns. Ten inputs used local choices. Exact entry and Search supplied the other two. Ten calls used 7,164 prompt tokens and 11,169 ms of model-call time. Menu scoring generated no output tokens. One load took 1,682.27 ms. Coordinator waits totaled 66,542.61 ms. Peak worker memory was 3,768,732,480 bytes, excluding browser and parent. This recovery does not replace either failed comparison or establish a root-cause fix.

JEV used pinned upstream `1231850a0bf1a0c0341fe408ef1668dbbfdfac46`, requested `jev-latest`, and configured Mercury 2.5 for text. Typesafe returned HTTP 200 with 4,268 input and 321 output tokens. OpenRouter returned HTTP 402 with usage unavailable. No browser input occurred. Later read-only diagnostics recognized the key and showed zero account credits. A key usage limit does not supply credits. That diagnostic changed no setting. A later funded attempt appears below. Account totals are not benchmark token usage.

Native and custom-browser profile state, tool interfaces, and coordinator context differ. These sequential attempts do not establish general speed superiority or savings. All raw sessions, images, credentials, and private paths remain outside the repository. Public evidence contains only necessary measurements, sanitized observations, and source/evidence hashes. No runtime implementation changed during preservation.


### Direct action adapter preparation

`scripts/worker_call.py` sends one issued request and returns its result with the next observation. It preserves request identity and refuses duplicate submission. A timeout reports unresolved execution and forbids replay. The existing worker retains all browser and inference safeguards. Root owns the launch in `artifacts/flights-direct-action-01/launch.py`. No runtime experiment started during implementation. Final existing tests passed: 184 in 4.27 seconds. Full lint passed after the authorized unused-import cleanup. The helper performs at most one additional read-only observation when the worker requires it. It preserves the mutation result separately. Adapter SHA256: `c78eec9b4f5b8f1ce4fefc46be5b4806d2d47a25c491eea999ae4f14f9c2db4f`. GitNexus queries used an older index. No index refresh ran during the short preparation.


### Isolated usage measurements and direct-action result

[The same result file](../results/flights-sequential-comparison.json) preserves all later attempts with independent usage sums and evidence hashes.

| Attempt | Outcome | Main duration | Coordinator total tokens | Recorded API-equivalent estimate |
| --- | --- | --- | --- | --- |
| Fresh native Desktop | PASS | 46.22 seconds | 1,287,557 | $1.871178 |
| Qwen startup failure | FAIL before browser/model startup | 16.10 seconds | 122,633 | $0.189314 |
| Authorized Qwen recovery | PASS | 140.80 seconds | 1,759,285 | $2.520906 |
| Direct-action Qwen | PASS | 123.14 seconds | 1,498,156 | $2.092752 |

Main durations run from dispatch through the final task event. The Qwen durations include automatic cleanup. Native cleanup follows its final verdict. Recovery retained earlier failed-startup and access-probe context. The direct-action attempt used a fresh repository chat and a 180-second worker limit. The previous Qwen limit was 300 seconds. Standard API-equivalent estimates are not subscription charges. Service tier and local compute cost are unavailable. Cached input is included in totals. Reasoning tokens are a subset of output.

The direct-action attempt passed all nine independent requirements and showed actual JetBlue, Delta, and Alaska options. Seven local calls used 3,218 prompt tokens and 5,309 ms. One model load took 1,713.48 ms. Eleven inputs came from eighteen requests. Four stale requests stopped before input. The first rejection occurred at request 3. The coordinator issued new requests without replaying uncertain execution. Peak sampled worker memory was 3,450,768,192 bytes, excluding browser and parent. Coordinator waiting totaled 95,080.14 ms. Total worker-launch-through-cleanup time was 107,141.88 ms. Source hashes stayed unchanged.

The adapter uses the existing file protocol through one shell call. It returns the original mutation result and performs at most one required read-only observation. It does not provide a native MCP endpoint. The earlier 140.80-second run used seven local calls with 4,730 prompt tokens and 7,591 ms. Different context and observations prevent attribution of the timing difference to the adapter alone.

After funding, JEV attempt 02 failed in 7,144.63 ms to its independent verdict and 7,711.14 ms through cleanup. Its first observed error was incorrect text at executed step 4: SFO entered the Departure date field. It later clicked Open Return three times without a page change and stopped. Eight actions executed. TypeSafe made twelve calls with 65,480 input and 4,294 output tokens. OpenRouter made three calls with 1,565 input and 318 output tokens. Only OpenRouter reported cost: $0.0001103. Total JEV cost is unavailable. Failed-run time is not comparable with completed search time.

The adapter passed lint and all 184 existing tests before measurement. No new tests or review cycle ran. GitNexus discovery, query, context, and change detection used the existing stale index. The graph omitted the new untracked helper and does not establish complete impact coverage. Source inspection and existing tests supplied the delivery checks. No index refresh interrupted measurement. The earlier freeze remains unexplained. Existing responsiveness observations remain applicable.

Final delivery checks passed: lint and all 184 existing tests in 4.55 seconds. Added evidence passed JSON, private-path, and credential-pattern checks. Runtime sources stayed frozen through measurement. No new responsiveness observation is needed.

### Experiment loop measurement

October 29, 2026. VM worker `bc-65a045d8-dfac-5b19-b5ec-702051a6d2cf` owns the sealed judge. Desktop worker `bc-7af786e3-ca6a-57c3-8e30-00259f3291e0` owns browser, offline model, Codex CLI, and Claude CLI execution and writes `results/`. No new measured batch has landed. This section does not claim a speedup.

The comparison arms are `browser-use`, `grok-4.7`, `grok-4.7+zero-browser`, and hypothesis arm `local-coordinator`. The first fixed goal remains `local_search`. Live flight goals stay closed until three consecutive independent local passes. The judge is `scripts/experiment_scoreboard.py`. Sakana AI-Scientist v3 task text, rubrics, and the first idea are in `experiments/local-coordinator/`. `evaluate.py` only scores recorded runs. Prior SFO–JFK numbers in `results/flights-sequential-comparison.json` used Codex and hosted JEV, so they are not this comparison.

On this Linux VM, ruff passed and the 10 new scoreboard tests passed. Thirteen existing tests failed while importing macOS `libproc` or `mlx`. Those files were not edited. The required suite still belongs on the desktop Mac.

`scripts/experiment_record.py` copies `verification.checks` from a finished non-pilot milestone directory into `results/experiment-loop/`. `outcome_verified` and DONE do not decide the record. The recorder does not start a browser or a model. No `results/experiment-loop/` batch was present when this landed.

`scripts/experiment_track.py` logs that directory to a local MLflow sqlite store under ignored `artifacts/mlflow`. `scripts/experiment_propose.py` writes one Sakana AI-Scientist v3 idea whose lever is the scoreboard recommendation. Neither command writes a file when the directory is missing or empty, and an unmeasured score is null rather than zero.

`local_search --ready --headless` no longer requires a private Linux patch. The loader accepts `mx.cuda.is_available()` on non-Apple hosts and still requires Metal on arm64 Darwin. Worker memory uses `/proc` on Linux and `libproc` on macOS. Common Linux Chrome paths are candidates. This change does not record a run.

### Scored local_search batch

The desktop records were rescored with `scripts/experiment_scoreboard.py`. The output matches `results/experiment-loop-summary.json`. `scripts/experiment_propose.py` wrote `experiments/local-coordinator/proposed-idea.json`. That idea has no measured latency ratio.

| Arm | Result | Evidence |
| --- | --- | --- |
| local-coordinator measurement | Fail, wrong_decision step 1, 41181 ms, 7 steps, 0 hosted calls | `results/experiment-loop/local-coordinator/local_search/local_search-1793259713570692462.json` |
| local-coordinator measurement | Fail, wrong_decision step 1, 6489 ms, 7 steps, 0 hosted calls | `results/experiment-loop/local-coordinator/local_search/local_search-1793260155458458566.json` |
| local-coordinator prompt | Fail, wrong_decision step 1, 6515 ms, 7 steps, 0 hosted calls | `results/experiment-loop/local-coordinator/local_search/local_search-1793260295460311524.json` |
| browser-use | Blocked, no credential | `results/experiment-loop/browser-use/local_search/blocked.json` |
| grok-4.7 | Blocked, no login | `results/experiment-loop/grok-4.7/local_search/blocked.json` |
| grok-4.7+zero-browser | Blocked, no login | `results/experiment-loop/grok-4.7+zero-browser/local_search/blocked.json` |

Independent checks failed on every requested field. `no_flight_selected` was true. DONE was false. Success rate is 0/3. Passing-run latency medians are null, and every baseline ratio is null. The next lever is stop. Do not run another local_search prompt change. The prompt evidence also records parent stop `Cannot read the worker memory footprint for 1491437`. That file stays as recorded.

The stop came from a `/proc` read that missed `VmRSS` while the worker was still starting or exiting. The supervisor slept and then raised without reading again. It now retries a live worker and treats an exited worker as finished. The 3 GiB floor is unchanged. local_search stays stopped.
