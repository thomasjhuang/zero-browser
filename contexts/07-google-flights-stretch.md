# 07 Google Flights stretch

Current status: Superseded by task 16. Use its goals, safety boundaries, and completion gates.

Priority P2. Timebox 45 min. Only after 06 passes twice. Whoever is free.

## Why

Same demo Browser Use shipped, now with zero hosted calls. Strong launch material if it works. Real pages
have far more candidates and autocomplete timing, so expect failures.

## Do

1. Copy `examples/flights.py` to `examples/flights_local.py`. Set `JEV_LOCAL=1`. Keep `verify()` as is.
2. Run once. Note where it fails. Candidate count per step is the first thing to check against 03.
3. One fix attempt. Likely the target stage needs chunking (01) or page text trimming.
4. Second run. If it fails, stop and write down the failure mode here. That is still a useful result.

## Verify

- `artifacts/flights-local/state.json` with `verification` block, pass or fail recorded as is.

## Don't

- Don't spend more than the timebox. Don't modify the policy for Flights specifically.
- Don't book or select a flight. `verify()` already guards this.

## Status 12:50 PT

Cut or superseded. See README ranking. 03/05/06/07 are replaced by the live bench loop in 12. 04 is absorbed into 13. 11 keeps run_cli.py and drops the installer.
