# Project status

> **Current coordination: October 11, 2026, authorized by Thomas in the context chat.**
> This agreement replaces the earlier single-agent banner and conflicting historical file reservations.
> Codex task 16 owns runtime integration and the only benchmark slot. Claude provides observation support after an explicit handoff.
> No two agents run local inference or browser experiments at the same time.
>
> **Current run state: IDLE, reserved for Codex task 16.** Thomas authorized two multi-step reload/persistent pairs, then the native desktop comparison. Native tool discovery passed in a fresh isolated agent. Task 16 is implementing bounded navigation and shared-session measurement. No inference is active.
> The coordinator released the hold after publishing `5799c81`. Task 16 owns the next run.
> The next owner is Codex, **Improve zero-browser benchmarking**. Claude must not start browser runs, replay, cache probes, or model loads.
>
> **Current scope:** task 16, with supporting notes in task 13. Tasks 18–22 remain cut from the active plan.
> This context update does not reopen task 19. Do not create new task numbers.
>
> **Revised scope, authorized by Thomas:** prove a bounded local browser worker before coordinator or planning work.
> The first shortened session is delivered. Thomas renewed work through the coordination chat and explicitly approved sequential isolated benchmark sessions at about 14:31 PT. No new numeric budget was specified. Complete required checks before delivery.
> Accept one outcome, supplied values, allowed actions, stopping conditions, a deadline, and an action budget.
> Return success/failure/uncertainty with observed evidence, actions, unresolved execution, timing, calls, and memory.
> Test supplied field entry, dropdown selection, and autocomplete with reordered, distracting, ambiguous, and missing controls.
> Pause caching, screenshots, desktop control, and long-task planning. The existing Codex chat delegated one live field task; multi-subtask integration remains untested.
> No new task numbers or parallel runtime agents. Sequential Codex sessions are authorized only as benchmark subjects, with no implementation work. The accounting agent is read-only and has finished. A controlled shared-interface comparison is recorded. Native desktop CUA speed and dollar savings remain unproven.
>
> **Test scope:** preserve existing tests and required delivery checks. Defer broad unit-test expansion until the flight demonstration works.
> Add only small, deterministic tests for critical safeguards or repeatable bugs.

Reconciled October 11, 2026. This file owns current state and reservations.
[README.md](README.md) gives the engineering sequence. Task files preserve implementation history.

## Where we are

The local CLI and Codex MCP connection work on a simple navigation goal.
Reliable multi-step completion, useful time savings, and a native Codex speed comparison remain unproven.
The active milestone now tests local task completion. The user reported a visible page, normal responsiveness, and clean closure during the pilot.
The final cancellation pilot stopped during inference. The user reported normal responsiveness and clean closure. The earlier freeze remains unexplained.

## Open follow-up

- **16, Improve zero-browser benchmarking:** bounded-worker proof delivered: three identical suites passed 27/27 requested outcomes and 6/6 safe stops. One live Wikipedia field task passed. Full local flight completion remains unresolved; no live flight run started. The shared-interface field comparison passed all ten original outcomes and both supplemental outcomes. The five-pair comparison set excludes the original pair with indexing overlap. Its median delegated time reduction is 1.90 seconds. Native desktop CUA speed remains unproven. Next: a deterministic-helper baseline and a useful multi-step task.

## Completed context work

- **19:** task state and the engineering sequence are reconciled. The isolated documentation candidate passed lint and all 118 tests. Coordination commit `86f94bc` published that context work.

## Current ownership

| Owner | Reserved files and actions |
| --- | --- |
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
| Current local experiments | [Measured runs](../results/milestone-local-runs.json). Failed tasks, interrupted records, source versions, and cancellation observations |
| MCP connection | [Codex run](../results/codex-mcp.json). Simple navigation only |
| Smaller models | [4B](../results/replay/quality-4b-plain.json), [1.7B](../results/replay/quality-1.7B-plain.json), [0.6B](../results/replay/quality-0.6B-plain.json). Synthetic cases only |
| Scoring and recorder history | [Decision comparison](../results/decision-comparison.json), [filter failure](../results/decision-quality-filter-rerun.json), [recordings](../results/demo-capture-summary.json) |

## Known limits

DONE can precede completion. The loop stops unchanged actions but does not detect all repeated state cycles.
The MCP interface tests text and URL fragments rather than every task requirement.
Each MCP goal starts a fresh browser and model worker. Login state is not preserved.
The native Codex CLI attempt exposed no browser tools. No valid native speed baseline exists.
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
