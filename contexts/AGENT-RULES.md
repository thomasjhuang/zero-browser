# Rules for any agent working in this repo

Read this file first, every session, before touching code. The contexts folder is the source of truth for
project state. Chat history, memory, and your own assumptions are not.

## Before starting

1. `git pull --rebase origin main`. Other agents push to the same branch and update these files.
2. Read `contexts/STATUS.md`. It says what is done, what is in progress, who owns it, and what is blocked.
3. Read `contexts/README.md` for the sequence, reservations, and time limits. `contexts/PROJECT.md`
   has the setup and run commands.
4. Read the current status banner and task file before taking work. Historical task bodies do not grant execution authority.
5. Claim the task. Edit `STATUS.md`, move the task to In progress with your lane or name, commit, push.
   If the push is rejected because someone else pushed first, pull, re-read STATUS.md, and check the task
   is still free before retrying.

## While working

- Prioritize end-to-end experiments. Follow [Experimental validation](../AGENTS.md#experimental-validation) for new unit tests.
- Until the flight demonstration works, defer broad unit-test expansion. Keep existing tests and required delivery checks.
  Add only small, deterministic tests for critical safeguards or repeatable bugs. Passing unit tests does not establish flight completion.
- Use the current ownership table in `contexts/STATUS.md`. Before editing another owner's files, obtain an explicit handoff.
  A coordination note alone does not transfer ownership.
- Respect the timebox. At its end, record completed and incomplete work. Follow publication holds and the delivery procedure.
- Before live Google Flights runs, require three consecutive independently successful local runs in task 16, then its local layout variations.
  Task 06 is historical. Preserve task 16 action boundaries. Do not add site-specific rules or hardcoded values to the policy.
- Run `uv run --offline --frozen --extra local ruff check .` and
  `BH_HOME=/private/tmp/zero-browser-tests uv run --offline --frozen --extra local pytest` before every commit.

## Exclusive runtime and benchmark access

1. Read the current run state in `STATUS.md` before each browser experiment or local model load.
2. Only the named run owner starts CLI goals, MCP goals, benchmarks, replay, cache probes, or browser-only experiments.
   This reservation does not reopen cut tasks. Preserve existing memory and worker limits.
3. Keep the existing single-run lock. If it is busy, wait for the owner to release it.
   Do not bypass the lock, change its directory, or stop another owner's process.
4. Before a measured run, record its command, source commit, dirty-file hashes, and evidence path in the task file.
   Use `ZB_RECORD_PATH=artifacts/replay/<run>.jsonl` for browser runs.
5. Freeze measured runtime files, prompts, fixtures, and environment configuration until the run ends.
   Do not edit another owner's files during the run, even without loading a model.
6. After the process ends, record the outcome and mark the slot idle.
   Preserve failed and interrupted evidence. A DONE choice does not establish completion.
7. Before transferring the slot, the current owner records the recipient and receives acknowledgment.
   Transfer file ownership separately with exact paths and the source commit.
8. If the owner is unavailable, keep the hold. Silence and an expired estimate do not transfer ownership.

Task 16 is the sole writer of shared run state after the current context update.
Other agents request ownership changes through that owner. They can continue read-only analysis without starting runtime work.
Serialize commits in the shared checkout. Stage only owned files and preserve all unrelated changes.
The current STATUS banner overrides historical task reservations and proposals for new tasks.

## When finishing a task or stopping for any reason

1. Update the task file. Add a `## Result` section at the bottom with what landed, what did not, real
   numbers from `results/`, and any follow-up.
2. Update `STATUS.md`. Move the task to Done or back to Open with a note. Add one line to the Log with
   the time and a short summary.
3. Commit with a message that names the task number. Push to origin main.
4. Follow the current scope in STATUS. During this milestone, record follow-up work in task 16 or task 13.
   Do not create new task numbers or restart cut tasks.

## Never

- Never push weights, `.venv`, `artifacts/`, or `.env`. `.gitignore` covers them. Check `git status` first.
- Never force push. Never rewrite history on main. No feature branches or PRs today. Commit to main.
- Never claim a task that STATUS.md shows as In progress by someone else without a Coordination note
  and a reason.
- Never state a result in README or STATUS that is not backed by a file in `results/`.
