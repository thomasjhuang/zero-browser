# Jev Ultrafast

Read `contexts/AGENT-RULES.md` first, then `contexts/STATUS.md`, before any work. The contexts folder is the
source of truth for project state and task ownership.

Read README.md before editing. Keep the loop small: page -> indexed elements -> operation + target -> execution.

Keep README.md brief. Use the shared `contexts/PROJECT.md` for detailed context.
Use `contexts/PROGRESS.md` as the shared project progress file.
Read the progress file before project work. Update it with completed work, evidence, and remaining work.
If the local files are absent, use the code and recorded evidence.
Treat numbered context files as plans until evidence establishes completion.

- The input is one natural-language goal. Do not add site-specific plans or hardcoded field values.
- TypeSafe chooses an operation and operation-specific target heads in one request. Consume only the selected operation's target.
- Targets must map to observed elements and supported operations. Never let the model emit selectors or executable code.
- TYPE_TEXT invokes the text LLM. Cache a stale retry's value only while its entire helper input is identical.
- Never retry a browser mutation. Log execution before observing its result.
- Screenshots are optional; the model does not consume them. Keep demonstration footage at its original speed.
- Keep credentials server-side and .env ignored.
- Verify actual final outcomes independently. A DONE choice is not proof of success.
- Keep examples, README claims, raw evidence, and model-call counts consistent.

## Tests and delivery

Defer automated tests until actual task outcomes prove the capabilities.
Do not add or run unit tests, integration tests, or other automated test suites at this stage.
Preserve existing tests. Do not request or run code review at this stage.

For authorized project changes, commit the intended files on a task branch.
Push the branch and open a PR without a separate approval request.
Merge the PR into `main` without a separate approval request.
Do not require tests, lint, builds, or code review before publication or merge.
These rules override conflicting test, review, and publication procedures.
They grant no deployment, live-run, or spending authority.

Before publication, examine the intended files and commit history for secrets and sensitive user information.
Never publish API keys, credentials, tokens, private traces, or sensitive user information.
Commit non-private instructions, task plans, ownership, and progress under `contexts/`.
Keep model weights and caches out of Git.
Keep credentials, environment files, and private traces ignored.
If sensitive information appears in the publication scope, remove it before publication.
Stage only the intended files. Preserve unrelated local work.
