# Project status

> **Current coordination: October 11, 2026, authorized by Thomas in the context chat.**
> This agreement replaces the earlier single-agent banner and conflicting historical file reservations.
> Codex task 16 owns runtime integration and the only benchmark slot. Claude provides observation support after an explicit handoff.
> No two agents run local inference or browser experiments at the same time.
>
> **Current run state: IDLE.** Codex README recording coordinator completed the user-requested flight recording. All nine round-trip checks passed. The worker and isolated browser closed; the run lock is released. [Recording evidence](../results/readme-flight-screen-recording.json).
> Task 16 completed the callable adapter and preserved every comparison. Final lint and all 184 existing tests passed. Publication follows the repository procedure.
> Latest measured results: native PASS in 46.22 seconds, prior Qwen PASS in 140.80 seconds, direct-action Qwen PASS in 123.14 seconds. Context and timing boundaries differ. Funded JEV failed after 7.14 seconds.
> [Evidence](../results/flights-sequential-comparison.json) contains usage, memory, source hashes, and failed-run records. No general reliability or savings claim follows.
>
> **Current scope:** task 16, with supporting notes in task 13. Tasks 18–22 remain cut from the active plan.
> This context update does not reopen task 19. Do not create new task numbers.
>
> **Revised scope, authorized by Thomas:** prove a bounded local browser worker before coordinator or planning work.
> The first shortened session is delivered. Thomas renewed work through the coordination chat and explicitly approved sequential isolated benchmark sessions at about 14:31 PT. No new numeric budget was specified. Complete required checks before delivery.
> Accept one outcome, supplied values, allowed actions, stopping conditions, a deadline, and an action budget.
> Return success/failure/uncertainty with observed evidence, actions, unresolved execution, timing, calls, and memory.
> Test supplied field entry, dropdown selection, and autocomplete with reordered, distracting, ambiguous, and missing controls.
> Pause caching, screenshots, desktop control, and long-task planning. Shared browser/model lifetime now supports bounded subtasks. The latest workflow attempt passed both subtasks and the independent route/answer assessment. Its recovery path did not run.
> No new task numbers or parallel runtime agents. Sequential Codex sessions are authorized only as benchmark subjects, with no implementation work. Read-only accounting and outcome audits passed for the recorded failed result. A controlled shared-interface comparison is recorded. Native desktop CUA speed and dollar savings remain unproven.
>
> **Test scope:** preserve existing tests and required delivery checks. Defer broad unit-test expansion until the flight demonstration works.
> Add only small, deterministic tests for critical safeguards or repeatable bugs.

Reconciled October 11, 2026. This file owns current state and reservations.
[README.md](README.md) gives the engineering sequence. Task files preserve implementation history.

## Where we are

The local CLI and Codex MCP connection work on a simple navigation goal.
General multi-step reliability, useful time savings, and a controlled native Codex speed comparison remain unproven.
The active milestone now tests local task completion. The user reported a visible page, normal responsiveness, and clean closure during the pilot.
The final cancellation pilot stopped during inference. The user reported normal responsiveness and clean closure. The earlier freeze remains unexplained.

## Open follow-up

- **16, Improve zero-browser benchmarking:** the callable adapter completed one full flight search with seven local choices. Native Desktop remains faster in the recorded attempts. Preserve the earlier failures and successful recoveries. General reliability, controlled savings, and a native MCP transport remain unproven. No runtime work remains active.

## Completed context work

- **19:** task state and the engineering sequence are reconciled. The isolated documentation candidate passed lint and all 118 tests. Coordination commit `86f94bc` published that context work.

## Current ownership

| Owner | Reserved files and actions |
| --- | --- |
| Codex: optional observation compactor support | Complete in detached candidate `1f1ccd4` from `3fd3936`, independently reviewed. New `observation_compactor.py`, its test, assessment script, and sanitized results only. Integration remains pending. No runtime integration or browser/model runs. Required checks use an agreed idle slot |
| Codex: **Improve zero-browser benchmarking**, task 16 | `jev_ultrafast/agent.py`, `local_policy.py`, `local_model.py`, `questions.py`, `snapshot.js`, `model.py`, `scripts/replay.py`, milestone scripts and fixtures, related tests, milestone evidence, root `README.md`, and task 16 |
| Claude: **Hackathon project tasks**, task 13 support | Handed `snapshot.js`, `model.py`, replay, and the recording hook to Codex at `9f5b613`. Read-only review and task 13 notes only. No runtime edits or browser/model runs without a new handoff |
| Codex: **Assess zero-browser’s thesis**, context coordinator | `contexts/AGENT-RULES.md`, `contexts/STATUS.md`, and `contexts/README.md` during this update. No inference or browser experiments |

