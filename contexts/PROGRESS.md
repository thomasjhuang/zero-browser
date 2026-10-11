# Shared project progress

Updated: October 11, 2026.
This tracked file records non-private project work, evidence, and remaining work.
Store detailed instructions in [PROJECT.md](PROJECT.md).
The numbered context files describe plans. A plan does not establish completion or grant execution authority.
Update this file after project work. Link the evidence and distinguish implementation from measured outcomes.

## Current state

Some earlier evidence and browser-baseline tools exist only in the preserved local checkout.
Entries marked local-only are not part of the public repository.

| Work | Status | Evidence |
| --- | --- | --- |
| Local Qwen scorer and pinned weights | Implemented. The saved rerun passed 12 distinct prompts across 48 forward passes. | [Saved rerun](../results/decision-smoke-rerun.json). Earlier setup evidence: local-only `results/setup-checks.json`. |
| Broader decision quality tests | Measured. The quality gate remains unmet: 35/36 decisions passed. The focused rerun passed 12/16. | Earlier quality evidence: local-only `results/quality-checks.json`. See the published [decision comparison](../results/decision-comparison.json). |
| Codex, Claude, and Jev baseline tools | Implemented. The tools record time, outcomes, tokens, and cost for three shared browser tasks. | Local-only `scripts/baselines.py` and `fixtures/browser_baselines.json`. |
| Baseline tests and independent review | Passed: 64 offline tests, 21 browser guard tests, syntax tests, and package build. The reviewer approved the candidate. | Local-only `artifacts/baselines/setup.json`. |
| Live agent comparisons | Pending. The live Codex, Claude, and Jev command flows remain untested. No live performance results exist. | Local-only `artifacts/baselines/setup.json`. |
| Local browser execution | Pending. The scorer lacks a browser adapter. Jev still uses hosted decision and text models. | [Adapter plan](01-local-choose-adapter.md), [text-helper plan](02-local-type-text.md) |
| Tests and delivery policy | Implemented. Automated tests and code review are deferred. Authorized changes use a pushed branch and a PR, then merge into `main`. | [Project rules](../AGENTS.md) |
| README and local context cleanup | Implemented. The README retains setup and attribution. Detailed instructions and non-private progress are shared under `contexts/`. | [README](../README.md), [shared context](PROJECT.md) |

## Remaining work

- Connect the local scorer to observed browser actions.
- Generate field text locally.
- Run a complete local browser task with independent outcome evidence.
- Resolve the candidate-order error in the stock-filter case.
- Measure live agent comparisons after the user authorizes the runs and any spending.

## Measurement limits

Synthetic decisions do not establish browser-task reliability.
Restricted scores do not guarantee correctness. The stock-filter error repeated with a 95.2% score.
The 16 GB memory target remains untested.
The browser verifier passed tests in an isolated headless Chrome profile.
The default Chrome profile lacked remote debugging during the first guard test.
Jev tests its timeout between steps. A slow model call can exceed that deadline.
Provider transport retries are absent from Jev's trace.
GitNexus omits some call flows and untracked source from its change scan. Source review supplements those results.

## Work rules

The user now permits non-private context in Git. Earlier exclusion notes below record the previous policy.
Use the current `AGENTS.md` for publication rules. Keep weights and caches excluded.

