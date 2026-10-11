# 06 End-to-end fixture run

Current status: Superseded by task 16. Its local completion gate replaces this historical task.

Priority P0. Timebox 60 min. Everyone joins once 01 and 02 land. This is the demo.

## Why

This is the whole point of the day. One goal, local model, fixture page, status done, verified independently.

## Do

1. Copy `scripts/smoke.py` to `scripts/local_smoke.py`. Remove `load_environment()`. Set `JEV_LOCAL=1`.
   Goal stays "Use the destination search and filters to find Design stays in Lisbon with Free cancellation,
   then open Casa Flora." Max actions 15.
2. Add independent verification at the end, same spirit as `examples/flights.py::verify`. Check the final
   page text contains "Casa Flora" as the opened place, category select reads Design, free cancellation
   checkbox is checked. Do not trust DONE.
3. Write `results/local-e2e.json`. Steps, each decision's operation and target probabilities, per-decision
   latency, text helper latency, total elapsed, verification result.
4. Run it. Watch the inspector at 127.0.0.1:8766 while it runs. When it picks wrong, look at the
   restricted scores before changing anything.
5. Fix loop. Most likely failures and the cheap fix for each.
   - Picks DONE early. Add "a visible result alone is not DONE" style sentence to the operation prompt.
   - Never picks TYPE_TEXT. Check the operation stage menu text describes TYPE_TEXT clearly.
   - Wrong target among many. Check 03 findings, reduce chunk size, or trim page text.
   - Text helper returns the whole goal. Tighten `TEXT_VALUE` with one example in the user message.
   - Repeated no-progress blocks. Compare `page_changed` in history, might be the 50ms settle wait.
6. Once it passes, run it three times. Record pass count honestly in the JSON and README.

## Verify

- Three runs, pass count recorded. Latency per step recorded.
- `pytest` and `ruff` still clean.

## Don't

- Don't add site-specific rules or hardcoded values to the policy. That violates AGENTS.md and the demo claim.
- Don't start Google Flights until this passes at least twice.

## Status 12:50 PT

Cut or superseded. See README ranking. 03/05/06/07 are replaced by the live bench loop in 12. 04 is absorbed into 13. 11 keeps run_cli.py and drops the installer.
