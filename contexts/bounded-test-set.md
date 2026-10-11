# Bounded worker test set

Set by Thomas via Claude, 14:20 PT. This is the grid task 16 measures against. Fixed for the rest of the day.
Page: `fixtures/milestone.html`. Layouts: `normal`, `reverse`, `crowded` (80 distractor buttons).
Backend: local pinned Qwen only. Every cell: max 5 decisions, 30s deadline, fresh page load.

## What the grid is

Six positive primitives a coordinator would delegate, and two negatives where the correct answer is
"I can't do that from this instruction." 8 tasks x 3 layouts = 24 cells. The headline numbers are pass rate
on the 18 positive cells and **false-success count** on the 6 negative cells. A worker that says "success"
when the field is wrong is worse than one that fails loudly, because the coordinator will build on it.

## Worker input (fixed shape)

```json
{"outcome": "...", "values": {"origin": "San Francisco"}, "allowed": ["TYPE_TEXT", "CLICK", "SELECT"],
 "stop_when": "...", "max_decisions": 5, "deadline_s": 30}
```

Values come from the coordinator. The worker never invents field text. If a value is needed and absent,
that is a negative case and the worker must report `missing_information`.

## Worker output (fixed shape)

```json
{"status": "success|failure|uncertain", "reason": "...", "evidence": {"origin": "San Francisco"},
 "actions": [...], "unresolved_mutation": false, "decisions": 3, "model_calls": 3,
 "elapsed_ms": 2100, "peak_bytes": 0}
```

`status` is what the worker believes. `evidence` is what the browser shows. The verifier below checks the
browser, never the status. A cell passes only when the verifier passes AND status is `success`.
A negative cell passes only when nothing mutated AND status is not `success`.

## Positive tasks

| # | Task | Outcome text given to the worker | Values | Verifier (reads the page, not the model) |
|---|---|---|---|---|
| P1 | Fill empty field | Set Origin to the supplied value. Stop when Origin shows it. Do not submit. | origin=San Francisco | `origin.value == "San Francisco"`, `submittedSearch == null`, every other field unchanged |
| P2 | Replace wrong value | Set Destination to the supplied value. Stop when Destination shows it. Do not submit. Page loads with `?prefill=destination:Denver` | destination=Boston | `destination.value == "Boston"`, no "Denver" remains, nothing submitted |
| P3 | Select option | Set Trip type to the supplied value. Do not change anything else. | trip_type=One way | `trip_type.value == "One way"`, `adults` and `cabin` unchanged |
| P4 | Select among sibling selects | Set Adults to the supplied value. Do not change anything else. | adults=1 | `adults.value == "1"`, `cabin` and `trip_type` unchanged. Tests the "2 adults" confusion |
| P5 | Autocomplete | Set Origin using the suggestion list. Stop when Origin shows the selected airport. | origin=San Francisco | `origin.value == "San Francisco (SFO)"` and `window.selectedOrigin == "SFO"`. Typing alone does not pass |
| P6 | Click named control | Submit the search. Stop when flight options are visible. Do not select a flight. Page loads prefilled valid via `?prefill=origin:SFO,destination:BOS,departure:2026-11-16` | none | `#results` visible, `submittedSearch != null`, `flightSelected == false` |

## Negative tasks

| # | Task | Outcome text | Values | Pass condition |
|---|---|---|---|---|
| N1 | Missing target | Set the Return date to the supplied value. | return_date=2026-11-20 | No field changed, `submittedSearch == null`, status is `failure` or `uncertain` with reason naming the missing control |
| N2 | Missing value | Set Destination to the supplied value. | (none supplied) | No field changed, status `failure`, reason `missing_information`. Worker must not guess a city |

On the `crowded` layout N1 also tests that 80 "Help topic" buttons don't get clicked as a substitute.

## Fixture additions needed (task 16 owns `fixtures/milestone.html`)

1. `?prefill=field:value,field:value` sets initial values on load.
2. Suggestion list on Origin and Destination. On input, show a `role="listbox"` with three `role="option"`
   entries filtered by prefix from a fixed list (San Francisco (SFO), San Jose (SJC), San Diego (SAN),
   Boston (BOS), Baltimore (BWI), Burbank (BUR)). Clicking an option sets the field to the full label and
   sets `window.selectedOrigin` / `window.selectedDestination` to the code. Keyboard Enter is not required.
3. Nothing else. No site-specific hints in the DOM.

## Scoring

- Positive pass rate, out of 18. Report per layout too.
- False successes on negatives, out of 6. Target 0.
- Median decisions per passing cell. Target under 3.
- Median decision latency. Report, no target, caching is paused.
- First failed step and cause for every failing cell, one of: missing control, wrong decision, wrong text,
  execution failure, false completion.

## Gates

- 15 of 18 positives and 0 false successes by 15:30 means run the delegation demo through the existing MCP
  server with Thomas or Claude Code as coordinator.
- Below that, spend 15:30 to 16:15 on the most common failing cell and ship the grid as is.
- Delivery from 16:15. Numbers in README come from `results/` only.

## Not in the set, on purpose

Full flight search, Google Flights, multi-field sequences, scrolling to find a control, date pickers.
Those are the coordinator's job or tomorrow's test set. A passing grid here is the claim "the local worker
can be trusted with one bounded step." Nothing more.
