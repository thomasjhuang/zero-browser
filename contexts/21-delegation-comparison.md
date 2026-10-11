# 21 Direct browser and local delegation comparison

Status: planned, unassigned. Depends on task 20 and an available native browser environment.

## Why

The project needs evidence of saved human attention and reduced frontier involvement.
The earlier native CLI attempt supplied no browser tools and is not a baseline.

## Do

- Establish a working native Codex browser environment before timing a comparison.
- Compare direct Codex browser operation with Codex delegating to the local MCP worker.
- Use identical goals, starting states, completion criteria, and comparable browser access.
- Record model and application versions, permissions, source hashes, and timing boundaries.
- Repeat each task and alternate run order. Include failures, interruption, correction, and setup time.
- Measure human active time separately from elapsed time. Include a manual completion baseline.
- Record available frontier usage, local calls, and sampled memory. Mark missing usage as unavailable.
- Separate cold startup from warm execution where supported. Do not claim warm reuse that does not exist.

## Verify

Publish sanitized per-run evidence and the comparison, with at least three attempts per machine configuration.
Use the same independent outcome assessment for both arms. Report small-sample uncertainty and resource limits.
If delegation itself appears beneficial, propose a frontier-worker control before attributing the benefit specifically to local inference.

## Measurement rules

Keep manual desktop sessions and CLI sessions in separate comparisons. Use fresh conversations and browser state for repeated trials.
Use a monotonic timer. Record browser setup, application startup, handoff, outcome assessment, and cleanup as separate intervals.
Count failed and unverified attempts in the success-rate denominator.
Count cached input once. Do not add reasoning tokens twice or duplicate usage from action history.
Keep incomplete usage totals marked incomplete. Do not import a resumed conversation as a fresh run.
Separate provider-reported cost, dated price estimates, and subscription charges. Missing prices remain unavailable.

## Do not

Do not add hosted calls to the local worker, new spending, or providers without existing authority.
Do not omit failed runs or substitute a different task for an unavailable baseline.
Do not claim that fewer tokens necessarily mean less human time.
