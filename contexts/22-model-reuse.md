# 22 Reuse the local model between goals

Status: deferred, unassigned. Depends on tasks 20 and 21 and the task 13 owner's handoff.

## Why

Each MCP request starts a new model worker. Startup measurements must establish whether reuse warrants added lifecycle complexity.

## Do

- Separate model loading, browser startup, inference, and coordinator overhead in existing measurements.
- Proceed only if repeated goals show meaningful startup overhead and acceptable completion.
- Keep one model worker with bounded idle lifetime and serial inference.
- Preserve independent browser sessions unless the user separately requests session reuse.
- Keep cancellation, external deadlines, memory limits, and cleanup effective across requests.
- Make busy behavior explicit. Do not automatically repeat uncertain browser mutations.

## Verify

Compare cold and warm runs on the same completed task.
Assess repeated-request memory, cancellation, worker failure, and shutdown.
Keep completion quality at least as good as the measured baseline. Publish limitations and failed runs.

## Do not

Do not add a swarm, concurrent local inference, shared login sessions, or cache research to this task.
Do not proceed from an assumed speed benefit. Planning does not authorize new experiments or spending.
