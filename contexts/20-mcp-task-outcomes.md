# 20 Multi-step MCP task outcomes

Status: planned, unassigned. Depends on repeated local completion in task 16 and the task 18 owner's handoff.

## Why

The MCP connection passes simple navigation. Delegation needs evidence that a complete task succeeded.
Text and URL fragments alone do not establish correct search submission.

## Do

- Reuse the fixed local task, starting state, and outcome tests from task 16.
- Let Codex supply one goal. Keep operation selection and field text inside the local worker.
- Return separate model completion, independently assessed outcome, and failure information.
- Return evidence for each requirement and known timing, model-call, and memory measurements.
- Assess completion outside the action policy. Keep expected answers out of its prompts.
- Keep per-request browser isolation and the single-run guard for this stage.

## Verify

Seek three consecutive complete runs through Codex and MCP, then test the task variations.
Disable native browser tools for the delegated arm. Save the actual tool call and sanitized results.
Exercise premature DONE and a busy worker. Neither case counts as success.
Run required lint and tests before each commit.

## Do not

Do not add a persistent worker, concurrency, site-specific policy, or a new coordinator provider.
Do not infer speed savings from successful delegation. This plan grants no new inference or spending authority.
