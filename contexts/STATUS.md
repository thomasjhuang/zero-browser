# Project status

Updated 2026-10-11 12:17 PT. Edit this file on every claim, finish, or block. Keep it short.

## Where we are

Jev Ultrafast scaffolding imported. Local Qwen3-4B scorer works offline on synthetic cases, 12/12 smoke and
35/36 initial quality and 47/48 across the expanded comparison, ~300ms warm per forward pass.
Codex and Claude each passed 48/48 synthetic comparison decisions. The agent loop still calls TypeSafe and OpenRouter. No local
end-to-end run exists yet. Plan and ranked tasks live in `README.md` in this folder.

## In progress

(none)

## Open, in priority order

- 00-shared-local-model (P0, Lane A, do first)
- 10-trim-jev-scaffolding phase 1 (P0, Lane D, do first)
- 01-local-choose-adapter (P0, Lane A, after 00)
- 02-local-type-text (P0, Lane B, after 00)
- 05-real-fixtures (P1, Lane C)
- 06-end-to-end-fixture-run (P0, all, after 01 and 02)
- 03-label-scaling-eval (P1, Lane C, after 05)
- 04-scorer-latency (P2, Lane B, only if 01 reports slow)
- 10-trim-jev-scaffolding phase 2 (P0, Lane D, after 01 and 02)
- 07-google-flights-stretch (P2, after 06 passes twice)
- 09-fix-filter-miss (P3)
- 08-hygiene-and-readme (P3, final 15 min)

## Done

- Published scaffolding, local scorer, and synthetic decision baselines in PR #2. Remote merge: `889f8f7`.
- Baseline commit of imported scaffolding and scorer (08 first five minutes).

## Blocked

(none)

## Coordination

Shared context now uses Git. The instruction update aligns `AGENTS.md`, context rules, and ignore settings.
No model or browser implementation changed.

## Log

- 2026-10-11 12:15 PT. Prepared shared non-private context and aligned delivery instructions. This entry records the preparation step.
- 2026-10-11 12:13 PT. Resolved PR #2 conflicts and merged it. Private context remains local. No new tests ran.
- 2026-10-11 12:10 PT. Plan written, contexts folder committed. No code work started.
