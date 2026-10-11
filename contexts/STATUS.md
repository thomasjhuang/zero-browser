# Project status

Updated 2026-10-11 12:44 PT. This is the single shared state file. Edit it on every claim, finish, or block.
Keep it short. Evidence lives in `results/` and is linked, never restated beyond one number.

## Where we are

Jev Ultrafast scaffolding imported. Local Qwen3-4B 4-bit scorer works offline on synthetic decisions.
The new CLI forces local Qwen decisions and field text. It completes a simple local fixture goal.
Multi-step goals remain incomplete. The inherited demo still uses hosted services.
Tasks 01 and 02 must reconcile their work with the CLI adapter before changing shared interfaces.
Plan and ranked tasks are in `README.md` here.

## In progress

- 15-cli-runtime-safety (Codex). Emergency safeguards after the user reported a freeze.

- 12-benchmark-loop (Astra). Owns bench.py, run_cli.py, bench_tasks.json, results/bench/, verify.py.
- 13-latency-and-field-text (Sol). Owns local_policy.py, local_model.py, questions.py, browser timeout.

## Open, in priority order

- iterate on next bench failure (both, after 12 and 13 land)
- 09-fix-filter-miss (P3, slack only)
- 10-trim-jev-scaffolding (P3, slack only)
- 08-hygiene-and-readme (P3, last 20 min)

## Cut 12:50 PT

03, 05, 06, 07 replaced by the live bench loop. 04 absorbed into 13. 11 installer dropped, run_cli.py kept.

## Done

| Work | Outcome | Evidence |
| --- | --- | --- |
| 11 Installer and local CLI | Setup and simple fixture goal passed. Multi-step goals failed | [Evidence](../results/install-cli-verification.json) |
| 00 Shared local model | One cached model supports scoring and generation. Smoke: 12/12 | [Smoke](../results/shared-local-model-smoke.json), [tests and reuse](../results/shared-local-model-verification.json) |
| Local scorer, pinned weights, offline rerun | 12/12 synthetic decisions, 48 forward passes, ~300ms warm | `results/decision-smoke.json`, `results/decision-smoke-rerun.json` |
| Quality cases | 35/36. One candidate order picks the wrong filter, repeats 4/4 in that order | `results/decision-quality.json`, `results/decision-quality-filter-rerun.json` |
| Synthetic comparison vs hosted CLIs | Qwen 47/48, Codex 48/48, Claude 48/48 on 12 cases x 4 orders. No browser execution | `results/decision-comparison.json`, `scripts/decision_baselines.py` |
| Human demo recorder | Two human examples captured. The second saved without errors. Action mapping remains partial | `results/demo-capture-summary.json`, `scripts/record_demo.py` |
| Repo on GitHub | Scaffolding, scorer, fixtures, results, recorder on `main`. PRs #1 to #4 merged | github.com/thomasjhuang/zero-browser |
| Contexts folder committed | Plan, tasks, rules, status shared across agents | this folder |
| 00 shared model | `local_model.get_model()` cached per process | `results/shared-local-model-smoke.json` |
| 01 + 02 local policy | `local_policy.py`, operation then target scoring, local field text, `JEV_LOCAL=1` dispatch | Codex live run 12:3x |
| First live comparison, SFO to BOS | Qwen 6 actions then browser timeout, 4.16s median decision. Jev+local text picked dates, failed destination at 123ms. Both typed "Boston Logan (BOS)" | Codex session, to be reproduced by 12 |

## Blocked

(none)

## Known limits

The CLI can stop at DONE before the entire goal succeeds. Final-page assertions detect this problem.
Destination submission and requested filters failed in local multi-step attempts.
Task 06 remains open. The new simple-goal result does not establish general browser reliability.

Human recordings expose unsupported clicks and manual scrolls. The largest observation contains 74 actions.
Resolve recording coverage and candidate scaling before longer demonstrations or training. Human completion
reports do not establish model performance or a completed purchase. Private recordings remain ignored.

Synthetic decisions do not establish browser reliability. Restricted scores are uncalibrated. The 16GB
memory target is untested. The browser guard check passed only in an isolated headless Chrome profile; the
default profile lacked remote debugging. Jev's per-step timeout can be exceeded by a slow local call.

## Coordination

- Task 15 adds safety guards to task 12's `run_cli.py` and task 13's `local_model.py`.
  The user reported a computer freeze. Changes cover limits and shutdown, not benchmark or prompt optimization.
  No Qwen or live browser benchmark runs occur during this repair. Preserve these guards in tasks 12 and 13.

- Task 11 owns `install.sh`, `zero-browser`, `scripts/run_cli.py`, `jev_ultrafast/local_policy.py`, and setup tests.
  It adds local dispatch to `model.py` and a read-only lock option to the downloader.
  It preserves task 00 files and the separate temporary single-task pilot.
  Tasks 01, 02, and 10 must reuse or reconcile the local CLI adapter before changing these interfaces.

- Two agents work this repo. Codex sessions previously used branch plus PR plus self-merge and kept
  contexts local. As of 12:25 PT the rules in `AGENT-RULES.md` and `AGENTS.md` apply to everyone. Commit to
  `main`, pull before push, contexts is committed.
- `scripts/decision_baselines.py` and the recorder are Codex's. Nobody deletes them in task 10.

## Log

- 2026-10-11 12:50 PT. Rescoped after the first live run. Tasks 12 and 13 written, 03/04/05/06/07/11 cut.
  Two agents only, Astra on 12, Sol on 13.

- 2026-10-11 12:44 PT. Task 11 shell retest passed. The installer and independently tested CLI goal both returned exit code 0. Evidence: `shell_retest` in the installation record.

- 2026-10-11 12:40 PT. Codex completed task 11. Installation and the simple CLI goal passed. Multi-step failures remain in the evidence.

- 2026-10-11 12:30 PT. Codex completed task 00 within its timebox. Evidence is linked in Done. Stopped after task 00.
- 2026-10-11 12:27 PT. Codex claimed task 00. Main matched origin before the claim.
- 2026-10-11. Added aggregate evidence for two human recordings. The second save completed without errors.
  The save fix is on main. Raw recordings remain private.

- 2026-10-11 12:25 PT. Reconciled local and remote histories. Folded `PROGRESS.md` into this file. Rewrote
  `AGENTS.md`. Contexts un-ignored and committed.
- 2026-10-11 12:13 PT. Codex merged PR #2 (scorer publication) and PR #3 (recorder).
- 2026-10-11 12:07 PT. Codex merged PR #1 (delivery rules).
- 2026-10-11 12:10 PT. Plan written, contexts folder created. No code work started.
