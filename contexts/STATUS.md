# Project status

Updated 2026-10-11 12:25 PT. This is the single shared state file. Edit it on every claim, finish, or block.
Keep it short. Evidence lives in `results/` and is linked, never restated beyond one number.

## Where we are

Jev Ultrafast scaffolding imported. Local Qwen3-4B 4-bit scorer works offline on synthetic decisions.
The agent loop still calls TypeSafe for decisions and OpenRouter for field text. No local end-to-end browser
run exists. No work on tasks 00 through 10 has started. Plan and ranked tasks are in `README.md` here.

## In progress

(none)

## Open, in priority order

- 00-shared-local-model (P0, Lane A, do first)
- 10-trim-jev-scaffolding phase 1 (P0, Lane D, do first)
- 01-local-choose-adapter (P0, Lane A, after 00)
- 02-local-type-text (P0, Lane B, after 00)
- 05-real-fixtures (P1, Lane C)
- 06-end-to-end-fixture-run (P0, all, after 01 and 02)
- 03-label-scaling-eval (P1, Lane C, after 05)
- 04-scorer-latency (P2, Lane B, only if 01 reports slow)
- 10-trim-jev-scaffolding phase 2 (P0, Lane D, after 01 and 02)
- 07-google-flights-stretch (P2, after 06 passes twice)
- 09-fix-filter-miss (P3)
- 08-hygiene-and-readme (P3, final 15 min)

## Done

| Work | Outcome | Evidence |
| --- | --- | --- |
| Local scorer, pinned weights, offline rerun | 12/12 synthetic decisions, 48 forward passes, ~300ms warm | `results/decision-smoke.json`, `results/decision-smoke-rerun.json` |
| Quality cases | 35/36. One candidate order picks the wrong filter, repeats 4/4 in that order | `results/decision-quality.json`, `results/decision-quality-filter-rerun.json` |
| Synthetic comparison vs hosted CLIs | Qwen 47/48, Codex 48/48, Claude 48/48 on 12 cases x 4 orders. No browser execution | `results/decision-comparison.json`, `scripts/decision_baselines.py` |
| Human demo recorder | Source landed, isolated Chromium session starts, Google Flights loads. No capture saved yet | `scripts/record_demo.py`, `scripts/recorder/` |
| Repo on GitHub | Scaffolding, scorer, fixtures, results, recorder on `main`. PRs #1 to #3 merged | github.com/thomasjhuang/zero-browser |
| Contexts folder committed | Plan, tasks, rules, status shared across agents | this folder |

## Blocked

(none)

## Known limits

Synthetic decisions do not establish browser reliability. Restricted scores are uncalibrated. The 16GB
memory target is untested. The browser guard check passed only in an isolated headless Chrome profile; the
default profile lacked remote debugging. Jev's per-step timeout can be exceeded by a slow local call.

## Coordination

- Two agents work this repo. Codex sessions previously used branch plus PR plus self-merge and kept
  contexts local. As of 12:25 PT the rules in `AGENT-RULES.md` and `AGENTS.md` apply to everyone. Commit to
  `main`, pull before push, contexts is committed.
- `scripts/decision_baselines.py` and the recorder are Codex's. Nobody deletes them in task 10.

## Log

- 2026-10-11 12:25 PT. Reconciled local and remote histories. Folded `PROGRESS.md` into this file. Rewrote
  `AGENTS.md`. Contexts un-ignored and committed.
- 2026-10-11 12:13 PT. Codex merged PR #2 (scorer publication) and PR #3 (recorder).
- 2026-10-11 12:07 PT. Codex merged PR #1 (delivery rules).
- 2026-10-11 12:10 PT. Plan written, contexts folder created. No code work started.
