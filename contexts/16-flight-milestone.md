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