After this update, task 16 becomes the sole writer of `STATUS.md` for ownership and run-state changes.
Other agents request a change through task 16 instead of editing the shared status file concurrently.
A runtime handoff must name the files, recipient, source commit, and run state.
Existing task numbers identify work. They do not override this ownership table.

## Deferred and historical work

- **18–22:** no active work. The existing MCP connection and context history remain available.
- **13:** supports task 16 after an explicit handoff. Its old broad model reservation no longer grants concurrent edits.
- **12:** its separate benchmark plan is superseded. Do not start a second runner.
- **03, 05, 06, 07:** superseded by task 16. **04:** absorbed into task 13.
- **08, 09, 10:** deferred. Evidence and required README corrections remain part of task 16 delivery.
- **00, 01, 02, 11:** implemented. **17:** instruction changes are on origin/main.

## Evidence

| Work | Evidence and limit |
| --- | --- |
| Local model and adapters | [Shared model](../results/shared-local-model-verification.json), [installation](../results/install-cli-verification.json). Simple completion does not establish general reliability |
| Runtime safety | [Guard tests](../results/cli-runtime-safety.json). The freeze cause remains unknown |
| Milestone preparation | [Preparation](../results/milestone-preparation.json). Scripted controls and outcome tests, not model performance |
| Controlled coordinator comparison | [Five-pair evidence](../results/paired-browser-five-pairs-v3.json), [summary](../results/paired-browser-comparison.json). One field task, shared custom executor; pair 4 latency flagged. No native-CUA or billing claim |
| Bounded worker | [Repeat summary](../results/bounded-worker-summary.json), [live assessment](../results/bounded-worker-live-assessment.json). Fixed field contracts only; no general reliability or savings claim |
| Live Flights attempt | [Independent failure assessment](../results/flights-demo-once.json). General local runner, no matching airport selection or dates, decision budget stop |
| JFK-only handoff attempt | [Failed selection](../results/flights-handoff-once.json). One actual correction retained the browser and model. The next decision violated the boundary and stopped before execution |
| Single-action attempt | [Failed destination selection](../results/flights-single-action-once.json). Exact fill produced the JFK suggestion. The second exact request stopped before execution because its observation was stale. No Qwen inference occurred |
| Target freshness attempt | [Separate verdicts](../results/flights-target-freshness-once.json). Independent JFK selection passed after one pre-input stale return. Automatic assessment failed. Coordinator cancellation and exit 130 remain preserved |
| Full round-trip development | [Both attempts](../results/flights-round-trip-development.json). Attempt 02 passed all nine conditions. Attempt 01 stopped after an unchanged immediate calendar observation. No comparative savings claim |
| Final sequential comparison and recovery | [All separate attempts](../results/flights-sequential-comparison.json). Native and zero-Qwen baseline passed. Delegated comparisons failed. Separate Qwen recovery passed. JEV is blocked on account funding |
| Current local experiments | [Measured runs](../results/milestone-local-runs.json). Failed tasks, interrupted records, source versions, and cancellation observations |
| MCP connection | [Codex run](../results/codex-mcp.json). Simple navigation only |
| Smaller models | [4B](../results/replay/quality-4b-plain.json), [1.7B](../results/replay/quality-1.7B-plain.json), [0.6B](../results/replay/quality-0.6B-plain.json). Synthetic cases only |
| Scoring and recorder history | [Decision comparison](../results/decision-comparison.json), [filter failure](../results/decision-quality-filter-rerun.json), [recordings](../results/demo-capture-summary.json) |

## Known limits

DONE can precede completion. The loop stops unchanged actions but does not detect all repeated state cycles.
The MCP interface tests text and URL fragments rather than every task requirement.
Each MCP goal starts a fresh browser and model worker. Login state is not preserved.
The earlier native Codex CLI attempt exposed no browser tools. A later desktop baseline passed in 33.05 seconds. Its browser state, context, and tools differ from the system run, so general speed superiority remains unproven.
The crowded local task still fails and exceeds its speed target. Unfamiliar live controls and other machines remain untested. Scores are uncalibrated.
The inherited demo retains hosted paths. The local worker must not use them.

## Coordination and publication

