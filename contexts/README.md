# Engineering plan

Read [AGENT-RULES.md](AGENT-RULES.md), then [STATUS.md](STATUS.md).
[PROJECT.md](PROJECT.md) contains current commands. STATUS owns task state and reservations.
Numbered task files retain history. Historical instructions do not restart retired work.

## Direction

Test whether a frontier coordinator can delegate useful browser work to a local model with less human attention and frontier involvement.
Travel search is the demonstration. Speed, cost savings, and general reliability remain unproven.
The browser worker keeps inference local. The Codex coordinator is a separate component.

## Active engineering work

[Task 16](16-flight-milestone.md) is the only active engineering milestone.
Complete the fixed local task repeatedly. Test the layout variations before live flight search.
Task 13 supplies observation support through an explicit handoff.

Tasks 18–22 remain outside the active plan. Their files preserve earlier proposals and results.
Do not restart MCP work, a delegation comparison, model reuse, or a second benchmark implementation.
Concurrent inference and a swarm remain outside the current milestone.

## Immediate task 16 work

Use saved observations to diagnose skipped fields, early submission, and premature DONE.
Distinguish incorrect decisions from missing controls, field-text errors, and execution failures.
Treat repeated state cycles as a separate failure. Preserve bounded stops and never repeat an uncertain mutation.
Keep one change per experiment. Completion quality precedes cache optimization.

## Ownership

Use the [current ownership table](STATUS.md#current-ownership). STATUS is the only source for current file reservations and run access.
Follow the [exclusive run and handoff rules](AGENT-RULES.md#exclusive-runtime-and-benchmark-access).
Codex task 16 owns runtime integration and benchmark execution. Claude's observer changes require a handoff before further edits.
The context coordinator owns shared context files only during this reconciliation.
Do not infer ownership from historical task descriptions.

## Experiment and time limits

Keep goals, starting state, outcome tests, and source versions fixed within each comparison.
Record the first failed step. Change one cause at a time. Reset consecutive successes after code changes.
Preserve failures and interrupted runs. Follow [experimental validation](../AGENTS.md#experimental-validation).

Retain the October 11 hackathon cut lines: assess incomplete Qwen results at 14:30 PT, stop new features then, and finish by 16:00 PT.
If completion still fails at the cut, report the measured failure. Deferred work does not extend the timebox.
Plans grant no new experiment, publication, provider, or spending authority.
Follow the current run state and publication coordination in STATUS.
