# 03 Label scaling eval

Priority P1. Timebox 45 min. Lane C after 05. Informs 01.

## Why

Current fixtures have four candidates. The travel fixture and Google Flights have dozens. We need one quick
answer. How many numeric labels can the scorer handle before accuracy falls apart.

## Do

1. Build `fixtures/decision_scaling_cases.json` by hand or by script. Three cases, each at 8, 16, and 24
   candidates. Pad with plausible distractor elements from the real observations captured in 05.
2. Labels are numeric strings `1`..`N`. Confirm single-token and boundary checks pass in `make_prompt`.
   If any numeric label fails the boundary check, note it and fall back to letters for that count.
3. Run `scripts/decision_smoke.py --cases ... --repeats 0`. Rotations are already built in.
4. Write a six-line summary at the top of this file. Accuracy per candidate count, position bias if visible,
   and the recommended chunk size for 01.

## Verify

- `results/decision-scaling.json` exists and was produced by the unchanged scoring code.

## Don't

- Don't go past 24 candidates. Don't try alternative label schemes beyond letters and numbers.
- Don't spend time on calibration or score analysis. Only accuracy and position bias.

## Status 12:50 PT

Cut or superseded. See README ranking. 03/05/06/07 are replaced by the live bench loop in 12. 04 is absorbed into 13. 11 keeps run_cli.py and drops the installer.
