# 19 Context and engineering roadmap

Owner: thesis chat. Status: completed locally. Publication pending. Scope: shared context only.

## Why

The shared queue mixes completed work, retired plans, and active experiments.
The next milestone needs explicit dependencies and outcome criteria.

## Do

- Reconcile the queue with committed evidence and current owner activity.
- Preserve active edits, file reservations, historical evidence, and publication holds.
- Define reliable local completion, multi-step MCP testing, and the native comparison as separate stages.
- Keep model reuse and concurrent inference behind measured prerequisites.

## Verify

Read the changed context and linked task files. Run required lint and tests before each commit.
Make sure that links resolve and that new plans grant no experiment or spending authority.

## Do not

Do not change runtime code, start inference, message other chats, or publish private traces.
Do not mark planned work complete or release another owner's files without evidence.

## Result

Reconciled the task queue and retained active owner reservations and historical evidence.
The sequence is task 16 local reliability, task 20 MCP outcomes, task 21 comparison, then conditional model reuse in task 22.
Removed stale operation commands and corrected the retired task 06 prerequisite.
No runtime code changed and no inference ran in this chat.

Links and the intended diff passed inspection. The isolated context-only candidate passed lint and all 118 tests.
The shared working tree passed tests but failed lint in another chat's unfinished runtime edit.
The candidate excluded that runtime edit. No independent review was required under the repository's hackathon delivery rule.
Publication remains pending because the shared checkout contains unfinished work and the earlier task 18 publication hold remains unresolved.
