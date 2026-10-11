# Project status

> **Read this banner first. 13:45 PT, set by Thomas via Claude.**
> One agent works at a time. That agent is the task 16 chat. Everything below the banner is reference.
>
> **Cut as of 13:45.** 18 (MCP), 19 (context roadmap), 20, 21, 22. Do not resume them. Do not create new
> task numbers. New work goes into the Result section of 16 or 13.
>
> **Task 16's next steps, one change per rerun of `scripts/milestone.py --task local_search`:**
> 1. Finish the current crowded-page run. Commit the milestone code and the duplicate-target removal with
>    its evidence. Nothing new starts before that commit is pushed.
> 2. Joint menu. When the operation stage's candidates plus every target for every operation total 26 or
>    fewer, skip the two-stage split and score one flat menu where each candidate is a concrete action,
>    for example `TYPE_TEXT [1] Where from? (empty)`, `SELECT [3] Trip type: Round trip -> One way`,
>    `CLICK [5] Search`, `DONE`. Keep the two-stage path for larger pages. This targets the observed
>    failures (clicks a field instead of typing, premature DONE, reverses a dropdown) and makes small-page
>    decisions one forward pass. Rerun. Keep the failed records.
> 3. Prefix KV cache for the two-stage path. All menus within one decision share the prefix up to the
>    candidate list. Prefill once, score suffixes from `copy.deepcopy` of the cache. Measured on this
>    machine, a 60-token suffix on a cached 1000-token prefix is 117ms versus ~1600ms uncached. Verify
>    identical picks against `scripts/replay.py --variant plain` on the same records before trusting it.
>    Rerun the crowded page. Target under 2s per decision there.
> 4. DONE confirmation. DONE stops the run only when it wins on two consecutive decisions, the second
>    taken after a fresh observation. Generic, no site knowledge. Rerun.
>
> Then three consecutive local_search passes, then the two layout variations, then live Flights.
> Record every rerun in `contexts/16-flight-milestone.md` Result with the first failed step and cause.
> Set `ZB_RECORD_PATH=artifacts/replay/<run>.jsonl` on runs so prompts can be replayed offline.


Reconciled October 11, 2026, at 13:40 PT. This file owns current state and reservations.
[README.md](README.md) gives the engineering sequence. Task files preserve implementation history.

## Where we are

The local CLI and Codex MCP connection work on a simple navigation goal.
Reliable multi-step completion, useful time savings, and a native Codex speed comparison remain unproven.
The active milestone now tests local task completion. The user reported a visible page, normal responsiveness, and clean closure during the pilot.
The final cancellation pilot stopped during inference. The user reported normal responsiveness and clean closure. The earlier freeze remains unexplained.

## In progress

- **16, Improve zero-browser benchmarking:** local completion remains unresolved. Cancellation observations passed. The owner is preparing the measured baseline commit before the next experiment.

## Completed context work

- **19:** task state and the engineering sequence are reconciled. The isolated documentation candidate passed lint and all 118 tests. Publication remains pending.

## Next, in order

| Task | State | Entry requirement |
| --- | --- | --- |
| [20 Multi-step MCP outcomes](20-mcp-task-outcomes.md) | Planned, unassigned | Task 16 demonstrates repeated local completion and the MCP owner hands off files |
| [21 Delegation comparison](21-delegation-comparison.md) | Planned, unassigned | Task 20 passes and a working native browser baseline is available |
| [22 Model reuse](22-model-reuse.md) | Deferred, unassigned | Measurements establish startup overhead and acceptable task reliability |
| [08 Evidence and README](08-hygiene-and-readme.md) | Deferred | Each public claim has a result file |

## Reservations and retired work

- **13:** preserve the existing model owner's reservation and recording hook. Replay work landed. Further latency work needs coordination with task 16.
- **12:** task 16 supersedes its separate benchmark plan. Its earlier file reservation remains until the owner releases it. No second benchmark runner is planned.
- **03, 05, 06, 07:** superseded by task 16. **04:** absorbed into task 13.
- **09:** deferred synthetic filter miss. **10:** deferred scaffolding removal. Neither is on the current completion path.
- **00, 01, 02, 11:** implemented. The installer was not dropped. Multi-step reliability belongs to task 16.
- **17:** instruction changes are committed and present on origin/main. Its old publication note is historical.
- **18:** connection milestone completed. MCP multi-step work is task 20, not a completed result of task 18.

## Evidence

| Work | Evidence and limit |
| --- | --- |
| Local model and adapters | [Shared model](../results/shared-local-model-verification.json), [installation](../results/install-cli-verification.json). Simple completion does not establish general reliability |
| Runtime safety | [Guard tests](../results/cli-runtime-safety.json). The freeze cause remains unknown |
| Milestone preparation | [Preparation](../results/milestone-preparation.json). Scripted controls and outcome tests, not model performance |
| Current local experiments | [Measured runs](../results/milestone-local-runs.json). Failed tasks, interrupted records, source versions, and cancellation observations |
| MCP connection | [Codex run](../results/codex-mcp.json). Simple navigation only |
| Smaller models | [4B](../results/replay/quality-4b-plain.json), [1.7B](../results/replay/quality-1.7B-plain.json), [0.6B](../results/replay/quality-0.6B-plain.json). Synthetic cases only |
| Scoring and recorder history | [Decision comparison](../results/decision-comparison.json), [filter failure](../results/decision-quality-filter-rerun.json), [recordings](../results/demo-capture-summary.json) |

## Known limits

DONE can precede completion. The loop stops unchanged actions but does not detect all repeated state cycles.
The MCP interface tests text and URL fragments rather than every task requirement.
Each MCP goal starts a fresh browser and model worker. Login state is not preserved.
The native Codex CLI attempt exposed no browser tools. No valid native speed baseline exists.
Crowded pages, unfamiliar live controls, and other machines need separate evidence. Scores are uncalibrated.
The inherited demo retains hosted paths. The local worker must not use them.

## Coordination and publication

Task 16 owns the active experiment. Task 13 retains its shared model reservation.
Task 16's recorded exception permits prompt experiments in `local_policy.py`; preserve task 13's recording hook.
Task 18's retest encountered the single-run lock. Schedule inference rather than bypassing the lock.
Keep raw records in ignored `artifacts/`. Publish only sanitized evidence in `results/`.
Do not erase the recorder or decision baseline tools during cleanup.

The final task 18 evidence commit `a232d80` is local. Automatic approval review rejected its push under the prior README publication rule.
This cleanup does not lift that hold or grant authority to publish unrelated changes.
Other chats have unfinished changes in the shared checkout. Preserve them and do not stage them with this cleanup.

## Log

- 2026-10-11. Task 16 recorded failed local runs and stopped inference on cancellation. The milestone remains open. Evidence: `results/milestone-local-runs.json`.

- October 11, task 19: reconciled stale task state, preserved owner reservations, and defined stages 16 → 20 → 21 → 22.
- Task 16: the user supplied the earlier pilot observations. The final cancellation observation passed. Its owner maintains the sanitized results in `results/milestone-local-runs.json`.
- Task 18: the MCP retest stopped at the run lock. The native CLI supplied no browser tool. Neither attempt establishes a speed result.

Earlier implementation details and evidence remain in the numbered task files and Git history.
