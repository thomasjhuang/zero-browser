# Engineering plan

Read [AGENT-RULES.md](AGENT-RULES.md), then [STATUS.md](STATUS.md).
[PROJECT.md](PROJECT.md) contains current commands. STATUS owns task state and reservations.
Numbered task files retain history. Historical instructions do not restart retired work.

## Direction

Test whether a frontier coordinator can delegate useful browser work to a local model with less human attention and frontier involvement.
Travel search is the demonstration. Speed, cost savings, and general reliability remain unproven.
The browser worker keeps inference local. The Codex coordinator is a separate component.

## Engineering sequence

| Order | Task | Completion requirement |
| --- | --- | --- |
| 1 | [16 Reliable local and flight search](16-flight-milestone.md) | Complete the fixed local task repeatedly, then test variations before live flights |
| 2 | [20 Multi-step MCP outcomes](20-mcp-task-outcomes.md) | Codex delegates the same task and receives independent evidence for every requirement |
| 3 | [21 Delegation comparison](21-delegation-comparison.md) | Compare direct Codex with local delegation on identical tasks, including failures and human attention |
| 4 | [22 Model reuse](22-model-reuse.md) | Proceed only after startup measurements identify a useful improvement |

Task 13 retains its model and prompt reservation. Its latency work supports this sequence after coordination with task 16.
Do not run a second benchmark implementation from task 12. Task 16 supplies the current runner.
Task 08 updates public claims after measured results. Tasks 09 and 10 remain deferred.
Concurrent inference and a swarm remain outside the current milestone.

## Immediate task 16 work

Use saved observations to diagnose skipped fields, early submission, and premature DONE.
Distinguish incorrect decisions from missing controls, field-text errors, and execution failures.
Treat repeated state cycles as a separate failure. Preserve bounded stops and never repeat an uncertain mutation.
Keep one change per experiment. Completion quality precedes cache optimization.

## Ownership

| Reservation | Files and boundary |
| --- | --- |
| 16, milestone chat | `scripts/milestone*.py`, `fixtures/milestone*`, milestone evidence, and its recorded prompt experiments |
| 13, existing model owner | `local_policy.py`, `local_model.py`, `questions.py`, replay and scoring records |
| 12, legacy reservation | `scripts/run_cli.py` and previously assigned benchmark paths. Retain until the owner releases them |
| 18, MCP chat | `scripts/mcp_server.py`, `scripts/codex_mcp_smoke.py`, MCP dependencies and evidence |
| 19, thesis chat | Context reconciliation only. Preserve other owners' task-file edits |
| 20–22 | Unassigned. Obtain the affected owner's handoff before edits |

Preserve the executor, observer, dispatch contract, and recorder. Coordinate any necessary change before editing shared runtime files.
One inference job runs at a time. A busy lock is not a benchmark result.

## Experiment and time limits

Keep goals, starting state, outcome tests, and source versions fixed within each comparison.
Record the first failed step. Change one cause at a time. Reset consecutive successes after code changes.
Preserve failures and interrupted runs. Follow [experimental validation](../AGENTS.md#experimental-validation).

Retain the October 11 hackathon cut lines: assess incomplete Qwen results at 14:30 PT, stop new features then, and finish by 16:00 PT.
If completion still fails at the cut, report the measured failure. Later stages remain planned and do not extend the timebox.
Plans grant no new experiment, publication, provider, or spending authority.
Keep the existing publication hold in STATUS until resolved under the delivery procedure.
