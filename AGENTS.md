# zero-browser

Read `contexts/AGENT-RULES.md` first, then `contexts/STATUS.md`, before any work. The `contexts/` folder is
committed and is the source of truth for plan, task ownership, and state. `contexts/PROJECT.md` has setup
and operation commands. Pull before reading.

Keep the loop small: page -> indexed elements -> operation + target -> execution.

- The input is one natural-language goal. Do not add site-specific plans or hardcoded field values.
- The decision model chooses an operation and a target for that operation. Consume only the selected
  operation's target. Targets must map to observed elements. The model never emits selectors or code.
- TYPE_TEXT invokes the text model. Cache a stale retry's value only while its entire helper input is identical.
- Never retry a browser mutation. Log execution before observing its result.
- Models run locally. Do not add hosted model calls. Keep .env ignored and credentials out of the repo.
- Verify actual final outcomes independently. A DONE choice is not proof of success.
- Keep README claims, raw evidence in `results/`, and `contexts/STATUS.md` consistent. No number without a file.

## Delivery

Commit to `main`. `git pull --rebase origin main` before every push. No PRs, no branches, no self-review
ceremony for this hackathon. Never force push.

Run `uv run --offline --frozen --extra local ruff check .` and
`BH_HOME=/private/tmp/zero-browser-tests uv run --offline --frozen --extra local pytest` before each commit.
They take seconds. Existing tests must keep passing. Add a test only when it is faster than checking by hand.

Before pushing, check `git status` and the diff for secrets, weights, `.venv`, `artifacts/`, and private
machine paths. Never publish API keys, tokens, or private traces.

Update `contexts/STATUS.md` and the task file when claiming, finishing, or stopping. See `AGENT-RULES.md`.