Follow the [exclusive run and handoff rules](AGENT-RULES.md#exclusive-runtime-and-benchmark-access).
The run slot covers CLI goals, MCP goals, milestone runs, replay, cache probes, and browser-only experiments.
Keep the existing single-run lock. A busy lock means wait. It does not grant permission to use another lock directory.
The ownership agreement covers entry points that do not acquire the lock themselves.

During a measured run, freeze the runtime files, prompts, fixtures, and environment configuration.
Record the owner, command, source commit, dirty-file hashes, evidence path, and start/end state in task 16.
Keep raw records in ignored `artifacts/`. Publish only sanitized evidence in `results/`.
Preserve the recorder, dispatch contract, bounded stops, and the rule against mutation retries.

Stage only owned files. Do not include another agent's work in a commit.
Before each commit, run the required lint and test commands. Before each push, pull with rebase on main.
If another agent has uncommitted edits, preserve them. Use an isolated publication checkout instead of stashing their work.
Do not alter the shared Git index while another owner prepares a commit.

## Log

- October 11, 14:45 PT: task 16 finished ten shared-interface trials, all outcomes passed. Four pairs support the limited timing summary; pair 4 retains its indexing caveat. Exact usage and independent audits are in results/paired-browser-comparison.json. Runtime is idle.

- October 11, 14:02 PT: task 16 integrated the observation handoff and corrected field descriptions. Both fixed local reruns failed. Evidence: `results/milestone-followup.json`. Slot idle.

- October 11, 13:59 PT: task 16 accepted the handoff in `5799c81`. No inference is running. Publish the measured follow-up before observation integration.

- October 11: Thomas requested coordination between Codex and Claude. Codex acknowledged the hold and reported no inference running. Claude acknowledged the hold and handed its observer and replay files to Codex. The context update assigns one runtime owner.

- October 11, task 16: implemented the requested joint menu, scoped cache reuse, and DONE confirmation. The local gate failed. Evidence: `results/milestone-followup.json` and `results/milestone-cache-parity.json`.

- October 11: the user requested publication and explicit limits on test expansion. Preserve existing tests and prioritize the flight demonstration.

- 2026-10-11. Task 16 recorded failed local runs and stopped inference on cancellation. The milestone remains open. Evidence: `results/milestone-local-runs.json`.

- October 11, task 19: reconciled stale task state, preserved owner reservations, and defined stages 16 → 20 → 21 → 22.
- Task 16: the user supplied the earlier pilot observations. The final cancellation observation passed. Its owner maintains the sanitized results in `results/milestone-local-runs.json`.
- Task 18: the MCP retest stopped at the run lock. The native CLI supplied no browser tool. Neither attempt establishes a speed result.

Earlier implementation details and evidence remain in the numbered task files and Git history.

- October 11: task 16 recorded the failed JFK-only attempt. One correction retained the browser and model but did not recover. Runtime is idle. No retry is authorized.

- October 11: task 16 prepared the separate single-action path. Lint and 184 existing tests passed. Root owns the one pending launch.

- October 11: task 16 recorded the failed single-action demonstration. The stale second request stopped before execution. Runtime is idle, with no retry authorized.

- October 11: task 16 prepared the minimal target freshness fix. Lint and 184 existing tests passed. Root owns the one pending attempt.

- October 11: task 16 preserved independent JFK selection, the automatic assessment failure, and coordinator cancellation. One safe stale continuation occurred. Runtime is idle.

- October 11: task 16 preserved full-task development attempts 01 and 02. Attempt 02 passed all nine conditions with clean exit 0. Runtime is frozen for sequential comparisons under root ownership.

- October 11: task 16 completed comparison preservation and separate Qwen recovery evidence. JEV remains blocked on account funding. All runtimes are idle. No further live tests ran.

- October 11, 2026: Task 16 preserved isolated usage comparisons and the funded JEV failure. The direct-action helper passed one full flight search. Runtime slot idle.

- October 30, 2026: Thomas narrowed repository cleanup to the README. Codex completed badges, evidence-linked examples, and a 16-second animated walkthrough of the saved Wikipedia run. The animation is labeled as evidence playback. Runtime code, existing local commits, and unfinished edits remain outside this change. No browser or model experiment ran.

- October 30, 2026: Thomas requested replacing the README animation with an actual screen recording. Codex README recording coordinator reserves the task 16 runtime slot for one coordinator-assisted local-Qwen flight search.

- October 30, 2026: The actual local-Qwen flight recording passed all nine round-trip checks in one attempt. Replaced the README animation with 4× Chrome footage. The run used 9 local model calls and 11 executed actions. Runtime is idle; evidence is in `results/readme-flight-screen-recording.json`.
