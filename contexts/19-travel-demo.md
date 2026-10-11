# 19 — isolated terminal travel demo

## Why

The user requested an end-to-end travel demonstration with a deterministic workflow, a verified terminal
shortlist, and an optional local model comparison. The fixed request is one-way SFO to BOS on 2026-11-16,
one adult in Economy, nonstop, under USD 400, arriving the same day before 18:00, up to five options.

## Do

- Work only in the separate `codex/travel-demo-scaffolding` worktree/branch. The user's authorization for
  this isolated scope supersedes older no-branch and no-site-specific-plan rules for this task only.
- Own new `travel_demo/` files. Preserve the main engine, shared model policy, browser runner, and guards.
- Reuse current observations and verified outcome checking. Never use model DONE as success evidence.
- Use the same observer/executor for deterministic fixture and future live experiments.
- Keep optional airline input as a strict restriction; blank means all airlines.
- Leave successful visible search results open for terminal-driven user review, outside the timed worker.
- Reuse existing single-run, memory, deadline, cancellation, and durable-journal facilities.
- Keep local inference opt-in and lazy inside the supervised worker. Do not run Qwen during preparation.
- Record the actual model-free browser preparation in `results/travel-demo-preparation.json` after checks.

## Verify

Run the existing required lint and test commands before local delivery. Parent integration owns the
model-free browser checks for normal, reordered, renamed, ambiguous, empty, and human-verification
fixtures. Check actual observed route/date/passenger/cabin fields, submitted URL, and row evidence.
Record honest fewer-than-five outcomes and reject overnight/late/over-budget/connecting flights.
Review and headless cleanup must preserve browser ownership. Frontier injection is an interface only;
no hosted comparison is implemented or measured.

## Don't

Do not modify main's engine or another active lane's files. Do not book, pay, log in, export, add hotels,
or publish private artifacts. Do not commit/push to main, push this branch, or start live Qwen inference
without the corresponding user authorization. Synthetic fares do not prove real availability or speed.

## Result

Preparation complete in the isolated branch. New CLI, semantic fixture, terminal formatter, outcome
checker, bounded session, and run documentation are present. The final source and all records are in
[the preparation evidence](../results/travel-demo-preparation.json).

All ten fixture expectations passed through the actual browser. These include reordered/renamed
controls, fresh passenger-popup proof with a scrolling header, empty results, strict and blank airline
restrictions, and protected stops for ambiguous controls and human verification.

The final headless Google observation verified three qualifying flights from twenty inspected rows;
six rows were unparsed and excluded. The final visible live attempt stopped at an unsupported transition
without a verified shortlist. Visible Google operation remains unreliable. Browser hold, target
presence, and Enter-to-close cleanup were verified on the synthetic fixture only.

Combined existing and focused checks passed: 276 tests, plus the required whole-repository lint.
No local Qwen inference, hosted inference, or three-way comparison was run in this preparation.
Interactive review is outside the worker's recorded time; no reliability or comparative-speed claim is
made. Publication remains unrequested. Follow-up is the visible Google transition and separately
authorized local/frontier adapters using the same request and outcome checker.
