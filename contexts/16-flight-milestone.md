# 16 Flight demonstration milestone

Priority P0. Owner Codex milestone chat. First stage: model-free preparation.

## Why

The user selected a dependable flight-search demonstration. Runtime safety precedes local inference.
The reported computer freeze has no established cause.

## Do

- Preserve task 15 safeguards and active ownership of tasks 12 and 13.
- Add a separate milestone runner, durable event records, fixed tasks, and independent outcome tests.
- Primary: San Francisco to Boston, November 16, 2026. Variations: November 17 and Seattle on November 16.
- Use one adult, economy, and one-way travel for every flight task. Stop with matching options visible.
- Permit navigation, scrolling, search fields, autocomplete, filters, and search submission.
- Stop for login, CAPTCHA, flight selection, booking, payment, messages, and account changes.
- Include a local multi-step task, crowded controls, and changed control order.
- Preserve failed and interrupted records. Measure total time, decision time, calls, and memory.
- Remove repeated prompt content before cache work. Coordinate changes to task 13 files.

## Verify

- Run model-free safety and outcome tests before inference.
- Prepare one short local run. Wait for user readiness before starting it.
- Obtain user observations about responsiveness and cancellation before longer runs.
- Test every requested requirement independently. DONE alone never establishes success.
- Seek three consecutive primary successes, then run both variations. Keep comparison conditions fixed.
- Follow the required lint, tests, commit, and push procedure. Keep evidence in results/.

## Do not

Do not load Qwen during preparation. Do not run concurrent benchmarks or hosted models.
Do not add site-specific decision rules, hardcoded field answers, or a separate Markdown report.

## Result

The fixed runner, durable records, outcome tests, and local layouts are ready.
Model-free delivery checks and scripted browser experiments passed. These are not agent-performance results.
Evidence: [preparation](../results/milestone-preparation.json).

One verifier error occurred before search submission. The correction passed the same test.
The live flight verifier and unfamiliar action labels remain untested. The freeze cause remains unknown.
Task 13 still owns prompt changes. No cache optimization was added to this milestone runner.

After the user gives readiness, run:

```bash
uv run --offline --frozen --extra local python scripts/milestone.py --task local_search --pilot --ready
```

The pilot cancels after ten seconds, permits two decisions, and has a twenty-second worker deadline.
Chrome startup has a separate twenty-second deadline. Cleanup adds time after cancellation.
Ask the user to observe pointer movement, application switching, scrolling, cancellation, and browser closure.
Obtain their observations before longer runs. No model run occurred during preparation.

Private event records remain in ignored `artifacts/milestone/`. Use `--report` to compare saved runs without inference.
Interrupted runs remain failures in comparisons. A code change resets the consecutive-success count.
