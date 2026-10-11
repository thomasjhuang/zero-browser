# Rules for project agents

Use `contexts/` as the shared source for project state and task ownership.
Commit non-private context. Keep model weights and caches out of Git.
Follow the publication and testing rules in the root `AGENTS.md`.
Those rules take precedence over older task plans.

## Before work

1. Inspect the branch, status, worktrees, and active ownership.
2. Fetch `origin` to read the current remote state.
3. Preserve local edits and unpublished commits. Do not rebase a checkout with unrelated work.
4. Read `contexts/STATUS.md`, then `contexts/README.md`, and the applicable task file.
5. Claim the task in `STATUS.md` before changing files that it owns.
6. Use an isolated task branch from current `origin/main` for new work.

## During work

- Stay inside the task's file ownership in `contexts/README.md`.
- If another task owns a required file, record the coordination in `STATUS.md`.
- Respect the timebox. Record incomplete outcomes.
- Do not start Google Flights work until task `06` passes twice.
- Do not add site-specific rules or hardcoded values to the policy.
- Keep automated tests and code review deferred under `AGENTS.md`.

## Delivery

1. Record implemented work, measured outcomes, and remaining work in `PROGRESS.md`.
2. Update `STATUS.md` and the task file with evidence and remaining work.
3. Examine the intended files and commit history for secrets and sensitive information.
4. Commit only the intended files on the task branch.
5. Push the branch and open a PR under `AGENTS.md`.
6. Merge authorized changes through the PR. Follow normal protections and use an exact head guard.
7. Make sure that GitHub reports the PR as merged before you report completion.

## Exclusions

- Do not publish model weights, caches, credentials, environment files, or private recordings.
- Keep non-private context tracked in Git.
- Do not force push or rewrite shared history.
- Do not claim another agent's active task without a coordination note and a reason.
- Do not report a capability without evidence. Plans do not establish completion.
