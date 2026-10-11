# 17 Experiment priority

Current status: Implemented and present on origin/main. The publication note in the original result is historical.

Owner Codex. Scope: repository instructions only.

## Why

The user requested end-to-end experiments before broader unit-test coverage.

## Do

Prioritize experiments through the actual pipeline. Permit new unit tests only for critical safeguards or repeatable bugs.
Preserve existing tests, delivery checks, and experiment authorization requirements.

## Verify

Read the updated policy and its references. Run the required delivery checks. Add no unit tests for this instruction change.

## Do not

Do not change runtime code or another chat's unfinished work.

## Result

The local instructions now prioritize controlled end-to-end experiments.
New unit tests are limited to critical safeguards or repeatable bugs.
Existing tests, delivery checks, and experiment authorization requirements remain in effect.
The policy references and diff passed inspection. No unit tests were added.
Lint and the existing suite passed. No model inference ran.
Publication remains pending. The shared checkout contains unrelated unfinished changes that prevent the required pull.
