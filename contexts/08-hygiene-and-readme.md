# 08 Hygiene and README

Priority P3. Timebox 20 min. Anyone, mostly at the end. First five minutes can happen at 0:00.

## At 0:00 (5 min)

1. Inspect the current Git state. Preserve existing edits and unpublished commits.
2. Keep non-private `contexts/` files tracked. Keep model weights and caches ignored.
3. Stage only the intended files and follow `AGENTS.md` for delivery.

## At 4:15 (15 min)

1. README. Add a "Local end-to-end" section. Commands to run `scripts/local_smoke.py`, the pass count from
   06, per-step latency, text helper latency. Numbers come from `results/local-e2e.json` only.
2. Update the "Browser scaffolding" paragraph. The adapter now exists. Say TYPE_TEXT is local too.
3. `AGENTS.md`. Replace the TypeSafe sentence with the local dispatch rule, `JEV_LOCAL=1` or missing keys.
4. `pyproject.toml`. Rename project to `zero-browser` only if nothing imports the dist name. Otherwise skip.
5. Record the completed work and follow the task branch and PR procedure in `AGENTS.md`.

## Don't

- Don't claim anything the JSON does not show. Don't rewrite the measurement section.