Use this file as the shared status record. Add actual results after each task.
Preserve other sessions' updates. Record each test result as passed, failed, skipped, or unverified. Record pending tests separately.
Keep measurements and execution traces in their existing data files.
Do not put project progress or detailed context back into the public README.
Use the current tests and delivery rules in the primary checkout's `AGENTS.md`.
The test and review results above are historical evidence. They impose no publication gates.
No automated tests or code review ran for this policy change.
Published project rules and ignore settings in [PR #1](https://github.com/thomasjhuang/zero-browser/pull/1).
PR #1 merged into `main` on October 11, 2026.
Merge commit: `bbbf441fae84062683c7fb23ed9fd51ee989bc8b`.
The rule permits authorized pushes and merges without separate approval.
No tests or code review ran for the merge authorization change.
The publication scan found no secret patterns in the intended files or inherited files.
PR #1 contains no local context, progress, or private traces.
The primary checkout remains on `main` with separate unpublished commits.
At that time, an unpublished commit tracked context files despite the ignore rule. The previous policy excluded those files from publication.
Preserve those commits and local edits. Reconcile them separately before publishing other project work.


## Decision comparison and code publication

The preserved synthetic comparison passed 47/48 decisions for Qwen and 48/48 for both Codex and Claude.
The comparison uses 12 cases with four candidate orders. It does not execute browser actions.
The saved comparison is `results/decision-comparison.json`.

Published the baseline code on branch `codex/publish-local-baselines` in [PR #2](https://github.com/thomasjhuang/zero-browser/pull/2).
Commit: `7ace24b881b5863c0826da4d99d06c69851b00c5`. The PR remains open and unmerged.
The publication branch contains the scaffolding, local scorer, decision comparison, dependency locks, existing tests, and synthetic results.
It excludes weights, caches, local context, private records, and the separate browser-baseline files.
The publication copy removes private machine paths from Codex warning metadata. Original local measurements remain unchanged.
The public comparison updates the source hash for that sanitized record.

No automated tests, lint, build, or code review ran for this publication.
Earlier verification passed 75 tests in the shared checkout. The publication scan found no secret patterns or private paths.
The current scorer still needs a browser adapter. The 16 GB target and browser-task reliability remain untested.

The primary checkout remains on `main` at local commit `91cf2b2`.
That local commit includes `contexts/`. It was not pushed.
That delivery used a clean publication branch and excluded the local context commit.


Publication follow-up: PR #2 remains open at `7ace24b881b5863c0826da4d99d06c69851b00c5`.
Remote main advanced to `bbbf441` during publication through PR #1.
Automatic approval review rejected merging origin/main into the publication branch.
The rejection states that the user authorized a push, not a merge, and repository rules cannot expand that authority.
It also flags a risk of adding private context. The rejected operation did not run.
The clean branch stays published. An explicit user merge instruction is required before merge work resumes.

## Human demonstration recorder

The recorder source is on `codex/human-demo-recorder` at `e9a043f`. The process started in a separate Chromium session. Google Flights loaded. The first human capture and save remain pending. Private output stays under ignored `artifacts/baselines/demonstrations/`. Automated suites and independent review were skipped under the current project policy. GitNexus query and context ran. Index refresh failed on registry permissions, and change analysis did not cover the isolated worktree.


## Baseline PR merged

The user explicitly authorized conflict resolution and merging PR #2.
Resolved conflicts in `AGENTS.md` and `.gitignore` with the published rules from remote main.
The scorer code and measurement values remain unchanged.
Pushed the resolution as `68fd0681de1bcec4138557845b2d8f8acbb6beeb`.
[PR #2](https://github.com/thomasjhuang/zero-browser/pull/2) merged into remote `main` on October 11, 2026.
Merge commit: `889f8f7fbc26906a35faa02c19fdde5ab6a6f706`.
GitHub reports `MERGED`. The merge used the exact head guard and normal protections.
No tests, lint, build, or code review ran for conflict resolution or merging, as the project rules require.
The publication scan found no secret patterns or private paths.
The remote tree contains no context files, private artifacts, model weights, environments, or caches.

The primary checkout stays on local `main` at `2711c40` with its unpublished context commits and edits.
It cannot fast-forward to remote main without reconciling that separate history. No reset or rebase changed it.
The new sharing change uses a clean task branch and preserves that separate local history.
Updated: 2026-10-11 12:13 PT.


## Shared context policy

The user requested shared, non-private context in Git.
Updated `AGENTS.md`, `contexts/AGENT-RULES.md`, and the context entry files.
Removed the `contexts/` ignore rule. Model weights and caches remain excluded.
Existing credential, environment, and private recording exclusions remain in place.
Task plans remain proposals until recorded outcomes establish completion.
No automated tests, lint, build, or code review ran for this instruction change.
This entry records preparation for publication through the task branch and PR workflow.
