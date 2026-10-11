# Rules for any agent working in this repo

Read this file first, every session, before touching code. The contexts folder is the source of truth for
project state. Chat history, memory, and your own assumptions are not.

## Before starting

1. `git pull --rebase origin main`. Other agents push to the same branch and update these files.
2. Read `contexts/STATUS.md`. It says what is done, what is in progress, who owns it, and what is blocked.
3. Read `contexts/README.md` for the plan, ranking, lanes, timeline, and cut lines. `contexts/PROJECT.md`
   has the setup and run commands.
4. Read the task file for the task you are taking. Each `contexts/NN-*.md` has Why, Do, Verify, Don't.
5. Claim the task. Edit `STATUS.md`, move the task to In progress with your lane or name, commit, push.
   If the push is rejected because someone else pushed first, pull, re-read STATUS.md, and check the task
   is still free before retrying.

## While working

- Prioritize end-to-end experiments. Follow [Experimental validation](../AGENTS.md#experimental-validation) for new unit tests.
- Stay inside the task's file ownership listed in `contexts/README.md`. If you must touch a file another
  lane owns, write a note in STATUS.md under Coordination and keep the change minimal.
- Respect the timebox. When it runs out, ship what passes and record what did not in the task file.
- Do not start Google Flights work until `06` passes twice. Do not add site-specific rules or hardcoded
  values to the policy.
- Run `uv run --offline --frozen --extra local ruff check .` and
  `BH_HOME=/private/tmp/zero-browser-tests uv run --offline --frozen --extra local pytest` before every commit.

## When finishing a task or stopping for any reason

1. Update the task file. Add a `## Result` section at the bottom with what landed, what did not, real
   numbers from `results/`, and any follow-up.
2. Update `STATUS.md`. Move the task to Done or back to Open with a note. Add one line to the Log with
   the time and a short summary.
3. Commit with a message that names the task number. Push to origin main.
4. If you discovered a new task, add `contexts/NN-name.md` using the same structure and a row in the
   README ranking table. Do not fold new work into an existing task's scope.

## Never

- Never push weights, `.venv`, `artifacts/`, or `.env`. `.gitignore` covers them. Check `git status` first.
- Never force push. Never rewrite history on main. No feature branches or PRs today. Commit to main.
- Never claim a task that STATUS.md shows as In progress by someone else without a Coordination note
  and a reason.
- Never state a result in README or STATUS that is not backed by a file in `results/`.
